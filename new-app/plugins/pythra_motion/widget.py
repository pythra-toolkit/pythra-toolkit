from typing import Optional

from pythra import StatefulWidget, Key, Widget

from .motion_state import MotionWidgetState
from .controller import AnimationController
from .types import Keyframes, TimelineStep


class MotionWidget(StatefulWidget):
    """Wrap any widget with animation capabilities.

    Provides animate/scroll/in-view/hover/press animations via motion.js.
    This is the single entry point for all animation types.

    Usage:
        MotionWidget(
            key=Key("hero"),
            child=my_widget,
            controller=controller,
            entrance_animation={"opacity": [0, 1], "y": [50, 0]},
            hover_animation_enter={"scale": 1.05},
            hover_animation_leave={"scale": 1},
        )
    """

    def __init__(
        self,
        key: Key,
        child: Widget,
        controller: AnimationController = None,
        entrance_animation: Optional[Keyframes] = None,
        entrance_options: Optional[dict] = None,
        scroll_animation: Optional[Keyframes] = None,
        scroll_options: Optional[dict] = None,
        in_view_animation: Optional[Keyframes] = None,
        in_view_options: Optional[dict] = None,
        hover_animation_enter: Optional[Keyframes] = None,
        hover_animation_leave: Optional[Keyframes] = None,
        hover_options: Optional[dict] = None,
        press_animation_start: Optional[Keyframes] = None,
        press_animation_end: Optional[Keyframes] = None,
        press_options: Optional[dict] = None,
        timeline: Optional[list] = None,
        layout: bool = False,
        layout_id: Optional[str] = None,
    ):
        self.child = child
        self.controller = controller or AnimationController()
        self.entrance_animation = entrance_animation
        self.entrance_options = entrance_options
        self.scroll_animation = scroll_animation
        self.scroll_options = scroll_options
        self.in_view_animation = in_view_animation
        self.in_view_options = in_view_options
        self.hover_animation_enter = hover_animation_enter
        self.hover_animation_leave = hover_animation_leave
        self.hover_options = hover_options
        self.press_animation_start = press_animation_start
        self.press_animation_end = press_animation_end
        self.press_options = press_options
        self.timeline = timeline
        self.layout = layout
        self.layout_id = layout_id
        super().__init__(key=key)

    def createState(self):
        return MotionWidgetState()
