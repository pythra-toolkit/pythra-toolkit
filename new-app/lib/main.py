import os
from pathlib import Path
import sys
import json
from typing import Optional, Union

from PySide6.QtCore import QTimer

from pythra import (
    Framework,
    StatefulWidget,
    State,
    Column,
    Row,
    Key,
    Widget,
    Container,
    Text,
    Alignment,
    Colors,
    Center,
    ElevatedButton,
    SizedBox,
    MainAxisAlignment,
    CrossAxisAlignment,
    EdgeInsets,
    ButtonStyle,
    TextStyle,
    Stack,
    Positioned,
    BoxDecoration,
    BorderRadius,
    BorderSide,
    Slider,
    SliderController,
    GestureDetector,
    Scrollbar,
    SingleChildScrollView,
    ContextMenu,
    MenuItem,
    Icons,
    ContextMenuTheme,
)
from pythra.styles import Offset

from plugins.pythra_motion.widget import MotionWidget
from plugins.pythra_motion.controller import AnimationController
from plugins.pythra_motion.easing import Easing, SpringPreset
from plugins.pythra_motion.types import AnimationOptions
from plugins.pythra_motion.svg import Svg, SvgPath, SvgCircle, SvgRect, SvgLine, SvgGroup
from plugins.pythra_motion import MotionValue


def runApp(rootWidget):
    app = Framework.instance()
    app.set_root(rootWidget())
    app.run()
    return rootWidget


ANIM_CARD = """
A Flutter-style animation plugin wrapping motion.dev for Pythra.
Provides Pythonic animations via MotionWidget and AnimationController.
"""


def _card(
    key: Key,
    title: str,
    description: str,
    child: Widget,
    width: str = "80vw",
    height: str = "auto",
):
    card_key = key.value if isinstance(key, Key) else str(key)
    return Container(
        key=key,
        width=width,
        height=height,
        decoration=BoxDecoration(
            color=Colors.hex("#2A2A2A"),
            borderRadius=BorderRadius.all(12),
            border=BorderSide(color=Colors.hex("#3A3A3A"), width=1),
        ),
        padding=EdgeInsets.all(20),
        margin=EdgeInsets.all(20),
        child=Column(
            key=Key(f"card_col_{card_key}"),
            crossAxisAlignment=CrossAxisAlignment.START,
            children=[
                Text(
                    title,
                    key=Key(f"card_title_{card_key}"),
                    style=TextStyle(
                        fontSize=18, color=Colors.hex("#FFFFFF"), fontWeight="bold"
                    ),
                ),
                SizedBox(height=4, key=Key(f"card_spacer1_{card_key}")),
                Text(
                    description,
                    key=Key(f"card_desc_{card_key}"),
                    style=TextStyle(fontSize=12, color=Colors.hex("#888888")),
                ),
                SizedBox(height=16, key=Key(f"card_spacer2_{card_key}")),
                child,
            ],
        ),
    )


class DemoPageState(State):
    def __init__(self):
        super().__init__()
        self.anim_ctrl = AnimationController()
        self.slider_ctrl = SliderController(value=0.0)
        self._rotating = False
        self.layout_expanded = False
        self.shared_element_position = 1
        self.reactive_val = MotionValue(0.0)
        self.reactive_opacity = self.reactive_val.map([0, 100], [0.3, 1.0])
        self.reactive_rotate = self.reactive_val.map([0, 100], ["rotate(0deg)", "rotate(360deg)"])
        self.splash_ctrl = AnimationController()

    def _on_slider_changed(self, new_value):
        self.slider_ctrl.value = new_value
        self.reactive_val.set(new_value)

    def _trigger_splash(self):
        sequence = [
            # Fall droplet
            [".splash-droplet", {"y": [0, 55], "scaleY": [1.4, 0.6], "opacity": [1, 1]}, {"duration": 0.4, "ease": "easeIn"}],
            # Hide droplet instantly
            [".splash-droplet", {"opacity": [1, 0]}, {"duration": 0.01, "at": 0.4}],
            # Ripple 1 expands and fades
            [".ripple-1", {"scale": [0, 2.5], "opacity": [1, 0]}, {"duration": 0.6, "ease": "easeOut", "at": 0.4}],
            # Ripple 2 expands slightly delayed
            [".ripple-2", {"scale": [0, 1.8], "opacity": [1, 0]}, {"duration": 0.5, "ease": "easeOut", "at": 0.48}],
            # Particle 1 (Left-up)
            [".particle-1", {"x": [0, -22], "y": [0, -25], "scale": [1, 0], "opacity": [1, 0]}, {"duration": 0.5, "ease": "easeOut", "at": 0.4}],
            # Particle 2 (Right-up)
            [".particle-2", {"x": [0, 22], "y": [0, -25], "scale": [1, 0], "opacity": [1, 0]}, {"duration": 0.5, "ease": "easeOut", "at": 0.4}],
            # Particle 3 (Center-high)
            [".particle-3", {"x": [0, 0], "y": [0, -35], "scale": [1.2, 0], "opacity": [1, 0]}, {"duration": 0.5, "ease": "easeOut", "at": 0.4}]
        ]
        self.splash_ctrl.timeline(sequence)

    def _toggle_layout_expand(self):
        self.layout_expanded = not self.layout_expanded
        self.setState()

    def _toggle_shared_element(self):
        self.shared_element_position = 2 if self.shared_element_position == 1 else 1
        self.setState()

    def _toggle_rotate(self):
        self._rotating = not self._rotating
        self.setState()
        QTimer.singleShot(0, self._apply_rotate)

    def _apply_rotate(self):
        if self._rotating:
            self.anim_ctrl.animate(
                {"rotate": [0, 360]},
                {"duration": 1, "ease": Easing.EASE_IN_OUT, "repeat": float("inf")},
                animation_id="rotate_demo",
            )
        else:
            self.anim_ctrl.stop("rotate_demo")

    def _bounce_card(self):
        self.anim_ctrl.animate(
            {"y": [0, -20, 0]},
            {"duration": 0.5, "ease": Easing.EASE_OUT, "bounce": 0.3},
            animation_id="bounce",
        )

    def _fade_out_in(self):
        self.anim_ctrl.animate(
            {"opacity": [1, 0, 1]},
            {"duration": 0.8, "ease": Easing.EASE_IN_OUT},
            animation_id="fade_demo",
        )

    def _arc_card(self):
        opts = AnimationOptions(
            path="arc",
            path_strength=0.5,
            duration=0.5,
            ease=Easing.EASE_IN_OUT,
            repeat=1,
            repeat_type="reverse"
        )
        self.anim_ctrl.animate(
            keyframes={"x": 200, "y": -100},
            options=opts,
            animation_id="arc_demo"
        )

    def build(self) -> Widget:
        return Container(
            key=Key("demo_root"),
            height="100vh",
            width="100vw",
            color=Colors.hex("#1A1A1A"),
            padding=EdgeInsets.all(24),
            child=SingleChildScrollView(
                key=Key("demo_scrollbar"),
                child=Column(
                    key=Key("demo_col"),
                    # crossAxisAlignment=CrossAxisAlignment.START,
                    children=[
                        SizedBox(height=20, key=Key("top_spacer")),
                        Text(
                            "pythra-motion",
                            key=Key("pythra-head"),
                            style=TextStyle(
                                fontSize=32,
                                color=Colors.hex("#FFFFFF"),
                                fontWeight="bold",
                            ),
                        ),
                        SizedBox(height=4, key=Key("pythra-head_sizer"),),
                        Text(
                            "Animation demos powered by motion.dev",
                            key=Key("pythra-sub_head"),
                            style=TextStyle(fontSize=14, color=Colors.hex("#666666")),
                        ),
                        SizedBox(height=32, key=Key("pythra-sub_head_sizer"),),
                        # --- Example 1: Entrance animation ---
                        MotionWidget(
                            key=Key("entrance_demo"),
                            child=Center(key=Key("entrance_card_center"),child=_card(
                                key=Key("entrance_card"),
                                title="Entrance Animation",
                                description="Fades in and slides up on load",
                                child=Container(
                                    key=Key("entrance_card-head_cont"),
                                    height=80,
                                    padding=EdgeInsets.all(20),
                                    color=Colors.hex("#3D5AFE"),
                                    decoration=BoxDecoration(
                                        borderRadius=BorderRadius.all(8),
                                    ),
                                    child=Center(
                                        key=Key("entrance_card-head_cont_cen"),
                                        child=Text(
                                            "I animated in!",
                                            key=Key("entrance_card-head_cont_txt"),
                                            style=TextStyle(
                                                fontSize=16,
                                                color=Colors.hex("#FFFFFF"),
                                            ),
                                        ),
                                    ),
                                ),
                            ),),
                            entrance_animation={"opacity": [0, 1], "y": [40, 0]},
                            entrance_options={"duration": 0.6, "ease": Easing.EASE_OUT},
                        ),
                        SizedBox(height=16, key=Key("entrance_card-head_cont_size"),),
                        # --- Example 2: Hover + Press ---
                        MotionWidget(
                            key=Key("hover_press_demo"),
                            child=Center(key=Key("hover_press_card_center"),child=_card(
                                key=Key("hover_press_card"),
                                title="Hover & Press",
                                description="Hover scales up, press scales down",
                                width="80vw",
                                child=Container(
                                    key=Key("hover_press_card-head_cont"),
                                    height=80,
                                    padding=EdgeInsets.all(20),
                                    color=Colors.hex("#FF6D00"),
                                    decoration=BoxDecoration(
                                        borderRadius=BorderRadius.all(8),
                                    ),
                                    child=Center(
                                        key=Key("hover_press_card-head_cont_cen"),
                                        child=Text(
                                            "Hover over me!",
                                            key=Key("hover_press_card-head_cont_text"),
                                            style=TextStyle(
                                                fontSize=16,
                                                color=Colors.hex("#FFFFFF"),
                                            ),
                                        ),
                                    ),
                                ),
                            ),),
                            hover_animation_enter={"scale": 1.05, "y": -4},
                            hover_animation_leave={"scale": 1, "y": 0},
                            hover_options={"duration": 0.2, "ease": Easing.EASE_OUT},
                            press_animation_start={"scale": 0.95},
                            press_animation_end={"scale": 1},
                            press_options={"duration": 0.15},
                        ),
                        SizedBox(height=16, key=Key("hover_press_card-head_cont_size"),),
                        # --- Example 3: Imperative animation via controller ---
                        _card(
                            key=Key("imperative_card"),
                            title="Imperative Animation",
                            description="Trigger animations programmatically via AnimationController",
                            child=Column(
                                key=Key("imperative_card-head_cont"),
                                children=[
                                    Container(
                                        key=Key("imperative_target"),
                                        height=80,
                                        padding=EdgeInsets.all(25),
                                        decoration=BoxDecoration(
                                            color=Colors.hex("#00C853"),
                                            borderRadius=BorderRadius.all(8),
                                        ),
                                        child=MotionWidget(
                                            key=Key("imperative_motion"),
                                            controller=self.anim_ctrl,
                                            child=Center(
                                                key=Key("imperative_motion_cen"),
                                                child=Text(
                                                    "Tap buttons below",
                                                    key=Key("imperative_motion_text"),
                                                    style=TextStyle(
                                                        fontSize=16,
                                                        color=Colors.hex("#FFFFFF"),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                    SizedBox(height=12, key=Key("imperative_motion_size"),),
                                    Row(
                                        key=Key("imperative_motion_btn_row"),
                                        mainAxisAlignment=MainAxisAlignment.SPACE_EVENLY,
                                        children=[
                                            ElevatedButton(
                                                key=Key("btn_bounce"),
                                                onPressed=self._bounce_card,
                                                child=Text("Bounce"),
                                            ),
                                            ElevatedButton(
                                                key=Key("btn_rotate"),
                                                onPressed=self._toggle_rotate,
                                                child=Text(
                                                    "Stop" if self._rotating else "Spin"
                                                ),
                                            ),
                                            ElevatedButton(
                                                key=Key("btn_fade"),
                                                onPressed=self._fade_out_in,
                                                child=Text("Pulse"),
                                            ),
                                            ElevatedButton(
                                                key=Key("btn_arc"),
                                                onPressed=self._arc_card,
                                                child=Text("Arc"),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        SizedBox(height=16, key=Key("imperative_motion_size"),),
                        # --- Example 4: Scroll-linked reveal ---
                        MotionWidget(
                            key=Key("scroll_reveal"),
                            child=Center(key=Key("scroll_card_cent"),child=_card(
                                key=Key("scroll_card"),
                                title="Scroll Reveal",
                                description="Opacity and position linked to scroll progress",
                                child=Container(
                                    key=Key("scroll_card_cont"),
                                    height=80,
                                    padding=EdgeInsets.all(20),
                                    color=Colors.hex("#7B1FA2"),
                                    decoration=BoxDecoration(
                                        borderRadius=BorderRadius.all(8),
                                    ),
                                    child=Center(
                                        key=Key("scroll_card_cont_cen"),
                                        child=Text(
                                            "Scroll up/down to see me animate",
                                            key=Key("scroll_card_cont_txt"),
                                            style=TextStyle(
                                                fontSize=16,
                                                color=Colors.hex("#FFFFFF"),
                                            ),
                                        ),
                                    ),
                                ),
                            ),),
                            scroll_animation={
                                "opacity": [0, 1, 1, 0],
                                "y": [60, 0, 0, -60],
                            },
                            scroll_options={
                                "offset": ["start end", "end start"],
                                "axis": "y",
                                "animationOptions": {"ease": "linear", "duration": 1},
                            },
                        ),
                        SizedBox(height=16, key=Key("scroll_card_cont_size"),),
                        # --- Example 5: Multiple staggered cards ---
                        _card(
                            key=Key("stagger_header"),
                            title="Stagger (in view)",
                            description="Each card fades in as you scroll down",
                            child=Column(
                                key=Key("stagger_header_col"),
                                children=[
                                    Row(
                                        key=Key("stagger_row_row"),
                                        mainAxisAlignment=MainAxisAlignment.SPACE_EVENLY,
                                        children=[
                                            _stagger_item(i, color)
                                            for i, color in enumerate(
                                                ["#E53935", "#FB8C00", "#43A047"]
                                            )
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        SizedBox(height=16, key=Key("stagger_row_size_svg"),),
                        # --- Example 6: SVG Animation & Morphing ---
                        _card(
                            key=Key("svg_demo_card"),
                            title="SVG Path Drawing & Morphing",
                            description="Animate SVG pathLength (drawing) and path shape morphing on hover",
                            child=Row(
                                key=Key("svg_row"),
                                mainAxisAlignment=MainAxisAlignment.SPACE_EVENLY,
                                children=[
                                    # SVG Line Drawing
                                    Column(
                                        key=Key("svg_col_draw"),
                                        children=[
                                            Text(
                                                "Line Drawing (Mount)",
                                                key=Key("svg_txt_draw"),
                                                style=TextStyle(fontSize=12, color=Colors.hex("#999999")),
                                            ),
                                            SizedBox(height=8, key=Key("svg_spacer_draw")),
                                            MotionWidget(
                                                key=Key("svg_draw_demo"),
                                                child=Svg(
                                                    key=Key("svg_draw_canvas"),
                                                    width=100,
                                                    height=100,
                                                    viewBox="0 0 100 100",
                                                    children=[
                                                        SvgPath(
                                                            key=Key("svg_path_draw"),
                                                            d="M 10 80 Q 52.5 10 95 80",
                                                            fill="none",
                                                            stroke="#00C853",
                                                            strokeWidth=4,
                                                        )
                                                    ]
                                                ),
                                                in_view_animation={"pathLength": [0, 1]},
                                                in_view_options={
                                                    "once": True,
                                                    "amount": 0.1,
                                                    "animationOptions": {"selector": "path", "duration": 1.5, "ease": "easeInOut"},
                                                },
                                            ),
                                        ],
                                    ),
                                    # SVG Path Morphing
                                    Column(
                                        key=Key("svg_col_morph"),
                                        children=[
                                            Text(
                                                "Morph Shape (Hover)",
                                                key=Key("svg_txt_morph"),
                                                style=TextStyle(fontSize=12, color=Colors.hex("#999999")),
                                            ),
                                            SizedBox(height=8, key=Key("svg_spacer_morph")),
                                            MotionWidget(
                                                key=Key("svg_morph_demo"),
                                                child=Svg(
                                                    key=Key("svg_morph_canvas"),
                                                    width=100,
                                                    height=100,
                                                    viewBox="0 0 100 100",
                                                    children=[
                                                        SvgPath(
                                                            key=Key("svg_path_morph"),
                                                            d="M 20 20 L 80 20 L 80 80 L 20 80 Z", # Rectangle
                                                            fill="#FF6D00",
                                                        )
                                                    ]
                                                ),
                                                hover_animation_enter={"d": "M 50 10 L 90 90 L 10 90 Z"}, # Triangle
                                                hover_animation_leave={"d": "M 20 20 L 80 20 L 80 80 L 20 80 Z"}, # Rectangle
                                                hover_options={"selector": "path", "duration": 0.5, "ease": "easeInOut"},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        SizedBox(height=16, key=Key("stagger_row_size_svg"),),
                        # --- Example 7: Layout Animation (FLIP) ---
                        _card(
                            key=Key("flip_layout_card"),
                            title="Automatic Layout Transitions (FLIP)",
                            description="Surrounding elements adjust smoothly when size or height changes",
                            child=Column(
                                key=Key("flip_col"),
                                children=[
                                    ElevatedButton(
                                        key=Key("flip_toggle_btn"),
                                        child=Text("Toggle Card Size", key=Key("flip_btn_txt")),
                                        onPressed=self._toggle_layout_expand,
                                    ),
                                    SizedBox(height=16, key=Key("flip_spacer")),
                                    MotionWidget(
                                        key=Key("flip_target_box"),
                                        layout=True,
                                        child=Container(
                                            key=Key("flip_content_box"),
                                            width=300 if self.layout_expanded else 150,
                                            height=120 if self.layout_expanded else 60,
                                            color="#6200EE",
                                            child=Center(
                                                key=Key("flip_center"),
                                                child=Text(
                                                    "Click button above!" if not self.layout_expanded else "Buttery Smooth FLIP!",
                                                    key=Key("flip_txt"),
                                                    style=TextStyle(color=Colors.white, fontSize=14),
                                                ),
                                            ),
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        SizedBox(height=16, key=Key("stagger_row_size_layout"),),
                        # --- Example 8: Shared Element Transitions (layoutId) ---
                        _card(
                            key=Key("shared_element_card"),
                            title="Shared Element Transitions (layoutId)",
                            description="Animate elements seamlessly moving between different container/layout trees",
                            child=Column(
                                key=Key("shared_element_col"),
                                children=[
                                    ElevatedButton(
                                        key=Key("shared_toggle_btn"),
                                        child=Text("Swap Card Container", key=Key("shared_btn_txt")),
                                        onPressed=self._toggle_shared_element,
                                    ),
                                    SizedBox(height=16, key=Key("shared_spacer")),
                                    Row(
                                        key=Key("shared_row"),
                                        mainAxisAlignment=MainAxisAlignment.SPACE_EVENLY,
                                        children=[
                                            # Left Container
                                            Container(
                                                key=Key("shared_container_left"),
                                                width=160,
                                                height=100,
                                                color="#222222",
                                                child=Center(
                                                    key=Key("shared_left_center"),
                                                    child=MotionWidget(
                                                        key=Key("shared_element_left"),
                                                        layout_id="shared_card_element",
                                                        child=Container(
                                                            key=Key("shared_card_left_content"),
                                                            width=120,
                                                            height=60,
                                                            color="#03DAC6",
                                                            child=Center(
                                                                key=Key("shared_card_left_center"),
                                                                child=Text("Shared Card", key=Key("shared_card_left_txt"), style=TextStyle(color=Colors.black)),
                                                            ),
                                                        ) if self.shared_element_position == 1 else Container(width=0, height=0, key=Key("shared_left_empty")),
                                                    ),
                                                ),
                                            ),
                                            # Right Container
                                            Container(
                                                key=Key("shared_container_right"),
                                                width=160,
                                                height=100,
                                                color="#222222",
                                                child=Center(
                                                    key=Key("shared_right_center"),
                                                    child=MotionWidget(
                                                        key=Key("shared_element_right"),
                                                        layout_id="shared_card_element",
                                                        child=Container(
                                                            key=Key("shared_card_right_content"),
                                                            width=120,
                                                            height=60,
                                                            color="#03DAC6",
                                                            child=Center(
                                                                key=Key("shared_right_card_center"),
                                                                child=Text("Shared Card", key=Key("shared_card_right_txt"), style=TextStyle(color=Colors.black)),
                                                            ),
                                                        ) if self.shared_element_position == 2 else Container(width=0, height=0, key=Key("shared_right_empty")),
                                                    ),
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        SizedBox(height=16, key=Key("stagger_row_size_layout_reactive"),),
                        # --- Example 9: Reactive Motion Values ---
                        _card(
                            key=Key("reactive_values_card"),
                            title="Reactive Motion Values",
                            description="Slide to directly drive scale and rotation in the browser (zero-latency)",
                            child=Column(
                                key=Key("reactive_col"),
                                children=[
                                    Slider(
                                        key=Key("reactive_slider"),
                                        controller=self.slider_ctrl,
                                        onChanged=self._on_slider_changed,
                                        min=0.0,
                                        max=100.0,
                                    ),
                                    SizedBox(height=24, key=Key("reactive_spacer")),
                                    MotionWidget(
                                        key=Key("reactive_target"),
                                        child=Container(
                                            key=Key("reactive_box"),
                                            width=100,
                                            height=100,
                                            color="#BB86FC",
                                            style={
                                                "opacity": self.reactive_opacity,
                                                "transform": self.reactive_rotate,
                                            },
                                            child=Center(
                                                key=Key("reactive_center"),
                                                child=Text(
                                                    "Interactive",
                                                    key=Key("reactive_txt"),
                                                    style=TextStyle(color=Colors.black, fontSize=12, fontWeight="bold"),
                                                ),
                                            ),
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        SizedBox(height=16, key=Key("stagger_row_size_reactive_splash"),),
                        # --- Example 10: Droplet Splash ---
                        _card(
                            key=Key("splash_animation_card"),
                            title="Coordinated Droplet Splash Timeline",
                            description="Uses timeline sequences to coordinate a falling droplet, expanding ripples, and radial particles.",
                            child=Column(
                                key=Key("splash_col"),
                                children=[
                                    ElevatedButton(
                                        key=Key("splash_btn"),
                                        onPressed=self._trigger_splash,
                                        child=Text("Release Droplet", key=Key("splash_btn_txt")),
                                    ),
                                    SizedBox(height=24, key=Key("splash_spacer")),
                                    MotionWidget(
                                        key=Key("splash_canvas"),
                                        controller=self.splash_ctrl,
                                        child=Container(
                                            key=Key("splash_canvas_container"),
                                            width=160,
                                            height=160,
                                            decoration=BoxDecoration(
                                                color=Colors.hex("#121212"),
                                                borderRadius=BorderRadius.all(12),
                                                border=Border.all(color=Colors.hex("#333"), width=1),
                                            ),
                                            style={
                                                "position": "relative",
                                                "overflow": "hidden",
                                            },
                                            child=Stack(
                                                key=Key("splash_stack"),
                                                children=[
                                                    # Platform line
                                                    Positioned(
                                                        key=Key("splash_line"),
                                                        top=110,
                                                        left=20,
                                                        right=20,
                                                        height=2,
                                                        child=Container(
                                                            key=Key("splash_line_box"),
                                                            color="#333",
                                                        ),
                                                    ),
                                                    # Ripple 1
                                                    Positioned(
                                                        key=Key("splash_ripple_1_pos"),
                                                        left=70,
                                                        top=100,
                                                        width=20,
                                                        height=20,
                                                        child=Container(
                                                            key=Key("splash_ripple_1"),
                                                            css_class="ripple-1",
                                                            decoration=BoxDecoration(
                                                                borderRadius=BorderRadius.all(10),
                                                                border=Border.all(color=Colors.hex("#03DAC6"), width=2),
                                                            ),
                                                            style={
                                                                "opacity": "0",
                                                                "transform-origin": "center",
                                                            },
                                                        ),
                                                    ),
                                                    # Ripple 2
                                                    Positioned(
                                                        key=Key("splash_ripple_2_pos"),
                                                        left=70,
                                                        top=100,
                                                        width=20,
                                                        height=20,
                                                        child=Container(
                                                            key=Key("splash_ripple_2"),
                                                            css_class="ripple-2",
                                                            decoration=BoxDecoration(
                                                                borderRadius=BorderRadius.all(10),
                                                                border=Border.all(color=Colors.hex("#BB86FC"), width=1.5),
                                                            ),
                                                            style={
                                                                "opacity": "0",
                                                                "transform-origin": "center",
                                                            },
                                                        ),
                                                    ),
                                                    # Particle 1 (Left-up)
                                                    Positioned(
                                                        key=Key("splash_part_1_pos"),
                                                        left=78,
                                                        top=108,
                                                        width=4,
                                                        height=4,
                                                        child=Container(
                                                            key=Key("splash_part_1"),
                                                            css_class="particle-1",
                                                            decoration=BoxDecoration(
                                                                color=Colors.hex("#03DAC6"),
                                                                borderRadius=BorderRadius.all(2),
                                                            ),
                                                            style={
                                                                "opacity": "0",
                                                                "transform-origin": "center",
                                                            },
                                                        ),
                                                    ),
                                                    # Particle 2 (Right-up)
                                                    Positioned(
                                                        key=Key("splash_part_2_pos"),
                                                        left=78,
                                                        top=108,
                                                        width=4,
                                                        height=4,
                                                        child=Container(
                                                            key=Key("splash_part_2"),
                                                            css_class="particle-2",
                                                            decoration=BoxDecoration(
                                                                color=Colors.hex("#03DAC6"),
                                                                borderRadius=BorderRadius.all(2),
                                                            ),
                                                            style={
                                                                "opacity": "0",
                                                                "transform-origin": "center",
                                                            },
                                                        ),
                                                    ),
                                                    # Particle 3 (Center-high)
                                                    Positioned(
                                                        key=Key("splash_part_3_pos"),
                                                        left=78,
                                                        top=108,
                                                        width=4,
                                                        height=4,
                                                        child=Container(
                                                            key=Key("splash_part_3"),
                                                            css_class="particle-3",
                                                            decoration=BoxDecoration(
                                                                color=Colors.hex("#BB86FC"),
                                                                borderRadius=BorderRadius.all(2),
                                                            ),
                                                            style={
                                                                "opacity": "0",
                                                                "transform-origin": "center",
                                                            },
                                                        ),
                                                    ),
                                                    # Falling Droplet
                                                    Positioned(
                                                        key=Key("splash_droplet_pos"),
                                                        left=76,
                                                        top=20,
                                                        width=8,
                                                        height=8,
                                                        child=Container(
                                                            key=Key("splash_droplet_circle"),
                                                            css_class="splash-droplet",
                                                            decoration=BoxDecoration(
                                                                color=Colors.hex("#BB86FC"),
                                                                borderRadius=BorderRadius.all(4),
                                                            ),
                                                            style={
                                                                "opacity": "0",
                                                                "transform-origin": "center",
                                                            },
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        SizedBox(height=60, key=Key("stagger_row_size"),),
                    ],
                ),
            ),
        )


def _stagger_item(index: int, color: str) -> Widget:
    return MotionWidget(
        key=Key(f"stagger_item_{index}"),
        child=Container(
            key=Key(f"stagger_box_{index}"),
            width=80,
            height=80,
            decoration=BoxDecoration(
                color=Colors.hex(color),
                borderRadius=BorderRadius.all(12),
            ),
            child=Center(
                key=Key(f"stagger_box_{index}_cen"),
                child=Text(
                    str(index + 1),
                    key=Key(f"stagger_box_{index}_txt"),
                    style=TextStyle(
                        fontSize=24, color=Colors.hex("#FFFFFF"), fontWeight="bold"
                    ),
                ),
            ),
        ),
        in_view_animation={"opacity": [0, 1], "y": [20, 0], "scale": [0.8, 1]},
        in_view_options={
            "animationOptions": {
                "duration": 0.4,
                "ease": Easing.EASE_OUT,
                "delay": 0.1 * index,
            },
        },
    )


class DemoPage(StatefulWidget):
    def createState(self) -> DemoPageState:
        return DemoPageState()


class MainState(State):
    def __init__(self):
        self.demo = DemoPage(key=Key("demo_page"))

    def on_copy(self):
        print("[CONTEXT MENU] copy")

    def on_paste(self):
        print("[CONTEXT MENU] paste")

    def on_delete(self):
        print("[CONTEXT MENU] delete")

    def build(self):
        return ContextMenu(
            items=[
                MenuItem(
                    "Copy", icon=Icons.content_copy_rounded, onPressed=self.on_copy
                ),
                MenuItem(
                    "Paste", icon=Icons.content_paste_rounded, onPressed=self.on_paste
                ),
                MenuItem(divider=True),
                MenuItem(
                    "Delete",
                    icon=Icons.delete_outline_rounded,
                    onPressed=self.on_delete,
                ),
            ],
            child=self.demo,
            theme=ContextMenuTheme(
                backgroundColor=Colors.surface,
                borderColor=Colors.outline,
                itemTextColor=Colors.onSurface,
                itemHoverColor=Colors.primary,
                iconSize=20,
                borderRadius=BorderRadius.all(8),
                elevation=8,
            ),
        )


@runApp
class Main(StatefulWidget):
    def __init__(self, key=Key("app_root")):
        super().__init__(key=key)

    def createState(self) -> MainState:
        return MainState()


if __name__ == "__main__":
    app = Framework.instance()
    app.set_root(DemoPage(key=Key("demo_page")))
    app.run()
