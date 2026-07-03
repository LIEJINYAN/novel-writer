"""写作方法论 - 方法定义与运行时实现。"""
from .base import WritingMethod, MethodStage
from .three_act import ThreeActMethod
from .hero_journey import HeroJourneyMethod
from .seven_point import SevenPointMethod
from .story_circle import StoryCircleMethod
from .pixar_formula import PixarFormulaMethod
from .snowflake import SnowflakeMethod
from .advisor import MethodAdvisor, Recommendation, method_advisor
from .converter import MethodConverter, method_converter
from .registry import PlotNode, WritingMethodDef, get_method, list_methods, list_method_choices, METHOD_REGISTRY

__all__ = [
    "WritingMethod", "MethodStage",
    "ThreeActMethod", "HeroJourneyMethod", "SevenPointMethod",
    "StoryCircleMethod", "PixarFormulaMethod", "SnowflakeMethod",
    "MethodAdvisor", "Recommendation", "method_advisor",
    "MethodConverter", "method_converter",
    "PlotNode", "WritingMethodDef", "get_method", "list_methods", "list_method_choices", "METHOD_REGISTRY",
]
