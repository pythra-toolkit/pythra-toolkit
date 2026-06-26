from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from .api import Api
from .base import Key, Widget
from .helpers import to_unit
from .icons.base import IconData
from .styles import EdgeInsets, BorderRadius, Colors
from .widgets import Container


# ── Helpers ──────────────────────────────────────────────────────────────────


def _css_val(value, default=None):
    """Resolve a style object to its CSS string, or fall back to a default."""
    if value is None:
        return default
    if hasattr(value, "to_css_value"):
        return value.to_css_value()
    if hasattr(value, "to_css"):
        return value.to_css()
    return str(value)


# ── MenuItem ─────────────────────────────────────────────────────────────────


@dataclass
class MenuItem:
    label: str = ""
    onPressed: Optional[Callable] = None
    icon: Optional[Union[str, IconData]] = None
    enabled: bool = True
    divider: bool = False
    shortcut: Optional[str] = None


# ── ContextMenuTheme ─────────────────────────────────────────────────────────


class ContextMenuTheme:
    """Theme for customising the appearance of a ContextMenu.

    All visual properties accept PyThra style objects (Color, EdgeInsets,
    BorderRadius, BoxDecoration, etc.) or plain CSS strings as a fallback.
    ``None`` picks the default value.
    """

    def __init__(
        self,
        *,
        # ── Menu panel ────────────────────────────────────────────────────────
        backgroundColor: Any = None,
        borderColor: Any = None,
        borderRadius: Any = None,
        borderWidth: Any = None,
        elevation: int = 4,
        # ── Items ─────────────────────────────────────────────────────────────
        itemTextColor: Any = None,
        itemFontSize: Any = None,
        itemFontFamily: str = "",
        itemPadding: Any = None,
        itemHoverColor: Any = None,
        disabledOpacity: float = 0.4,
        # ── Icons ─────────────────────────────────────────────────────────────
        iconSize: Any = None,
        iconColor: Any = None,
        # ── Divider ───────────────────────────────────────────────────────────
        dividerColor: Any = None,
        dividerMargin: Any = None,
    ):
        self.backgroundColor = backgroundColor
        self.borderColor = borderColor
        self.borderRadius = borderRadius
        self.borderWidth = borderWidth
        self.elevation = elevation
        self.itemTextColor = itemTextColor
        self.itemFontSize = itemFontSize
        self.itemFontFamily = itemFontFamily
        self.itemPadding = itemPadding
        self.itemHoverColor = itemHoverColor
        self.disabledOpacity = disabledOpacity
        self.iconSize = iconSize
        self.iconColor = iconColor
        self.dividerColor = dividerColor
        self.dividerMargin = dividerMargin

    def to_js_dict(self) -> Dict[str, Any]:
        """Serialise theme values to a flat JSON-friendly dict for the JS engine."""
        d: Dict[str, Any] = {}
        # Menu panel
        bg = _css_val(self.backgroundColor, "#2d2d2d")
        bc = _css_val(self.borderColor, "#555")
        br = _css_val(self.borderRadius, "6px")
        bw = _css_val(self.borderWidth, "1px")
        d["panel"] = {
            "backgroundColor": bg,
            "borderColor": bc,
            "borderRadius": br,
            "borderWidth": bw,
            "boxShadow": (
                f"0 {to_unit(self.elevation)}px {to_unit(max(self.elevation * 2, 8))}px "
                f"rgba(0,0,0,0.3)"
            ),
        }
        # Items
        itc = _css_val(self.itemTextColor, "#eee")
        ifs = _css_val(self.itemFontSize, "13px")
        ifa = self.itemFontFamily or "sans-serif"
        ip = _css_val(self.itemPadding, "6px 16px")
        ihc = _css_val(self.itemHoverColor, "#3d3d3d")
        d["item"] = {
            "color": itc,
            "fontSize": ifs,
            "fontFamily": ifa,
            "padding": ip,
            "hoverBackgroundColor": ihc,
            "disabledOpacity": self.disabledOpacity,
        }
        # Icons
        isz = _css_val(self.iconSize, "18px")
        ic = _css_val(self.iconColor)
        d["icon"] = {"size": isz}
        if ic:
            d["icon"]["color"] = ic
        # Divider
        dc = _css_val(self.dividerColor, "#555")
        dm = _css_val(self.dividerMargin, "4px 0")
        d["divider"] = {"color": dc, "margin": dm}
        return d


# ── ContextMenu widget ────────────────────────────────────────────────────────


class ContextMenu(Container):
    """An app-level widget that wraps content and shows a custom menu on right-click.

    Place this at the root of your widget tree to replace the default browser
    context menu with a themed PyThra menu.

    Example:
        class MyApp(StatefulWidget):
            def build(self) -> Widget:
                return ContextMenu(
                    items=[
                        MenuItem(label="Copy", icon=Icons.content_copy_rounded,
                                 onPressed=lambda: print("Copy!")),
                        MenuItem(label="Paste", icon=Icons.content_paste_rounded,
                                 onPressed=lambda: print("Paste!")),
                        MenuItem(divider=True),
                        MenuItem(label="Delete", icon=Icons.delete_rounded,
                                 onPressed=lambda: print("Delete!")),
                    ],
                    child=Scaffold(...)
                )
    """

    def __init__(
        self,
        child: Optional[Widget] = None,
        items: Optional[List[MenuItem]] = None,
        key: Optional[Key] = None,
        theme: Optional[ContextMenuTheme] = None,
    ):
        self._menu_items = items or []
        self.theme = theme or ContextMenuTheme()

        serialized_items = []
        for i, item in enumerate(self._menu_items):
            cb_name = f"ctx_menu_{uuid.uuid4().hex[:12]}"
            if item.onPressed:
                Api().register_callback(cb_name, item.onPressed)
            icon_val = item.icon
            icon_font = None
            if isinstance(icon_val, IconData):
                icon_font = icon_val.fontFamily
                icon_val = icon_val.name

            serialized_items.append({
                "label": item.label,
                "cb": cb_name if item.onPressed else None,
                "icon": icon_val,
                "fontFamily": icon_font,
                "enabled": item.enabled,
                "divider": item.divider,
                "shortcut": item.shortcut,
            })

        js_init = {
            "engine": "PythraContextMenuInternal",
            "instance_name": f"ctx_menu_{key.value if key else id(self)}",
            "options": {
                "items": serialized_items,
                "theme": self.theme.to_js_dict(),
            },
        }

        super().__init__(
            child=child,
            key=key,
            js_init=js_init,
            cssClass="pythra-context-menu-wrapper",
        )
