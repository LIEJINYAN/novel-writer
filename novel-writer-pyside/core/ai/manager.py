"""AI 管理器 - 提供商注册、配置管理、统一调用入口。"""
from typing import Optional, Generator
from .base import (
    BaseAIProvider, Message, AIConfig, AIResponse,
    AIProviderError,
)
from .providers.openai_provider import OpenAIProvider
from .providers.deepseek_provider import DeepSeekProvider
from .providers.ollama_provider import OllamaProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.gemini_provider import GeminiProvider
from .providers.tongyi_provider import TongyiProvider
from .providers.doubao_provider import DoubaoProvider
from utils.crypto import encrypt_api_key, decrypt_api_key, is_old_format


class AIManager:
    """AI 管理器单例。"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._providers: dict[str, BaseAIProvider] = {}
        self._active_provider_name: str | None = None
        # 提供商配置缓存（从数据库加载）
        self._configs: dict[str, dict] = {}
    
    def init(self):
        """初始化：注册默认提供商，从数据库加载配置。"""
        # 注册默认提供商
        self.register(OpenAIProvider())
        self.register(DeepSeekProvider())
        self.register(OllamaProvider())
        self.register(AnthropicProvider())
        self.register(GeminiProvider())
        self.register(TongyiProvider())
        self.register(DoubaoProvider())
        
        # 从数据库加载配置
        self.load_configs()
    
    def register(self, provider: BaseAIProvider):
        """注册提供商。"""
        self._providers[provider.name] = provider
    
    def get_provider(self, name: str) -> Optional[BaseAIProvider]:
        """获取提供商实例。"""
        return self._providers.get(name)
    
    def get_active_provider(self) -> Optional[BaseAIProvider]:
        """获取当前激活的提供商。"""
        if self._active_provider_name:
            return self._providers.get(self._active_provider_name)
        return None
    
    def set_active_provider(self, name: str):
        """设置激活提供商。"""
        if name not in self._providers:
            raise AIProviderError(f"未知的提供商: {name}")
        self._active_provider_name = name
    
    def list_providers(self) -> list[dict]:
        """返回所有提供商信息。"""
        result = []
        for name, provider in self._providers.items():
            config = self._configs.get(name, {})
            result.append({
                "name": provider.name,
                "display_name": provider.display_name,
                "default_api_base": provider.default_api_base,
                "default_models": provider.default_models,
                "is_configured": bool(config.get("api_key") or name == "ollama"),
                "is_active": name == self._active_provider_name,
                "api_base": config.get("api_base", provider.default_api_base),
                "model": config.get("model", ""),
                "temperature": config.get("temperature", 0.8),
                "max_tokens": config.get("max_tokens", 4096),
            })
        return result
    
    def save_config(self, name: str, api_key: str, api_base: str,
                    model: str, temperature: float, max_tokens: int):
        """保存提供商配置到数据库。"""
        from models import db_manager, AIProvider
        
        session = db_manager.get_session()
        try:
            # 查找已有记录
            provider = session.query(AIProvider).filter_by(provider_name=name).first()
            
            # 加密 API Key
            if api_key:
                # 有新 API Key，直接加密为新格式
                encrypted_key = encrypt_api_key(api_key)
            elif provider and provider.api_key_encrypted:
                # 编辑但不修改 key，保留原有加密值，检查是否需要迁移旧格式
                encrypted_key = provider.api_key_encrypted
                if is_old_format(encrypted_key):
                    try:
                        decrypted = decrypt_api_key(encrypted_key)
                        encrypted_key = encrypt_api_key(decrypted)  # 重新加密为新格式
                    except Exception:
                        pass  # 迁移失败，保留原值
            else:
                encrypted_key = ""
            
            if provider:
                # 更新
                provider.api_key_encrypted = encrypted_key
                provider.api_base = api_base
                provider.default_model = model
                provider.temperature = temperature
                provider.max_tokens = max_tokens
                provider.is_enabled = True
            else:
                # 新建
                provider = AIProvider(
                    provider_name=name,
                    display_name=self._providers[name].display_name if name in self._providers else name,
                    api_key_encrypted=encrypted_key,
                    api_base=api_base,
                    default_model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    is_enabled=True,
                )
                session.add(provider)
            
            session.commit()
            
            # 更新缓存
            self._configs[name] = {
                "api_key": api_key,
                "api_base": api_base,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # 如果还没有激活提供商，设为激活
            if self._active_provider_name is None:
                self._active_provider_name = name
                
        except Exception as e:
            session.rollback()
            raise AIProviderError(f"保存配置失败: {e}")
        finally:
            session.close()
    
    def load_configs(self):
        """从数据库加载所有配置。"""
        from models import db_manager, AIProvider
        
        session = db_manager.get_session()
        try:
            providers = session.query(AIProvider).filter_by(is_enabled=True).all()
            for p in providers:
                # 解密 API Key
                api_key = ""
                if p.api_key_encrypted:
                    try:
                        api_key = decrypt_api_key(p.api_key_encrypted)
                        # 如果是旧格式，自动迁移为新格式并保存
                        if is_old_format(p.api_key_encrypted):
                            try:
                                p.api_key_encrypted = encrypt_api_key(api_key)
                            except Exception:
                                pass  # 迁移失败不影响使用
                    except Exception:
                        api_key = ""
                
                self._configs[p.provider_name] = {
                    "api_key": api_key,
                    "api_base": p.api_base or "",
                    "model": p.default_model or "",
                    "temperature": p.temperature or 0.8,
                    "max_tokens": p.max_tokens or 4096,
                }
            
            # 设置第一个已配置的提供商为激活（如果没有激活的）
            if self._active_provider_name is None and self._configs:
                self._active_provider_name = next(iter(self._configs))
            
            session.commit()  # 持久化旧格式迁移等变更
        finally:
            session.close()
    
    def get_config(self, name: str) -> dict:
        """获取提供商配置。"""
        return self._configs.get(name, {})
    
    def chat(self, messages: list[Message], config: AIConfig = None) -> AIResponse:
        """通过激活的提供商调用。"""
        provider = self.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商，请先在设置中配置")
        
        if config is None:
            config = self._create_config_from_active()
        
        return provider.chat(messages, config)
    
    def chat_stream(self, messages: list[Message], config: AIConfig = None) -> Generator[str, None, None]:
        """通过激活的提供商流式调用。"""
        provider = self.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商，请先在设置中配置")
        
        if config is None:
            config = self._create_config_from_active()
        
        yield from provider.chat_stream(messages, config)
    
    def _create_config_from_active(self) -> AIConfig:
        """从激活提供商的缓存配置创建 AIConfig。"""
        config_dict = self._configs.get(self._active_provider_name, {})
        
        # 尝试从 Vault 获取加密的 API Key
        api_key = config_dict.get("api_key", "")
        provider_name = self._active_provider_name
        if provider_name:
            try:
                from core.security.vault import vault as credential_vault
                if credential_vault.has_api_key(provider_name):
                    api_key = credential_vault.get_api_key(provider_name)
            except Exception:
                pass  # Vault 不可用时优雅退化到明文
        
        return AIConfig(
            model=config_dict.get("model", ""),
            temperature=config_dict.get("temperature", 0.8),
            max_tokens=config_dict.get("max_tokens", 4096),
            api_key=api_key,
            api_base=config_dict.get("api_base", ""),
            stream=True,
        )


# 全局单例
ai_manager = AIManager()
