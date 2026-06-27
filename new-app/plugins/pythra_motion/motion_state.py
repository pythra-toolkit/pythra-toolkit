import json
from typing import Optional

from PySide6.QtCore import QTimer
from pythra import State, Container, Framework, Key

framework = Framework.instance()


class MotionWidgetState(State):
    def __init__(self):
        super().__init__()
        self._cached_js_init = None
        self._callback_name = None

    def initState(self):
        widget = self.widget
        if not widget:
            return

        if widget.controller:
            widget.controller._attach(self)

        self._callback_name = f"pythra_motion_cb_{widget.key.value}"
        if framework and hasattr(framework, 'api') and framework.api:
            framework.api.register_callback(
                self._callback_name, self._handle_animation_event
            )

        scroll_anim = getattr(widget, 'scroll_animation', None)
        if scroll_anim:
            QTimer.singleShot(100, self._setup_scroll_animation)

        timeline_seq = getattr(widget, 'timeline', None)
        if timeline_seq:
            QTimer.singleShot(100, self._setup_timeline)

    def _handle_animation_event(self, event_json: str):
        try:
            event = json.loads(event_json)
            widget = self.widget
            if widget and widget.controller:
                widget.controller._notify_listeners(
                    event.get("type"), event.get("data")
                )
        except json.JSONDecodeError:
            pass

    def _setup_scroll_animation(self):
        widget = self.widget
        if not widget or not framework or not framework.window:
            return

        anim = getattr(widget, 'scroll_animation', None)
        sopts = getattr(widget, 'scroll_options', None)
        if not anim or not sopts:
            return

        instance_name = f"{widget.key.value}_PythraMotion"
        kf_js = json.dumps(anim)
        sopts_js = json.dumps(sopts)

        js = f"""
            (function(){{
                var inst = (window._pythra_instances && window._pythra_instances['{instance_name}']);
                if (inst && typeof inst.scrollAnimate === 'function') {{
                    inst.scrollAnimate({kf_js}, {sopts_js});
                }}
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        framework.window.evaluate_js(window_id, js)

    def _setup_timeline(self):
        widget = self.widget
        if not widget or not framework or not framework.window:
            return

        seq = getattr(widget, 'timeline', None)
        if not seq:
            return

        self.start_timeline(seq)

    def _js_inst(self, instance_name):
        return f"(window._pythra_instances && window._pythra_instances['{instance_name}'])"

    def start_animation(
        self,
        keyframes: dict,
        options: dict,
        animation_id: Optional[str] = None,
    ) -> Optional[str]:
        if not framework or not framework.window:
            return None

        widget = self.widget
        if not widget:
            return None

        instance_name = f"{widget.key.value}_PythraMotion"
        kf_js = json.dumps(keyframes)
        opts_js = json.dumps(options)
        id_js = json.dumps(animation_id) if animation_id else "null"

        def _js_inst():
            return f"(window._pythra_instances && window._pythra_instances['{instance_name}'])"

        js = f"""
            (function(){{
                var inst = {_js_inst()};
                if (inst && typeof inst.animate === 'function') {{
                    var opts = {opts_js};
                    if ({id_js}) {{ opts.id = {id_js}; }}
                    return inst.animate({kf_js}, opts);
                }}
                return null;
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        result = framework.window.evaluate_js(window_id, js)
        return result

    def start_scroll_animation(self, keyframes: dict, scroll_options: dict):
        if not framework or not framework.window:
            return

        widget = self.widget
        if not widget:
            return

        instance_name = f"{widget.key.value}_PythraMotion"
        kf_js = json.dumps(keyframes)
        sopts_js = json.dumps(scroll_options)

        js = f"""
            (function(){{
                var inst = (window._pythra_instances && window._pythra_instances['{instance_name}']);
                if (inst && typeof inst.scrollAnimate === 'function') {{
                    inst.scrollAnimate({kf_js}, {sopts_js});
                }}
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        framework.window.evaluate_js(window_id, js)

    def start_in_view_animation(self, keyframes: dict, view_options: dict):
        if not framework or not framework.window:
            return

        widget = self.widget
        if not widget:
            return

        instance_name = f"{widget.key.value}_PythraMotion"
        kf_js = json.dumps(keyframes)
        vopts_js = json.dumps(view_options)

        js = f"""
            (function(){{
                var inst = (window._pythra_instances && window._pythra_instances['{instance_name}']);
                if (inst && typeof inst.inViewAnimate === 'function') {{
                    inst.inViewAnimate({kf_js}, {vopts_js});
                }}
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        framework.window.evaluate_js(window_id, js)

    def control_animation(self, animation_id: str, command: str, value=None):
        if not framework or not framework.window:
            return

        widget = self.widget
        if not widget:
            return

        instance_name = f"{widget.key.value}_PythraMotion"
        id_js = json.dumps(animation_id)
        cmd_js = json.dumps(command)
        val_js = json.dumps(value) if value is not None else "null"

        js = f"""
            (function(){{
                var inst = (window._pythra_instances && window._pythra_instances['{instance_name}']);
                if (inst && typeof inst.control === 'function') {{
                    inst.control({id_js}, {cmd_js}, {val_js});
                }}
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        framework.window.evaluate_js(window_id, js)

    def start_timeline(self, sequence: list, default_options: dict = None):
        if not framework or not framework.window:
            return None

        widget = self.widget
        if not widget:
            return None

        instance_name = f"{widget.key.value}_PythraMotion"
        seq_js = json.dumps(sequence)
        opts_js = json.dumps(default_options or {})

        js = f"""
            (function(){{
                var inst = (window._pythra_instances && window._pythra_instances['{instance_name}']);
                if (inst && typeof inst.timeline === 'function') {{
                    return inst.timeline({seq_js}, {opts_js});
                }}
                return null;
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        result = framework.window.evaluate_js(window_id, js)
        return result

    def start_stagger(self, selector: str, keyframes: dict, options: dict):
        if not framework or not framework.window:
            return

        widget = self.widget
        if not widget:
            return

        instance_name = f"{widget.key.value}_PythraMotion"
        sel_js = json.dumps(selector)
        kf_js = json.dumps(keyframes)
        opts_js = json.dumps(options)

        js = f"""
            (function(){{
                var inst = (window._pythra_instances && window._pythra_instances['{instance_name}']);
                if (inst && typeof inst.staggerChildren === 'function') {{
                    inst.staggerChildren({sel_js}, {kf_js}, {opts_js});
                }}
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        framework.window.evaluate_js(window_id, js)

    def destroy_animations(self):
        if not framework or not framework.window:
            return

        widget = self.widget
        if not widget:
            return

        instance_name = f"{widget.key.value}_PythraMotion"

        js = f"""
            (function(){{
                var inst = (window._pythra_instances && window._pythra_instances['{instance_name}']);
                if (inst && typeof inst.destroyAll === 'function') {{
                    inst.destroyAll();
                }}
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        framework.window.evaluate_js(window_id, js)

    def dispose(self):
        self.destroy_animations()
        widget = self.widget
        if widget and widget.controller:
            widget.controller._detach()
        if widget and framework and hasattr(framework, 'api') and framework.api:
            cb = f"pythra_motion_cb_{widget.key.value}"
            if cb in framework.api.callbacks:
                del framework.api.callbacks[cb]
        super().dispose()

    def build(self):
        widget = self.widget
        if not widget:
            return Container(width=0, height=0)

        if self._cached_js_init is None:
            options = {
                "instanceId": f"{widget.key.value}_PythraMotion",
                "callback": self._callback_name,
            }

            entrance = getattr(widget, 'entrance_animation', None)
            if entrance:
                options["entranceAnimation"] = entrance
                options["entranceOptions"] = getattr(widget, 'entrance_options', {})

            scroll_anim = getattr(widget, 'scroll_animation', None)
            if scroll_anim:
                options["scrollAnimation"] = scroll_anim
                options["scrollOptions"] = getattr(widget, 'scroll_options', {})

            in_view_anim = getattr(widget, 'in_view_animation', None)
            if in_view_anim:
                options["inViewAnimation"] = in_view_anim
                options["inViewOptions"] = getattr(widget, 'in_view_options', {})

            hover_enter = getattr(widget, 'hover_animation_enter', None)
            if hover_enter:
                options["hoverAnimationEnter"] = hover_enter
                options["hoverAnimationLeave"] = getattr(widget, 'hover_animation_leave', None)
                options["hoverOptions"] = getattr(widget, 'hover_options', {})

            press_start = getattr(widget, 'press_animation_start', None)
            if press_start:
                options["pressAnimationStart"] = press_start
                options["pressAnimationEnd"] = getattr(widget, 'press_animation_end', None)
                options["pressOptions"] = getattr(widget, 'press_options', {})

            self._cached_js_init = {
                "engine": "PythraMotion",
                "instance_name": f"{widget.key.value}_PythraMotion",
                "options": options,
            }

        child = widget.child if hasattr(widget, 'child') else None

        attrs = {}
        if getattr(widget, "layout", False):
            attrs["data-layout"] = "true"
        layout_id = getattr(widget, "layout_id", None)
        if layout_id:
            attrs["data-layout-id"] = layout_id

        return Container(
            key=Key(f"{widget.key.value}_motion_container"),
            js_init=self._cached_js_init,
            attributes=attrs if attrs else None,
            child=child,
        )
