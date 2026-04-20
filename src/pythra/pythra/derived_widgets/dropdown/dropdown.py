# dropdown.py

import os
import sys
import json

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pythra.styles import *
from pythra.widgets import *
from pythra.state import *
from pythra.core import Framework
from .controller import VirtualDropdownController
from .style import VirtualDropdownTheme
from typing import Callable, List, Optional


# ==============================================================================
# 2. THE DROPDOWN WIDGET AND ITS STATE (The Core Component)
# ==============================================================================


class VirtualDropdown(StatefulWidget):
    """
    A composable dropdown widget that displays a menu of selectable items.
    Its value is controlled by a VirtualDropdownController.
    """

    def __init__(
        self,
        key: Key,  # pyright: ignore[reportInvalidTypeForm]
        itemBuilder: Optional[Callable[[str], None]] = None,
        controller: VirtualDropdownController = None,
        onChanged: Optional[Callable[[str], None]] = None,
        initialItemCount: Optional[int] = 5,
        theme: Optional[VirtualDropdownTheme] = None,
        margin: Optional[EdgeInsets] = None,
        dropDirection: Optional[str] = None,
        hoverStyle: Optional[BoxDecoration] = None,
        focusStyle: Optional[BoxDecoration] = None,
        activeStyle: Optional[BoxDecoration] = None,
        itemHoverStyle: Optional[BoxDecoration] = None,
        itemFocusStyle: Optional[BoxDecoration] = None,
        itemActiveStyle: Optional[BoxDecoration] = None,
    ):

        # Store configuration on the widget instance.
        self.itemBuilder = itemBuilder
        self.controller = controller
        self.onChanged = onChanged
        self.initialItemCount = initialItemCount
        self.theme = (
            theme
            if theme
            else VirtualDropdownTheme(
                hoverStyle=hoverStyle,
                focusStyle=focusStyle,
                activeStyle=activeStyle,
                itemHoverStyle=itemHoverStyle,
                itemFocusStyle=itemFocusStyle,
                itemActiveStyle=itemActiveStyle,
            )
        )
        self.margin = margin
        # Direction for dropdown placement: VerticalDirection.UP/DOWN or HorizontalDirection.LEFT/RIGHT
        self.dropDirection = (
            dropDirection if dropDirection is not None else VerticalDirection.DOWN
        )

        # print("key init: ", key)

        # super().__init__() must be called to kick off the state creation lifecycle.
        super().__init__(key=key)

    def createState(self):
        return _VirtualDropdownState()


class _VirtualDropdownState(State):
    """Manages the internal UI state of the VirtualDropdown (e.g., if it's open)."""

    def __init__(self):
        self.is_open: bool = False
        self.itemBuilder: Optional[Callable[[str], None]] = None
        self.controller: VirtualDropdownController = None
        self.theme: VirtualDropdownTheme = None
        self.selected_value: Optional[Any] = None
        self.initialItemCount: Optional[int] = None
        self.list_controller = VirtualListController()
        self.parent_key = None
        self.margin: Optional[EdgeInsets] = None
        self.dropDirection: Optional[str] = None

    def initState(self):
        """Called once when the state is created."""

        # Listen for external changes to the controller's value
        self.get_widget().controller.add_listener(self._on_external_update)

    def dispose(self):
        """Called when the widget is removed, to prevent memory leaks."""
        self.get_widget().controller.remove_listener(self._on_external_update)

    def _on_external_update(self, new_value: str):
        """When the controller changes externally, just rebuild the widget."""
        self.setState()

    def _update_floating_label_background(self):
        fw = Framework.instance()
        key_1 = f"dropdown_button_{self.parent_key}_floating_label_container"
        key_2 = f"dropdown_button_{self.parent_key}_container"
        if key_1:
            fw.window.evaluate_js(
                fw.id, f"setFloatingLabelBg('{key_1}', getFinalSolidColor('{key_2}'));"
            )

    def toggle_dropdown(self, key=None):
        """Opens or closes the dropdown menu."""
        self.is_open = not self.is_open
        # if key[1] == self.selected_value:
        print("is_open: ", self.is_open)
        # print("Pressed dropdown key: ", key[0], key[1], key[2])
        # self._update_floating_label_background()
        self.setState()

    def select_item(self, value):
        """Handles item selection, updates the controller, and closes the menu."""
        widget = self.get_widget()
        if not widget:
            return

        # 1. Update the controller. This will trigger the listener.
        widget.controller.set_value(value[0])

        # 2. Close the dropdown menu.
        self.is_open = False

        # 3. Call the developer's onChanged callback.
        if widget.onChanged:
            widget.onChanged(value[0])

        # 4. We don't need a setState() here because the listener (_on_external_update)
        #    will be called by set_value, which in turn calls setState().
        #    However, to ensure the dropdown closes instantly, we'll call it.
        self.setState()

    def vlist_item_builder(self, item: int) -> Widget:
        return Container(
            height=40,
            padding=self.theme.itemPadding
            or EdgeInsets.symmetric(horizontal=12, vertical=8),
            color=(
                self.theme.selectedItemColor
                if self.controller.items[item] == self.selected_value
                else Colors.transparent
            ),
            width="100%",
            decoration=BoxDecoration(
                borderRadius=self.theme.selectedItemShape or BorderRadius.circular(4),
            ),
            key=Key(f"dropdown_item_{item}_padding_{self.parent_key}"),
            child=ListTile(
                key=Key(f"dropdown_item_{item}_{self.parent_key}"),
                title=Text(
                    self.controller.items[item],
                    key=Key(f"dropdown_item_title_{item}_{self.parent_key}"),
                    style=TextStyle(color=self.theme.dropdownTextColor),
                ),
                onTap=self.select_item,
                onTapName=f"item_tap_callback_{self.parent_key}_{item}",
                onTapArg=[self.controller.items[item]],
                selected=self.controller.items[item] == self.selected_value,
                selectedTileColor=self.theme.selectedItemColor,
                contentPadding=EdgeInsets.symmetric(horizontal=12, vertical=8),
                hoverStyle=self.theme.itemHoverStyle,
                focusStyle=self.theme.itemFocusStyle,
                activeStyle=self.theme.itemActiveStyle,
            ),
        )

    def build(self) -> Widget:
        """Builds the dropdown UI, including the overlay menu if it's open."""
        widget = self.get_widget()
        if not widget:
            return SizedBox()  # Return empty if widget is gone

        # Get the authoritative configuration from the widget instance
        self.controller = widget.controller
        self.theme = widget.theme if widget.theme else VirtualDropdownTheme()
        self.selected_value = self.controller.value
        self.initialItemCount = widget.initialItemCount
        self.itemBuilder = widget.itemBuilder
        self.margin = widget.margin
        # capture dropDirection from widget (fallback to DOWN)
        self.dropDirection = getattr(widget, "dropDirection", VerticalDirection.DOWN)

        # --- SOLUTION: Use the parent widget's key to create stable child keys ---
        parent_key = widget.key.value
        self.parent_key = parent_key

        # ── Resolve trigger-button appearance ───────────────────────────────
        dec: Optional[InputDecoration] = (
            self.theme.inputDecoration
            if hasattr(self.theme, "inputDecoration")
            and self.theme.inputDecoration is not None
            else None
        )
        _use_decoration = dec is not None

        # --- Use a Stack to layer the menu over other content ---
        # `clipBehavior=ClipBehavior.NONE` is crucial to allow the menu
        # to draw outside the bounds of the Stack's original layout space.
        # ── Build the trigger button child based on decoration mode ────────
        if _use_decoration:
            # InputDecoration mode: mimic TextField's outlined/filled appearance.
            _fill = dec.fillColor
            _border_radius = dec.borderRadius or BorderRadius.all(4)
            _border = dec.border or BorderSide(width=2.0, color=Colors.outline)
            _focused_border = dec.focusedBorder or BorderSide(
                width=2.0, color=dec.focusColor or Colors.primary
            )
            # Use focused border visually when dropdown is open
            _active_border = _focused_border if self.is_open else _border
            _label_text = dec.label or ""
            _hint_text = dec.hintText or "Select..."
            _display_text = self.selected_value or _hint_text
            _text_color = (
                dec.inputStyle.color
                if dec.inputStyle and dec.inputStyle.color
                else Colors.onSurface
            )
            _text_font_size = (
                dec.inputStyle.fontSize
                if dec.inputStyle and dec.inputStyle.fontSize
                else 16
            )
            _label_color = (
                dec.focusColor
                if self.is_open
                else (dec.labelColor or Colors.onSurfaceVariant)
            )
            _content_padding = dec.contentPadding or EdgeInsets.symmetric(
                horizontal=16, vertical=16
            )

            # Choose arrow icon based on dropDirection so the trigger reflects placement
            dropdown_icon = Icons.arrow_drop_down_rounded
            if self.dropDirection == VerticalDirection.UP:
                dropdown_icon = Icons.arrow_drop_up_rounded
            elif self.dropDirection == HorizontalDirection.LEFT:
                dropdown_icon = Icons.arrow_left_rounded
            elif self.dropDirection == HorizontalDirection.RIGHT:
                dropdown_icon = Icons.arrow_right_rounded

            trigger_child = Container(
                key=Key(f"dropdown_button_{parent_key}_m3_container"),
                width=self.theme.width,
                # role="dropdown-button",
                decoration=BoxDecoration(
                    color=_fill,
                    border=_active_border,
                    borderRadius=_border_radius,
                ),
                hoverStyle=self.theme.hoverStyle,
                focusStyle=self.theme.focusStyle,
                activeStyle=self.theme.activeStyle,
                child=Stack(
                    key=Key(f"dropdown_button_{parent_key}_decoration_stack"),
                    clipBehavior=ClipBehavior.NONE,
                    children=[
                        Positioned(
                            key=Key(f"dropdown_button_{parent_key}_floating_label_pos"),
                            left="16px",
                            top=f"-{_active_border.width}px",
                            bottom=0,
                            child=Container(
                                key=Key(
                                    f"dropdown_button_{parent_key}_floating_label_container"
                                ),
                                cssPosition="fixed",
                                height=8,
                                # role="floating-label-container",
                                js_init={
                                    "engine": "PythraVirtualizedDropdownInternal",
                                    "instance_name": f"virtualized-dropdown-widget{parent_key}",
                                    "options": {
                                        "floatingLabelContainerKey": f"dropdown_button_{parent_key}_floating_label_container",
                                        "dropdownButtonKey": f"dropdown_button_{parent_key}_m3_container",
                                        "floatingLabelPositionKey": f"dropdown_button_{parent_key}_floating_label_pos",
                                    },
                                },
                                child=Transform.translate(
                                    offset=Offset(0, -10),
                                    key=Key(
                                        f"dropdown_button_{parent_key}_floating_label_translate"
                                    ),
                                    child=Text(
                                        (
                                            _label_text
                                            if _label_text and self.selected_value
                                            else ""
                                        ),
                                        key=Key(
                                            f"dropdown_button_{parent_key}_floating_label"
                                        ),
                                        style=TextStyle(
                                            color=_label_color,
                                            fontSize=12,
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        # Content row: label-as-hint + value + arrow
                        Container(
                            key=Key(f"dropdown_button_{parent_key}_inner_padding"),
                            padding=EdgeInsets.symmetric(horizontal=16, vertical=8),
                            width=self.theme.width,
                            child=Row(
                                key=Key(f"dropdown_button_{parent_key}_row"),
                                mainAxisAlignment=MainAxisAlignment.SPACE_BETWEEN,
                                crossAxisAlignment=CrossAxisAlignment.CENTER,
                                children=[
                                    Column(
                                        key=Key(
                                            f"dropdown_button_{parent_key}_text_col"
                                        ),
                                        mainAxisAlignment=MainAxisAlignment.CENTER,
                                        crossAxisAlignment=CrossAxisAlignment.START,
                                        children=[
                                            # Floating label (shown when a value is selected)
                                            # Selected value / hint
                                            Text(
                                                _display_text,
                                                key=Key(
                                                    f"dropdown_button_{parent_key}_text"
                                                ),
                                                style=TextStyle(
                                                    color=(
                                                        _text_color
                                                        if self.selected_value
                                                        else (
                                                            dec.hintStyle.color
                                                            if dec.hintStyle
                                                            and dec.hintStyle.color
                                                            else Colors.onSurfaceVariant
                                                        )
                                                    ),
                                                    fontSize=_text_font_size,
                                                ),
                                            ),
                                        ],
                                    ),
                                    Icon(
                                        dropdown_icon,
                                        key=Key(f"dropdown_button_{parent_key}_icon"),
                                        color=_label_color,
                                        size=20,
                                    ),
                                ],
                            ),
                        ),
                        # Resting label (shown when nothing is selected)
                        Positioned(
                            key=Key(f"dropdown_button_{parent_key}_resting_label_pos"),
                            left=16,
                            top=0,
                            bottom=0,
                            child=(
                                Center(
                                    key=Key(
                                        f"dropdown_button_{parent_key}_resting_label_center"
                                    ),
                                    child=Text(
                                        _label_text,
                                        key=Key(
                                            f"dropdown_button_{parent_key}_resting_label"
                                        ),
                                        style=TextStyle(
                                            color=_label_color,
                                            fontSize=16,
                                        ),
                                    ),
                                )
                                if _label_text and not self.selected_value
                                else SizedBox(
                                    key=Key(
                                        f"dropdown_button_{parent_key}_resting_label_sizedbox"
                                    )
                                )
                            ),
                        ),
                    ],
                ),
            )
        else:
            # Legacy flat-prop mode — original appearance unchanged
            trigger_child = Container(
                key=Key(f"dropdown_button_{parent_key}_Legacy_container"),
                padding=self.theme.padding,
                width=self.theme.width,
                decoration=BoxDecoration(
                    color=self.theme.backgroundColor,
                    border=_border,
                    borderRadius=BorderRadius.circular(self.theme.borderRadius),
                ),
                hoverStyle=self.theme.hoverStyle,
                focusStyle=self.theme.focusStyle,
                activeStyle=self.theme.activeStyle,
                child=Row(
                    key=Key(f"dropdown_button_{parent_key}_row"),
                    mainAxisAlignment=MainAxisAlignment.SPACE_BETWEEN,
                    crossAxisAlignment=CrossAxisAlignment.CENTER,
                    children=[
                        Text(
                            self.selected_value or "Select...",
                            key=Key(f"dropdown_button_{parent_key}_text"),
                            style=TextStyle(
                                color=self.theme.textColor,
                                fontSize=self.theme.fontSize,
                            ),
                        ),
                        SizedBox(
                            width=8,
                            key=Key(f"dropdown_button_{parent_key}_icon_padding"),
                        ),
                        Icon(
                            dropdown_icon,
                            key=Key(f"dropdown_button_{parent_key}_icon"),
                            color=self.theme.textColor,
                            size=20,
                        ),
                    ],
                ),
            )

        _btn_shape = (
            _border_radius
            if _use_decoration
            else BorderRadius.circular(self.theme.borderRadius)
        )

        return Container(
            key=Key(f"dropdown_op_Stack_{parent_key}_root_container"),
            width=self.theme.width,
            margin=self.margin,
            child=Stack(
                key=Key(f"dropdown_op_Stack_{parent_key}_icon"),
                clipBehavior=ClipBehavior.NONE,
                children=[
                    # The main box is the base layer of the stack.
                    Container(
                        key=Key(f"dropdown_button_{parent_key}_text_button_root_con"),
                        cssPosition="absolute",
                        zAxisIndex=10000,
                        child=TextButton(
                            key=Key(f"dropdown_button_{parent_key}_text_button"),
                            onPressed=self.toggle_dropdown,
                            onPressedArgs=[
                                "dropdown_button_",
                                self.selected_value,
                                self.controller.items,
                            ],
                            onPressedName=f"my_dropdown_toggle_callback_{parent_key}",
                            style=ButtonStyle(
                                padding=EdgeInsets.all(0),
                                shape=_btn_shape,
                                backgroundColor=Colors.transparent,
                            ),
                            child=trigger_child,
                        ),
                    ),
                    # The menu is positioned relative to the Stack.
                    (
                        Positioned(
                            key=Key(f"dropdown_op_Positioned_{parent_key}_overlay"),
                            top="-1000px",  # Position it just below the main box (adjust as needed)
                            left="-1000px",
                            right=0,
                            width="15000px",
                            height="15000px",
                            child=GestureDetector(
                                key=Key(
                                    f"dropdown_op_Positioned_{parent_key}_overlay_con_gesture_detector"
                                ),
                                onTap=lambda t: self.toggle_dropdown(t),
                                child=Container(
                                    key=Key(
                                        f"dropdown_op_Positioned_{parent_key}_overlay_con"
                                    ),
                                    height=15000,
                                    width=15000,
                                    color=Colors.hex("#00000009"),
                                    cssPosition="fixed",
                                    zAxisIndex=9999,
                                ),
                            ),
                        )
                        if self.is_open
                        else Container(height=0)
                    ),
                    # position the dropdown menu according to `dropDirection`
                    Positioned(
                        key=Key(f"dropdown_op_Positioned_{parent_key}_iconpos"),
                        **(
                            # Vertical UP: anchor above the trigger (use bottom)
                            {
                                "bottom": "15px",
                                "left": 0,
                                "right": 0,
                                "width": f"{self.theme.width}px",
                                "height": f"{self.theme.dropdownHeight}px",
                            }
                            if self.dropDirection == VerticalDirection.UP
                            # Horizontal LEFT: anchor to the left of the trigger
                            else (
                                {
                                    "top": "50px",
                                    "right": f"{self.theme.width}px",
                                    "width": f"{self.theme.width}px",
                                    "height": f"{self.theme.dropdownHeight}px",
                                }
                                if self.dropDirection == HorizontalDirection.LEFT
                                # Horizontal RIGHT: anchor to the right (default left 0)
                                else (
                                    {
                                        "top": "50px",
                                        "left": 0,
                                        "right": 0,
                                        "width": f"{self.theme.width}px",
                                        "height": f"{self.theme.dropdownHeight}px",
                                    }
                                    if self.dropDirection == HorizontalDirection.RIGHT
                                    # Default / Vertical DOWN
                                    else {
                                        "top": "50px",
                                        "left": 0,
                                        "right": 0,
                                        "width": f"{self.theme.width}px",
                                        "height": f"{self.theme.dropdownHeight}px",
                                    }
                                )
                            )
                        ),
                        child=(
                            Container(
                                height=self.theme.dropdownHeight,
                                key=Key(f"dropdown_op_container_{parent_key}_icon_"),
                                color=_fill if _use_decoration else None,
                                cssPosition="fixed",
                                zAxisIndex=100000,
                                child=Container(
                                    key=Key(f"dropdown_menu_container{parent_key}_122"),
                                    # margin=self.theme.dropdownMargin.edit(
                                    #     operation="+", top=40
                                    # ),
                                    # padding=self.theme.padding,
                                    # color=self.theme.dropdownColor,
                                    width=self.theme.width,  # self.theme.width,
                                    height=self.theme.dropdownHeight,  # self.theme.dropdownHeight,
                                    zAxisIndex=1000,
                                    padding=self.theme.padding,
                                    decoration=BoxDecoration(
                                        color=(
                                            _fill
                                            if _use_decoration
                                            else self.theme.dropdownColor
                                        ),
                                        borderRadius=BorderRadius.circular(
                                            self.theme.borderRadius
                                        ),
                                        boxShadow=[
                                            BoxShadow(
                                                color=Colors.rgba(0, 0, 0, 0.15),
                                                blurRadius=12,
                                                offset=Offset(0, 6),
                                            )
                                        ],
                                    ),
                                    child=VirtualListView(
                                        key=Key("my_virtual_list"),
                                        controller=self.list_controller,
                                        itemCount=len(self.controller.items),
                                        itemBuilder=(
                                            self.itemBuilder
                                            if self.itemBuilder
                                            else self.vlist_item_builder
                                        ),
                                        itemExtent=40,
                                        initialItemCount=self.initialItemCount,
                                        theme=ScrollbarTheme(
                                            height=self.theme.dropdownHeight
                                            - self.theme.padding.to_int_vertical(),
                                            # contentPadding=EdgeInsets.only(right=16),
                                        ),
                                    ),
                                ),
                                decoration=BoxDecoration(
                                    borderRadius=BorderRadius.circular(
                                        self.theme.borderRadius
                                    ),
                                ),
                            )
                            if self.is_open
                            else Container(height=self.theme.dropdownHeight)
                        ),  # The menu will only appear if `is_open` is true
                    ),
                ],
            ),
        )
