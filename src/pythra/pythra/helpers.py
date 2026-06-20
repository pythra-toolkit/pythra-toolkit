"""Utility helpers for CSS generation and common transformations."""

from typing import Any, Dict, List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# CSS unit helpers
# ---------------------------------------------------------------------------

def to_unit(value):
    """Convert a number to a CSS pixel string, or pass through strings/None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return f"{value}px"
    if isinstance(value, str):
        return value
    raise TypeError(f"Expected int, float, str, or None, got {type(value).__name__}")


def dict_to_css(style_dict: Dict[str, str]) -> str:
    """Convert a dict of CSS properties to a semicolon-separated string."""
    return " ".join(f"{prop}: {value};" for prop, value in style_dict.items())


def camel_to_kebab(name: str) -> str:
    """Convert camelCase to kebab-case (e.g. 'borderRadius' → 'border-radius')."""
    return "".join(
        ["-" + c.lower() if c.isupper() else c for c in name]
    ).lstrip("-")


def hex_to_rgba(hex_str: str, alpha: float) -> Optional[str]:
    """Convert a #RRGGBB hex string to an rgba() string with the given alpha."""
    if not hex_str or not hex_str.startswith("#") or len(hex_str) != 7:
        return None
    try:
        r, g, b = (
            int(hex_str[1:3], 16),
            int(hex_str[3:5], 16),
            int(hex_str[5:7], 16),
        )
        return f"rgba({r}, {g}, {b}, {alpha})"
    except (ValueError, IndexError):
        return None


M3_STANDARD_EASING = "cubic-bezier(0.4, 0.0, 0.2, 1)"


# ---------------------------------------------------------------------------
# Shape / border-radius normalization
# ---------------------------------------------------------------------------

def normalize_shape(shape, default: Union[int, float] = 4.0) -> str:
    """Normalize a shape parameter to a CSS border-radius value.

    Accepts BorderRadius, int, float, tuple, or None.
    """
    if shape is None:
        return to_unit(default)
    from .styles import BorderRadius  # defer import to avoid circular deps
    if isinstance(shape, BorderRadius):
        return shape.to_css_value()
    if isinstance(shape, tuple):
        return BorderRadius(*shape).to_css_value()
    if isinstance(shape, (int, float)):
        return to_unit(max(0.0, shape))
    return to_unit(default)


# ---------------------------------------------------------------------------
# Decoration parsing
# ---------------------------------------------------------------------------

def parse_decoration(val):
    """Parse a value into a BoxDecoration if possible.

    Accepts None, a BoxDecoration, a tuple of constructor args,
    or any object with ``to_css()``.
    """
    if not val:
        return None
    if isinstance(val, tuple):
        try:
            from .styles import BoxDecoration
            return BoxDecoration(*val)
        except Exception:
            return None
    return val if hasattr(val, "to_css") else None


# ---------------------------------------------------------------------------
# M3 elevation shadow
# ---------------------------------------------------------------------------

def elevation_shadow(
    elevation: float,
    shadow_color: Optional[str] = None,
) -> str:
    """Build an M3-style box-shadow string for a given elevation level."""
    color = shadow_color or "rgba(0,0,0,0.2)"
    if not elevation or elevation <= 0:
        return ""

    if elevation >= 3:
        return (
            f"box-shadow: 0px 3px 5px -1px {color}, "
            f"0px 6px 10px 0px rgba(0,0,0,0.14), "
            f"0px 1px 18px 0px rgba(0,0,0,0.12);"
        )

    # Elevation 1-2
    return (
        f"box-shadow: 0px 1px 3px 0px rgba(0,0,0,0.30), "
        f"0px 1px 1px 0px rgba(0,0,0,0.15);"
    )


def elevation_shadow_custom(
    elevation: float,
    shadow_color: Optional[str] = None,
) -> Tuple[str, str]:
    """Compute ambient and key shadow strings for a custom elevation.

    Returns (ambient_shadow, key_shadow) suitable for combining.
    """
    color = shadow_color or "rgba(0,0,0,0.2)"
    if not elevation or elevation <= 0:
        return ("", "")

    offset_y = 1 + elevation * 0.5
    blur = 2 + elevation * 1.0
    spread = 0

    ambient = (
        f"0px {to_unit(offset_y * 0.5)} {to_unit(blur * 0.5)} "
        f"{to_unit(spread)} rgba(0,0,0,0.15)"
    )
    key = (
        f"0px {to_unit(offset_y)} {to_unit(blur)} "
        f"{to_unit(spread + 1)} rgba(0,0,0,0.10)"
    )
    return (ambient, key)


def elevation_shadow_hover_custom(
    elevation: float,
    shadow_color: Optional[str] = None,
) -> Tuple[str, str]:
    """Compute ambient and key shadow strings for a hovered state."""
    color = shadow_color or "rgba(0,0,0,0.25)"
    if not elevation or elevation <= 0:
        return ("", "")

    h_offset_y = 1 + (elevation + 2) * 0.5
    h_blur = 2 + (elevation + 2) * 1.0
    h_spread = 0

    ambient = (
        f"0px {to_unit(h_offset_y * 0.5)} {to_unit(h_blur * 0.5)} "
        f"{to_unit(h_spread)} rgba(0,0,0,0.18)"
    )
    key = (
        f"0px {to_unit(h_offset_y)} {to_unit(h_blur)} "
        f"{to_unit(h_spread + 1)} rgba(0,0,0,0.13)"
    )
    return (ambient, key)


# ---------------------------------------------------------------------------
# Ripple effect
# ---------------------------------------------------------------------------

def build_ripple_css(
    css_class: str,
    fg_color: Optional[str] = None,
    start_opacity: float = 0.2,
) -> str:
    """Build keyframe + base + active CSS rules for a Material ripple effect.

    Returns the concatenated CSS string.
    """
    bg = f"{repr(fg_color)} if {repr(fg_color)} else 'currentColor'" if fg_color else "currentColor"
    keyframes = (
        f"@keyframes ripple_{css_class} {{"
        f" 0% {{ transform: translate(-50%, -50%) scale(0); opacity: {start_opacity}; }}"
        f" 100% {{ transform: translate(-50%, -50%) scale(2.5); opacity: 0; }}"
        f" }}"
    )
    base = (
        f".{css_class}::after {{"
        f" content: ''; position: absolute; top: 50%; left: 50%;"
        f" width: 100%; padding-top: 100%; background-color: {bg};"
        f" border-radius: 50%; transform: translate(-50%, -50%) scale(0);"
        f" opacity: 0; pointer-events: none;"
        f" }}"
    )
    active = (
        f".{css_class}:active::after {{"
        f" animation: ripple_{css_class} 0.6s ease-out;"
        f" }}"
    )
    return f"{keyframes}\n{base}\n{active}"


# ---------------------------------------------------------------------------
# Disabled state rule
# ---------------------------------------------------------------------------

def build_disabled_rule(
    css_class: str,
    bg_color: str = "transparent",
    fg_color: str = "rgba(0, 0, 0, 0.38)",
    no_shadow: bool = True,
    extra: str = "",
) -> str:
    """Build a CSS rule for the .disabled state of a widget."""
    shadow = "box-shadow: none;" if no_shadow else ""
    return (
        f".{css_class}.disabled {{"
        f" background-color: {bg_color};"
        f" color: {fg_color};"
        f" {shadow}"
        f" cursor: default; pointer-events: none;"
        f" {extra}"
        f" }}"
    )


# ---------------------------------------------------------------------------
# Interactive state rules (hover, focus, active)
# ---------------------------------------------------------------------------

def build_interactive_css(
    css_class: str,
    style_obj,
) -> str:
    """Build hover/focus-visible/active pseudo-class rules from a style object.

    The style object should have optional ``hoverStyle``, ``focusStyle``,
    and ``activeStyle`` attributes (each a BoxDecoration, tuple, or None).
    Returns the concatenated CSS (may be empty).
    """
    rules = []
    for pseudo, attr in [
        ("hover", "hoverStyle"),
        ("focus-visible", "focusStyle"),
        ("active", "activeStyle"),
    ]:
        dec = parse_decoration(getattr(style_obj, attr, None))
        if dec:
            rules.append(f".{css_class}:{pseudo} {{ {dec.to_css()} }}")
    return "\n".join(rules)
