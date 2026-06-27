import random
from typing import List, Any, Union
from pythra import Framework

framework = Framework.instance()


class MotionValue:
    """Represents a reactive motion value that can drive properties directly in the DOM.

    Updates to this value (e.g. from animations or Python code) instantly propagate to all
    bound style properties.
    """

    def __init__(self, initial_value: float = 0.0):
        # ── Sections divider matching user_global rule ──
        # ── Unique ID Generation ─────────────────────────────────────────────
        self.id = f"mv_{id(self)}_{random.randint(1000, 9999)}"
        self.initial_value = initial_value

    def map(self, input_range: List[float], output_range: List[Union[float, str]]) -> "TransformValue":
        """Linearly map this value to a new range of values (e.g. mapping 0-100 to 0-1 opacity)."""
        return TransformValue(self, input_range, output_range)

    def set(self, value: float):
        """Set the value of this MotionValue, updating all bound UI elements instantly."""
        self.initial_value = value
        if framework and framework.window:
            window_id = getattr(framework, "id", None)
            if window_id:
                js = f"""
                    (function(){{
                        if (window.PythraMotionValues) {{
                            var mv = window.PythraMotionValues.get('{self.id}');
                            if (mv) {{
                                mv.set({value});
                            }}
                        }}
                    }})()
                """
                framework.window.evaluate_js(window_id, js)

    def __str__(self) -> str:
        # Serialized token: motion-val:id:initial_value
        return f"motion-val:{self.id}:{self.initial_value}"


class TransformValue:
    """Represents a mapped transform value derived from a parent MotionValue."""

    def __init__(self, source: MotionValue, input_range: List[float], output_range: List[Union[float, str]]):
        self.id = f"tv_{id(self)}_{random.randint(1000, 9999)}"
        self.source = source
        self.input_range = input_range
        self.output_range = output_range

    def __str__(self) -> str:
        # Serialized token: motion-val:id:map:source_id:input_range:output_range
        input_str = ",".join(map(str, self.input_range))
        output_str = ",".join(map(str, self.output_range))
        return f"motion-val:{self.id}:map:{self.source.id}:{input_str}:{output_str}"
