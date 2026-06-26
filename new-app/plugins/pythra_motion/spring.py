import json
from typing import Union, List, Dict, Any, Optional
from pythra.async_utils import evaluate_js_sync

# ── Spring Solver Bridge ──────────────────────────────────────────────

def solve_spring(
    keyframes: List[float],
    stiffness: float = 100.0,
    damping: float = 10.0,
    mass: float = 1.0,
    velocity: float = 0.0,
    time_ms: Union[float, List[float]] = 0.0,
    window_id: Optional[str] = None,
) -> Union[float, List[float], None]:
    """
    Evaluate the spring physics solver at a specific time (or list of times) in milliseconds.

    Returns the calculated position value(s) synchronously using evaluate_js_sync.
    """
    config = {
        "keyframes": keyframes,
        "stiffness": stiffness,
        "damping": damping,
        "mass": mass,
        "velocity": velocity,
    }
    config_json = json.dumps(config)

    if isinstance(time_ms, list):
        times_json = json.dumps(time_ms)
        val_js = times_json
    else:
        val_js = str(time_ms)

    script = f"""
    (function() {{
        try {{
            var res = PythraMotion.solveSpring({config_json}, {val_js});
            return JSON.stringify({{ success: true, value: res }});
        }} catch (e) {{
            return JSON.stringify({{ success: false, error: e.name + ": " + e.message + "\\n" + e.stack }});
        }}
    }})()
    """

    res_str = evaluate_js_sync(script, window_id)
    if not res_str:
        return None
    res = json.loads(res_str)
    if not res.get("success"):
        raise RuntimeError(f"JavaScript execution failed: {res.get('error')}")
    return res.get("value")


def solve_spring_details(
    keyframes: List[float],
    stiffness: float = 100.0,
    damping: float = 10.0,
    mass: float = 1.0,
    velocity: float = 0.0,
    times_ms: List[float] = None,
    window_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Evaluate the spring physics solver and return both calculated values and the overall duration.
    """
    config = {
        "keyframes": keyframes,
        "stiffness": stiffness,
        "damping": damping,
        "mass": mass,
        "velocity": velocity,
    }
    config_json = json.dumps(config)
    times_json = json.dumps(times_ms or [])

    script = f"""
    (function() {{
        try {{
            var res = PythraMotion.solveSpringDetails({config_json}, {times_json});
            return JSON.stringify({{ success: true, value: res }});
        }} catch (e) {{
            return JSON.stringify({{ success: false, error: e.name + ": " + e.message + "\\n" + e.stack }});
        }}
    }})()
    """
    res_str = evaluate_js_sync(script, window_id)
    if not res_str:
        return None
    res = json.loads(res_str)
    if not res.get("success"):
        raise RuntimeError(f"JavaScript execution failed: {res.get('error')}")
    return res.get("value")
