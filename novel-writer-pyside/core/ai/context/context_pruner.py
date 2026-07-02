"""上下文裁剪器 - 按优先级/Token 限制裁剪上下文。"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ContextPruner:
    """上下文裁剪器。"""

    # 优先级标签
    PRIORITY_HIGH = 0
    PRIORITY_MEDIUM = 1
    PRIORITY_LOW = 2

    def __init__(self):
        # 延迟导入避免循环依赖
        self._token_counter = None
    
    def _get_counter(self):
        if self._token_counter is None:
            from core.ai.context.token_counter import token_counter
            self._token_counter = token_counter
        return self._token_counter
    
    def prune(self, context: str, max_tokens: int, model: str = "gpt-4",
              priority_sections: Optional[list[str]] = None) -> str:
        """按 Token 限制裁剪上下文。
        
        Args:
            context: 原始上下文文本
            max_tokens: 最大允许 token 数
            model: 模型名称
            priority_sections: 高优先级节点头部（如 ["【角色列表】", "【章节内容】"]）
        Returns:
            str: 裁剪后的上下文
        """
        counter = self._get_counter()
        current_tokens = counter.count(context, model)
        
        if current_tokens <= max_tokens:
            return context
        
        # 按段落拆分
        paragraphs = context.split("\n")
        token_counts = []
        for p in paragraphs:
            token_counts.append(counter.count(p, model))
        
        # 如果指定了优先级部分，优先保留
        high_priority_indices = set()
        if priority_sections:
            for i, p in enumerate(paragraphs):
                for section_header in priority_sections:
                    if p.strip().startswith(section_header):
                        # 保留该段及其后的内容直到下一个优先级标签或空行
                        j = i
                        while j < len(paragraphs):
                            is_next_header = any(
                                paragraphs[j].strip().startswith(h) 
                                for h in priority_sections
                            ) and j > i
                            if is_next_header:
                                break
                            high_priority_indices.add(j)
                            j += 1
        
        # 计算高优先级 token 数
        high_priority_tokens = sum(
            token_counts[i] for i in high_priority_indices
        )
        
        # 如果高优先级部分已经超过限制，需要进一步裁剪高优先级内容
        if high_priority_tokens > max_tokens:
            # 只保留高优先级部分，然后继续裁剪
            filtered_paragraphs = [
                p for i, p in enumerate(paragraphs) 
                if i in high_priority_indices
            ]
            return self._prune_by_length(filtered_paragraphs, max_tokens, counter, model)
        
        # 低优先级内容可用的 token 配额
        remaining = max_tokens - sum(
            token_counts[i] for i in high_priority_indices
        )
        
        # 收集低优先级段落及其 token
        low_priority = [
            (i, p, token_counts[i])
            for i, p in enumerate(paragraphs)
            if i not in high_priority_indices and p.strip()
        ]
        
        # 按 token 数从小到大排序（优先保留较短的段落）
        low_priority.sort(key=lambda x: x[2])
        
        # 从最小的开始，尽量保留更多段落
        kept_low = []
        low_total = 0
        for i, p, tc in low_priority:
            if low_total + tc <= remaining:
                kept_low.append((i, p))
                low_total += tc
        
        # 重建上下文
        result_paragraphs = []
        seen_indices = set(high_priority_indices)
        seen_indices.update(i for i, _ in kept_low)
        
        for i, p in enumerate(paragraphs):
            if i in seen_indices:
                result_paragraphs.append(p)
        
        result = "\n".join(result_paragraphs)
        logger.info(
            f"上下文裁剪: {current_tokens} → {counter.count(result, model)} token "
            f"(限制 {max_tokens})"
        )
        return result
    
    def _prune_by_length(self, paragraphs: list[str], max_tokens: int,
                         counter, model: str) -> str:
        """当高优先级内容也超限时，从最长的段落开始裁剪。"""
        # 保留第一个和最后一个段落（通常是标签/标题和最新内容）
        if len(paragraphs) <= 2:
            # 非常少的内容，直接截断字符
            result = ""
            for p in paragraphs:
                next_tokens = counter.count(result + "\n" + p, model)
                if next_tokens <= max_tokens:
                    result += "\n" + p if result else p
                else:
                    break
            return result
        
        first = paragraphs[0]
        last = paragraphs[-1]
        middle = paragraphs[1:-1]
        
        # 计算首尾 token
        first_tokens = counter.count(first, model)
        last_tokens = counter.count(last, model)
        
        if first_tokens + last_tokens > max_tokens:
            # 极端情况：连首尾都超限，截断首段
            ratio = max_tokens / (first_tokens + last_tokens)
            first = first[:int(len(first) * ratio)]
            last = ""
        
        middle_remaining = max_tokens - counter.count(first, model) - counter.count(last, model)
        
        if middle_remaining <= 0:
            return first + ("\n" + last if last else "")
        
        # 从中间段落的中部开始删除，保留首尾
        middle_text = "\n".join(middle)
        middle_tokens = counter.count(middle_text, model)
        if middle_tokens <= middle_remaining:
            return first + "\n" + middle_text + "\n" + last
        
        # 滑动窗口保留中间的核心部分
        middle_len = len(middle_text)
        target_chars = int(middle_len * (middle_remaining / middle_tokens))
        
        if target_chars >= middle_len // 2:
            # 保留开头和结尾部分（滑动窗口）
            half = target_chars // 2
            new_middle = middle_text[:half].rstrip() + "\n...\n" + middle_text[-half:].lstrip()
        else:
            # 只保留开头部分
            new_middle = middle_text[:target_chars].rstrip()
        
        return first + "\n" + new_middle + ("\n" + last if last else "")
    
    def prune_messages(self, messages: list, max_tokens: int,
                       model: str = "gpt-4") -> list:
        """裁剪消息列表（保留 system 消息，丢弃最早的对话历史）。
        
        Args:
            messages: Message 对象列表
            max_tokens: 最大允许 token 数
            model: 模型名称
        Returns:
            list: 裁剪后的消息列表
        """
        if not messages:
            return messages
        
        counter = self._get_counter()
        
        # 分离 system 消息
        system_msgs = []
        other_msgs = []
        for msg in messages:
            role = msg.role if hasattr(msg, 'role') else msg.get('role', '')
            if role == 'system':
                system_msgs.append(msg)
            else:
                other_msgs.append(msg)
        
        # 计算 system 消息 token 数
        system_tokens = counter.count_messages(system_msgs, model)
        
        if system_tokens > max_tokens:
            # 极端情况：system 消息自身超限，返回空列表
            logger.warning("System 消息已超过 Token 限制")
            return system_msgs
        
        remaining = max_tokens - system_tokens
        
        # 从最新的消息开始保留
        result = list(other_msgs)  # 先全部保留
        while len(result) > 1:
            tokens = counter.count_messages(system_msgs + result, model)
            if tokens <= max_tokens:
                break
            # 丢弃最早的非 system 消息
            result.pop(0)
        
        return system_msgs + result

    def estimate_window(self, context: str, model: str = "gpt-4") -> dict:
        """估算上下文窗口使用情况。
        
        Args:
            context: 上下文文本
            model: 模型名称
        Returns:
            dict: {total_tokens, max_tokens, usage_pct, is_exceeded}
        """
        counter = self._get_counter()
        total = counter.count(context, model)
        max_tokens = counter.get_model_max_tokens(model)
        return {
            "total_tokens": total,
            "max_tokens": max_tokens,
            "usage_pct": round(total / max_tokens * 100, 1) if max_tokens > 0 else 0,
            "is_exceeded": total > max_tokens,
        }


# 全局实例
context_pruner = ContextPruner()
