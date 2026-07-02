"""AI 对话服务 - 会话管理、历史管理、上下文裁剪、持久化。"""

import uuid
import time
import os
import json
import logging
from dataclasses import dataclass, field
from typing import Optional, Generator

from core.ai.base import Message
from core.ai.manager import ai_manager

logger = logging.getLogger(__name__)

SAVE_DIR = os.path.expanduser("~/.novel-writer/chat_history")
MAX_SESSIONS = 20


@dataclass
class SessionData:
    """会话数据。"""
    session_id: str
    messages: list[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    max_history: int = 20
    system_prompt: str = "你是一位专业的写作助手。请根据用户的问题提供有帮助的回复。"


def _ensure_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def _session_path(session_id: str) -> str:
    return os.path.join(SAVE_DIR, f"{session_id}.json")


def _messages_to_dicts(messages: list[Message]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in messages]


def _dicts_to_messages(dicts: list[dict]) -> list[Message]:
    return [Message(role=d["role"], content=d["content"]) for d in dicts]


class ChatService:
    """AI 对话服务。"""

    def __init__(self):
        self._sessions: dict[str, SessionData] = {}
        _ensure_dir()
        self._load_sessions()

    def _load_sessions(self):
        """从文件加载会话列表。"""
        if not os.path.isdir(SAVE_DIR):
            return
        for fname in sorted(os.listdir(SAVE_DIR), key=lambda f: os.path.getmtime(os.path.join(SAVE_DIR, f)), reverse=True):
            if fname.endswith(".json"):
                session_id = fname[:-5]
                filepath = _session_path(session_id)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        messages = _dicts_to_messages(data)
                        self._sessions[session_id] = SessionData(
                            session_id=session_id,
                            messages=messages,
                            created_at=os.path.getmtime(filepath),
                        )
                except Exception as e:
                    logger.warning(f"加载会话文件失败 {filepath}: {e}")
        logger.info(f"从磁盘加载了 {len(self._sessions)} 个会话")

    def _save_session(self, session_id: str):
        """保存会话到文件。"""
        session = self._sessions.get(session_id)
        if not session:
            return
        _ensure_dir()
        filepath = _session_path(session_id)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(_messages_to_dicts(session.messages), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存会话失败 {session_id}: {e}")

    def _cleanup_old_sessions(self):
        """清理最旧的会话（超出 MAX_SESSIONS）。"""
        sessions = sorted(self._sessions.items(), key=lambda x: x[1].created_at)
        while len(sessions) > MAX_SESSIONS:
            sid, _ = sessions.pop(0)
            self.delete_session(sid)

    def create_session(self, system_prompt: str = "") -> str:
        """创建新会话。"""
        session_id = uuid.uuid4().hex[:12]
        self._sessions[session_id] = SessionData(
            session_id=session_id,
            system_prompt=system_prompt or "你是一位专业的写作助手。请根据用户的问题提供有帮助的回复。",
        )
        _ensure_dir()
        # 写入空文件
        filepath = _session_path(session_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([], f)
        logger.info(f"创建会话: {session_id}")
        self._cleanup_old_sessions()
        return session_id

    def send_message(self, session_id: str, content: str) -> Generator[str, None, None]:
        """发送消息并获取流式回复。"""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        session.messages.append(Message(role="user", content=content))

        messages = [Message(role="system", content=session.system_prompt)]
        messages.extend(session.messages)

        session_max_messages = session.max_history * 2 + 1
        if len(messages) > session_max_messages:
            messages = [messages[0]] + messages[-(session_max_messages):]

        full_response = ""
        try:
            config = ai_manager._create_config_from_active()
            provider = config.provider
            for chunk in provider.chat_stream(messages, config):
                full_response += chunk
                yield chunk

            session.messages.append(Message(role="assistant", content=full_response))
            # 回复完成后持久化
            self._save_session(session_id)
        except Exception as e:
            error_msg = f"AI 回复出错: {e}"
            logger.error(error_msg)
            yield error_msg

    def get_history(self, session_id: str) -> list[Message]:
        """获取会话历史。"""
        session = self._sessions.get(session_id)
        if not session:
            return []
        return list(session.messages)

    def clear_history(self, session_id: str):
        """清空会话历史。"""
        session = self._sessions.get(session_id)
        if session:
            session.messages.clear()
            self._save_session(session_id)

    def delete_session(self, session_id: str):
        """删除会话。"""
        self._sessions.pop(session_id, None)
        filepath = _session_path(session_id)
        if os.path.exists(filepath):
            os.remove(filepath)
        logger.info(f"删除会话: {session_id}")

    def list_sessions(self) -> list[str]:
        """列出活跃会话。"""
        return list(self._sessions.keys())

    def get_session_preview(self, session_id: str, max_len: int = 50) -> str:
        """获取会话预览文本（最近一条用户消息）。"""
        history = self.get_history(session_id)
        for msg in reversed(history):
            if msg.role == "user":
                text = msg.content[:max_len]
                return text + ("..." if len(msg.content) > max_len else "")
        return "空对话"


# 全局实例
chat_service = ChatService()
