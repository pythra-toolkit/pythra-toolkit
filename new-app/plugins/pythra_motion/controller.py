import json
from typing import Optional, Dict, Any, List, Callable, Union
from .types import AnimationOptions, Keyframes


class AnimationController:
    def __init__(self):
        self._state_ref = None
        self._listeners: List[Callable] = []

    def _attach(self, state):
        self._state_ref = state

    def _detach(self):
        self._state_ref = None

    def add_listener(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self, event: str, data=None):
        for listener in self._listeners:
            listener(event, data)

    def animate(
        self,
        keyframes: Keyframes,
        options: Optional[Union[dict, AnimationOptions]] = None,
        animation_id: Optional[str] = None,
    ) -> Optional[str]:
        if not self._state_ref:
            return None
        opts = options
        if hasattr(opts, "to_dict"):
            opts = opts.to_dict()
        return self._state_ref.start_animation(keyframes, opts or {}, animation_id)

    def scroll_animate(
        self,
        keyframes: Keyframes,
        scroll_options: Optional[dict] = None,
    ):
        if not self._state_ref:
            return
        self._state_ref.start_scroll_animation(keyframes, scroll_options or {})

    def in_view_animate(
        self,
        keyframes: Keyframes,
        view_options: Optional[dict] = None,
    ):
        if not self._state_ref:
            return
        self._state_ref.start_in_view_animation(keyframes, view_options or {})

    def play(self, animation_id: str):
        if self._state_ref:
            self._state_ref.control_animation(animation_id, "play")

    def pause(self, animation_id: str):
        if self._state_ref:
            self._state_ref.control_animation(animation_id, "pause")

    def stop(self, animation_id: str):
        if self._state_ref:
            self._state_ref.control_animation(animation_id, "stop")

    def reverse(self, animation_id: str):
        if self._state_ref:
            self._state_ref.control_animation(animation_id, "reverse")

    def set_speed(self, animation_id: str, speed: float):
        if self._state_ref:
            self._state_ref.control_animation(animation_id, "setSpeed", speed)

    def set_time(self, animation_id: str, time: float):
        if self._state_ref:
            self._state_ref.control_animation(animation_id, "setTime", time)

    def timeline(
        self,
        sequence: list,
        default_options: Optional[dict] = None,
    ) -> Optional[str]:
        if not self._state_ref:
            return None
        return self._state_ref.start_timeline(sequence, default_options)

    def stagger_children(
        self,
        selector: str,
        keyframes: Keyframes,
        options: Optional[dict] = None,
    ):
        if not self._state_ref:
            return
        self._state_ref.start_stagger(selector, keyframes, options or {})

    def destroy(self):
        if self._state_ref:
            self._state_ref.destroy_animations()
