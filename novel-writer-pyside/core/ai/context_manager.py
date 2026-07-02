"""AI 上下文管理器 - 整合 Token 计数、上下文构建与裁剪。"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AIContextManager:
    """AI 上下文管理器。"""

    def __init__(self):
        from core.ai.context.token_counter import token_counter
        from core.ai.context.context_builder import context_builder
        from core.ai.context.context_pruner import context_pruner
        self._counter = token_counter
        self._builder = context_builder
        self._pruner = context_pruner
    
    @property
    def counter(self):
        return self._counter
    
    @property
    def builder(self):
        return self._builder
    
    @property
    def pruner(self):
        return self._pruner
    
    def get_chapter_context(self, chapter_id: int, project_id: int,
                           max_tokens: Optional[int] = None,
                           model: str = "gpt-4") -> str:
        """一键获取裁剪后的章节上下文。
        
        Args:
            chapter_id: 章节 ID
            project_id: 项目 ID
            max_tokens: 最大 token 数（不指定则使用模型默认限制的 80%）
            model: 模型名称
        Returns:
            str: 裁剪后的上下文
        """
        # 1. 构建原始上下文
        context = self._builder.build_chapter_context(chapter_id, project_id)
        
        # 2. 如果没有指定 max_tokens，使用模型最大上下文的 80%
        if max_tokens is None:
            max_tokens = int(self._counter.get_model_max_tokens(model) * 0.8)
        
        # 3. 上下文裁剪，高优先级保留章节内容和角色列表
        context = self._pruner.prune(
            context, max_tokens, model,
            priority_sections=["【项目信息】", "【角色列表】", "【当前章节】", "【章节内容】"]
        )
        
        return context
    
    def get_analysis_context(self, chapter_id: int, project_id: int,
                            max_tokens: Optional[int] = None,
                            model: str = "gpt-4") -> str:
        """获取分析专用上下文。"""
        context = self._builder.build_analysis_context(chapter_id, project_id)
        
        if max_tokens is None:
            max_tokens = int(self._counter.get_model_max_tokens(model) * 0.8)
        
        context = self._pruner.prune(
            context, max_tokens, model,
            priority_sections=["章节内容"]
        )
        
        return context
    
    def get_chat_context(self, messages: list, max_tokens: Optional[int] = None,
                        model: str = "gpt-4") -> list:
        """裁剪聊天历史。"""
        if max_tokens is None:
            max_tokens = int(self._counter.get_model_max_tokens(model) * 0.5)
        
        return self._pruner.prune_messages(messages, max_tokens, model)
    
    def estimate(self, context: str, model: str = "gpt-4") -> dict:
        """估算上下文窗口使用情况。"""
        return self._pruner.estimate_window(context, model)
    
    def count(self, text: str, model: str = "gpt-4") -> int:
        """快速计算 token 数。"""
        return self._counter.count(text, model)


# 全局实例
ai_context = AIContextManager()
