"""AI 写作服务。"""
from typing import Optional
from .base import Message, AIConfig, AIProviderError
from .manager import ai_manager
from .ai_worker import AIWorker
from .prompts.registry import get_template


class WritingAIService:
    """AI 写作服务，封装续写逻辑。"""

    def __init__(self):
        self._worker: Optional[AIWorker] = None

    def continue_write(self, chapter_id: int, project_id: int, max_tokens: int = 2000) -> AIWorker:
        """触发 AI 续写。

        Args:
            chapter_id: 当前章节 ID
            project_id: 当前项目 ID
            max_tokens: 最大生成字数（默认 2000）

        Returns:
            AIWorker 实例，调用者连接信号后启动线程

        Raises:
            AIProviderError: 未配置 AI 提供商
        """
        # 检查是否有激活的提供商
        provider = ai_manager.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商，请先在设置中配置")

        # 加载章节和项目数据
        from models import db_manager, Chapter, Project
        session = db_manager.get_session()
        try:
            chapter = session.query(Chapter).filter_by(id=chapter_id).first()
            project = session.query(Project).filter_by(id=project_id).first()

            if not chapter:
                raise AIProviderError("找不到章节")

            # 构建模板上下文
            # 加载前 3 章内容作为上下文
            prev_chapters = session.query(Chapter)\
                .filter(Chapter.project_id == project_id, Chapter.id < chapter_id)\
                .order_by(Chapter.id.desc())\
                .limit(3)\
                .all()
            prev_chapters.reverse()  # 按正序排列
            prev_content = ""
            for ch in prev_chapters:
                prev_content += f"【第 {ch.order or ch.id} 章 {ch.title or ''}】\n{ch.content or ''}\n\n"

            context = {
                "title": chapter.title or "",
                "content": chapter.content or "",
                "previous_chapters": prev_content,
                "genre": project.genre if project else "",
                "writing_method": project.writing_method if project else "",
                "word_count": chapter.word_count or 0,
            }
        finally:
            session.close()

        # 获取续写模板并渲染
        template = get_template("continue_write")
        if template is None:
            raise AIProviderError("找不到续写模板")

        message_dicts = template.render(context)
        # 转换 dict 为 Message 对象
        messages = [Message(role=m["role"], content=m["content"]) for m in message_dicts]

        # 获取配置
        config = ai_manager._create_config_from_active()
        config.stream = True
        config.max_tokens = max_tokens

        # 创建 Worker
        self._worker = AIWorker(messages, config)
        return self._worker

    def cancel(self):
        """取消当前生成。"""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()

    @property
    def is_running(self) -> bool:
        """是否正在生成。"""
        return self._worker is not None and self._worker.isRunning()


# 全局实例
writing_service = WritingAIService()
