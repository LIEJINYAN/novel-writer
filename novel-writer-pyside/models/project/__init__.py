from .project_info import ProjectInfo
from .volume import Volume
from .chapter import Chapter
from .character import Character
from .character_state import CharacterState
from .character_appearance import ChapterAppearance
from .plot_node import PlotNode
from .foreshadowing import Foreshadowing
from .conflict import Conflict
from .relationship import Relationship
from .faction import Faction
from .faction_member import FactionMember
from .relationship_history import RelationshipHistory
from .timeline_event import TimelineEvent
from .validation_rule import ValidationRule
from .world_setting import WorldSetting
from .writing_method_config import WritingMethodConfig
from .writing_statistic import WritingStatistic

# Backward-compatible aliases（旧模型名 → 新模型名）
# plot_arcs → plot_nodes（通过 plot_type 区分）
PlotArc = PlotNode
# plot_foreshadows → foreshadowings
PlotForeshadow = Foreshadowing
# relationship_changes → relationship_history
RelationshipChange = RelationshipHistory

__all__ = [
    "ProjectInfo", "Volume", "Chapter", "Character",
    "CharacterState", "ChapterAppearance", "PlotNode",
    "Foreshadowing", "Conflict", "Relationship", "Faction",
    "FactionMember", "RelationshipHistory", "TimelineEvent",
    "ValidationRule", "WorldSetting", "WritingMethodConfig",
    "WritingStatistic",
    # Backward-compatible
    "PlotArc", "PlotForeshadow", "RelationshipChange",
]
