from typing import Optional, List, Dict, Union, Any
from pythra import Widget, Key


class Svg(Widget):
    """The root SVG container widget, rendering as an <svg> element.

    Acts as the canvas for vector graphic shapes like SvgPath, SvgCircle, SvgRect, etc.
    """
    def __init__(
        self,
        children: List[Widget],
        key: Optional[Key] = None,
        width: Optional[Union[float, str]] = None,
        height: Optional[Union[float, str]] = None,
        viewBox: Optional[str] = None,
        style: Optional[Dict[str, Any]] = None,
        css_class: Optional[str] = None,
    ):
        super().__init__(key=key, children=children)
        self.width = width
        self.height = height
        self.viewBox = viewBox
        self.style = style or {}
        self.css_class = css_class

    def render_props(self) -> Dict[str, Any]:
        attrs = {}
        if self.width is not None:
            attrs["width"] = str(self.width)
        if self.height is not None:
            attrs["height"] = str(self.height)
        if self.viewBox is not None:
            attrs["viewBox"] = self.viewBox

        props = {
            "attributes": attrs,
            "style": self.style,
        }
        if self.css_class:
            props["css_class"] = self.css_class
        return props


class SvgPath(Widget):
    """An SVG path widget, rendering as a <path> element.

    Can be used for drawing lines, curves, and morphing vector shapes.
    """
    def __init__(
        self,
        d: str,
        key: Optional[Key] = None,
        fill: Optional[str] = None,
        stroke: Optional[str] = None,
        strokeWidth: Optional[float] = None,
        strokeDasharray: Optional[str] = None,
        strokeDashoffset: Optional[float] = None,
        style: Optional[Dict[str, Any]] = None,
        css_class: Optional[str] = None,
    ):
        super().__init__(key=key, children=[])
        self.d = d
        self.fill = fill
        self.stroke = stroke
        self.strokeWidth = strokeWidth
        self.strokeDasharray = strokeDasharray
        self.strokeDashoffset = strokeDashoffset
        self.style = style or {}
        self.css_class = css_class

    def render_props(self) -> Dict[str, Any]:
        attrs = {"d": self.d}
        if self.fill is not None:
            attrs["fill"] = self.fill
        if self.stroke is not None:
            attrs["stroke"] = self.stroke
        if self.strokeWidth is not None:
            attrs["stroke-width"] = str(self.strokeWidth)
        if self.strokeDasharray is not None:
            attrs["stroke-dasharray"] = self.strokeDasharray
        if self.strokeDashoffset is not None:
            attrs["stroke-dashoffset"] = str(self.strokeDashoffset)

        props = {
            "attributes": attrs,
            "style": self.style,
        }
        if self.css_class:
            props["css_class"] = self.css_class
        return props


class SvgCircle(Widget):
    """An SVG circle widget, rendering as a <circle> element."""
    def __init__(
        self,
        cx: float,
        cy: float,
        r: float,
        key: Optional[Key] = None,
        fill: Optional[str] = None,
        stroke: Optional[str] = None,
        strokeWidth: Optional[float] = None,
        style: Optional[Dict[str, Any]] = None,
        css_class: Optional[str] = None,
    ):
        super().__init__(key=key, children=[])
        self.cx = cx
        self.cy = cy
        self.r = r
        self.fill = fill
        self.stroke = stroke
        self.strokeWidth = strokeWidth
        self.style = style or {}
        self.css_class = css_class

    def render_props(self) -> Dict[str, Any]:
        attrs = {
            "cx": str(self.cx),
            "cy": str(self.cy),
            "r": str(self.r),
        }
        if self.fill is not None:
            attrs["fill"] = self.fill
        if self.stroke is not None:
            attrs["stroke"] = self.stroke
        if self.strokeWidth is not None:
            attrs["stroke-width"] = str(self.strokeWidth)

        props = {
            "attributes": attrs,
            "style": self.style,
        }
        if self.css_class:
            props["css_class"] = self.css_class
        return props


class SvgRect(Widget):
    """An SVG rect widget, rendering as a <rect> element."""
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        key: Optional[Key] = None,
        rx: Optional[float] = None,
        ry: Optional[float] = None,
        fill: Optional[str] = None,
        stroke: Optional[str] = None,
        strokeWidth: Optional[float] = None,
        style: Optional[Dict[str, Any]] = None,
        css_class: Optional[str] = None,
    ):
        super().__init__(key=key, children=[])
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry
        self.fill = fill
        self.stroke = stroke
        self.strokeWidth = strokeWidth
        self.style = style or {}
        self.css_class = css_class

    def render_props(self) -> Dict[str, Any]:
        attrs = {
            "x": str(self.x),
            "y": str(self.y),
            "width": str(self.width),
            "height": str(self.height),
        }
        if self.rx is not None:
            attrs["rx"] = str(self.rx)
        if self.ry is not None:
            attrs["ry"] = str(self.ry)
        if self.fill is not None:
            attrs["fill"] = self.fill
        if self.stroke is not None:
            attrs["stroke"] = self.stroke
        if self.strokeWidth is not None:
            attrs["stroke-width"] = str(self.strokeWidth)

        props = {
            "attributes": attrs,
            "style": self.style,
        }
        if self.css_class:
            props["css_class"] = self.css_class
        return props


class SvgLine(Widget):
    """An SVG line widget, rendering as a <line> element."""
    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        key: Optional[Key] = None,
        stroke: Optional[str] = None,
        strokeWidth: Optional[float] = None,
        style: Optional[Dict[str, Any]] = None,
        css_class: Optional[str] = None,
    ):
        super().__init__(key=key, children=[])
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.stroke = stroke
        self.strokeWidth = strokeWidth
        self.style = style or {}
        self.css_class = css_class

    def render_props(self) -> Dict[str, Any]:
        attrs = {
            "x1": str(self.x1),
            "y1": str(self.y1),
            "x2": str(self.x2),
            "y2": str(self.y2),
        }
        if self.stroke is not None:
            attrs["stroke"] = self.stroke
        if self.strokeWidth is not None:
            attrs["stroke-width"] = str(self.strokeWidth)

        props = {
            "attributes": attrs,
            "style": self.style,
        }
        if self.css_class:
            props["css_class"] = self.css_class
        return props


class SvgGroup(Widget):
    """An SVG group widget, rendering as a <g> element."""
    def __init__(
        self,
        children: List[Widget],
        key: Optional[Key] = None,
        style: Optional[Dict[str, Any]] = None,
        css_class: Optional[str] = None,
    ):
        super().__init__(key=key, children=children)
        self.style = style or {}
        self.css_class = css_class

    def render_props(self) -> Dict[str, Any]:
        props = {
            "style": self.style,
        }
        if self.css_class:
            props["css_class"] = self.css_class
        return props
