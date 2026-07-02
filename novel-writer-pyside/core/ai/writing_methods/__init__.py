"""写作方法模块。"""
from .base import WritingMethod, MethodStage
from .three_act import ThreeActMethod
from .hero_journey import HeroJourneyMethod
from .seven_point import SevenPointMethod
from .method_converter import method_converter, MethodConverter

__all__ = [
    "WritingMethod", "MethodStage",
    "ThreeActMethod", "HeroJourneyMethod", "SevenPointMethod",
    "method_converter", "MethodConverter",
]
