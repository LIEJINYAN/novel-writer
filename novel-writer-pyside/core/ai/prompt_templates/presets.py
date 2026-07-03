"""预设配置方案。"""
from core.ai.base import AIConfig

# 创作模式 - 高创造力
CREATIVE_CONFIG = AIConfig(
    temperature=0.9,
    max_tokens=8000,
)

# 编辑模式 - 中等创造力
EDITING_CONFIG = AIConfig(
    temperature=0.6,
    max_tokens=4000,
)

# 分析模式 - 低创造力，精确输出
ANALYSIS_CONFIG = AIConfig(
    temperature=0.3,
    max_tokens=6000,
)

# 对话生成 - 高创造力
DIALOGUE_CONFIG = AIConfig(
    temperature=1.0,
    max_tokens=3000,
)

# 大纲生成 - 中等创造力
OUTLINE_CONFIG = AIConfig(
    temperature=0.7,
    max_tokens=6000,
)

# 创作强化要求（额外的质量保障）
CREATIVE_ENHANCEMENT = """
**创作强化要求**（必须遵循）：
1. 情感表达：必须创造情感丰富的内容
2. 对话自然化：拒绝说明式对话，采用真实对话节奏
3. 场景生动化：要求至少3种感官体验
4. 冲突张力：制造戏剧张力（动作、微表情、环境烘托）
5. 节奏变化：长短句交替，快慢节奏切换
6. 反AI检测：
   - 30-50% 单句成段
   - 每段 50-100 字
   - 避免 AI 高频词
   - 具象化抽象表达
"""
