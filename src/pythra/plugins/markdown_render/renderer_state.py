import json
from typing import Optional
from pythra import State, Container, Key, Framework

from .controller import MarkdownRendererController
from .style import RendererStyle

framework = Framework.instance()

class MarkdownRendererState(State):
    def __init__(self):
        super().__init__()
        self._markdown_text: Optional[str] = None
        self._cached_js_init = None

    def initState(self):
        widget = self.widget
        if not widget:
            return

        # Attach controller
        if widget.controller:
            widget.controller._attach(self)

    def dispose(self):
        widget = self.widget
        if widget and widget.controller:
            widget.controller._detach()
        super().dispose()

    def set_markdown(self, markdown_text: str):
        """Update the frontend markdown content dynamically."""
        if not framework or not framework.window:
            return

        self._markdown_text = markdown_text
        widget = self.widget
        if not widget:
            return

        instance_name = f"{widget.key.value}_PythraMarkdownRender"
        md_js = json.dumps(markdown_text)

        js = f"""
            (function(){{
                const engine = window._pythra_instances['{instance_name}'];
                if (engine && typeof engine.renderMarkdown === 'function') {{
                    engine.renderMarkdown({md_js});
                }} else {{
                    console.error("Could not find MarkdownRender engine instance: '{instance_name}'");
                }}
            }})()
        """
        window_id = getattr(self, '_window_id', framework.id)
        framework.window.evaluate_js(window_id, js)

    def build(self):
        widget = self.widget
        if not widget:
            return Container(width=0, height=0)

        if self._markdown_text is None:
             self._markdown_text = widget.markdown_text

        # Memoize js_init
        if self._cached_js_init is None:
            self._cached_js_init = {
                "engine": "PythraMarkdownRender",
                "instance_name": f"{widget.key.value}_PythraMarkdownRender",
                "options": {
                    "instanceId": f"{widget.key.value}_PythraMarkdownRender",
                    "initialMarkdown": self._markdown_text,
                    "width": widget.width,
                    "height": widget.height,
                    "style": widget.style.to_dict() if hasattr(widget.style, 'to_dict') else {}
                }
            }

        return Container(
            key=widget.key,
            width=widget.width,
            height=widget.height,
            js_init=self._cached_js_init
        )
