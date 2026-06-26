"""
PyThra Motion Plugin
A Flutter-style animation plugin wrapping motion.dev for Pythra.
Provides Pythonic animation via MotionWidget and AnimationController.
"""

from .widget import MotionWidget
from .controller import AnimationController
from .easing import Easing, SpringPreset
from .types import AnimationOptions, ScrollOptions, InViewOptions, TimelineStep
from .spring import solve_spring, solve_spring_details

__version__ = "1.0.0"
__all__ = [
    "MotionWidget",
    "AnimationController",
    "Easing",
    "SpringPreset",
    "AnimationOptions",
    "ScrollOptions",
    "InViewOptions",
    "TimelineStep",
    "solve_spring",
    "solve_spring_details",
]

plugin_definition = {
    "name": "pythra_motion",
    "version": __version__,
    "js_modules": {
        "PythraMotion": {
            "file": "js/animation_engine.js",
            "global": "PythraMotion",
            "initializer": "initialize",
        }
    },
}
