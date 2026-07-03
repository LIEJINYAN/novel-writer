class AIAuditService:
    """AI 内容审计服务"""

    BANNED_WORDS = [
        "弥漫着", "唯一的", "直到", "不禁", "顿时",
        "摇摇欲坠", "空气凝固", "话音未落", "猛地",
        "宛如", "仿佛", "犹如", "心中暗想",
    ]

    def audit_text(self, text: str) -> dict:
        """审计文本的AI痕迹。返回:
        {
            "total_issues": int,
            "issues": [
                {
                    "type": "banned_word" | "long_paragraph" | "low_single_sentence_ratio",
                    "word": str | None,          # 仅 banned_word 类型
                    "paragraph": int | None,      # 仅 long_paragraph 类型
                    "char_count": int | None,     # 仅 long_paragraph 类型
                    "ratio": str | None,          # 仅 low_single_sentence_ratio 类型
                    "severity": "high" | "medium",
                    "suggestion": str,
                }
            ],
            "ai_score": float,  # 0.0 到 1.0
        }
        """
        issues = []

        # 1. 检查AI高频词
        for word in self.BANNED_WORDS:
            if word in text:
                issues.append({
                    "type": "banned_word",
                    "word": word,
                    "severity": "high",
                    "suggestion": "替换为更具体的表达",
                })

        # 2. 检查段落长度
        paragraphs = text.split("\n\n")
        for i, para in enumerate(paragraphs):
            char_count = len(para.strip())
            if char_count > 150:
                issues.append({
                    "type": "long_paragraph",
                    "paragraph": i + 1,
                    "char_count": char_count,
                    "severity": "medium",
                    "suggestion": f"段落 {i+1} 过长（{char_count}字），建议拆分为50-100字短段",
                })

        # 3. 检查单句成段比例
        single_sentence_paras = sum(1 for p in paragraphs if p.count("。") <= 1)
        ratio = single_sentence_paras / len(paragraphs) if paragraphs else 0
        if ratio < 0.3:
            issues.append({
                "type": "low_single_sentence_ratio",
                "ratio": f"{ratio:.0%}",
                "severity": "medium",
                "suggestion": f"单句成段比例仅 {ratio:.0%}，建议提升到 30-50%",
            })

        # 计算 AI 分数
        ai_score = self._calculate_ai_score(issues, len(text))

        return {
            "total_issues": len(issues),
            "issues": issues,
            "ai_score": ai_score,
        }

    def _calculate_ai_score(self, issues: list, text_length: int) -> float:
        """根据 issue 数量和文本长度计算 AI 痕迹分数 (0-1)。"""
        if text_length == 0:
            return 0.0
        # 基础分数来自 issue 密度
        base_score = min(1.0, len(issues) / max(1, text_length / 100))
        # 严重问题加权
        high_count = sum(1 for i in issues if i.get("severity") == "high")
        base_score += high_count * 0.1
        return min(1.0, base_score)


# 全局实例
audit_service = AIAuditService()
