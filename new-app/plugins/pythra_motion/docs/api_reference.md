# PyThra Motion Plugin API Reference

The `pythra_motion` plugin exposes a comprehensive physics-based animation system for PyThra using [Motion.dev](https://motion.dev) as its client-side engine.

---

## 1. MotionWidget (`widget.py`)

A stateful wrapper widget that adds layout transitions, gesture/state states (hover, press), and page scroll/in-view bindings to any child widget.

### Constructor
```python
MotionWidget(
    key: Key,
    child: Widget,
    controller: Optional[AnimationController] = None,
    entrance_animation: Optional[Keyframes] = None,
    entrance_options: Optional[dict] = None,
    scroll_animation: Optional[Keyframes] = None,
    scroll_options: Optional[dict] = None,
    in_view_animation: Optional[Keyframes] = None,
    in_view_options: Optional[dict] = None,
    hover_animation_enter: Optional[Keyframes] = None,
    hover_animation_leave: Optional[Keyframes] = None,
    hover_options: Optional[dict] = None,
    press_animation_start: Optional[Keyframes] = None,
    press_animation_end: Optional[Keyframes] = None,
    press_options: Optional[dict] = None,
    timeline: Optional[list] = None,
    layout: bool = False,
    layout_id: Optional[str] = None,
)
```

### Parameters
* **`key`**: (Required) A unique `Key` used to track the widget during incremental UI reconciliations.
* **`child`**: (Required) The target child widget which will be animated.
* **`controller`**: An optional `AnimationController` instance for triggering imperative animations or managing timeline controls.
* **`entrance_animation`**: A dictionary containing initial animation property values (e.g. `{"opacity": [0, 1]}`).
* **`entrance_options`**: Configuration dictionary or `AnimationOptions` instance guiding the entrance animation.
* **`scroll_animation`**: A dictionary binding animation progress to the page scroll offset.
* **`scroll_options`**: Configuration options for the scroll-linked animations. See `ScrollOptions` for fields.
* **`in_view_animation`**: Keyframe parameters triggered when the element becomes visible in the viewport.
* **`in_view_options`**: Configuration options for in-view animations. See `InViewOptions` for fields.
* **`hover_animation_enter`**: Keyframes applied when the user's cursor hovers over the element.
* **`hover_animation_leave`**: Keyframes applied when the user's cursor leaves the element.
* **`hover_options`**: Hover state animation settings.
* **`press_animation_start`**: Keyframes applied when the user clicks or presses the element.
* **`press_animation_end`**: Keyframes applied when the user releases their click/press.
* **`press_options`**: Press animation configurations.
* **`timeline`**: A sequence of animations run sequentially upon mounting.
* **`layout`**: Set to `True` to enable automatic layout shift transitions (using the FLIP technique).
* **`layout_id`**: A string enabling shared element layout transitions moving seamlessly between different parent widget trees.

---

## 2. AnimationController (`controller.py`)

Provides control hooks to trigger animations programmatically, manage complex timelines, and handle multi-property staggers.

### Methods
* **`animate(keyframes: Keyframes, options: Optional[dict] = None, animation_id: Optional[str] = None) -> Optional[str]`**
  Imperatively triggers an animation target using keyframe properties. Returns the generated animation ID string.
* **`scroll_animate(keyframes: Keyframes, scroll_options: Optional[dict] = None)`**
  Sets up scroll-bound property tracks dynamically.
* **`in_view_animate(keyframes: Keyframes, view_options: Optional[dict] = None)`**
  Binds in-view animations on elements imperatively.
* **`play(animation_id: str)`**
  Resumes execution of an active animation.
* **`pause(animation_id: str)`**
  Pauses the current animation at its current frame.
* **`stop(animation_id: str)`**
  Terminates execution of the target animation.
* **`reverse(animation_id: str)`**
  Plays the animation backward from its current state.
* **`set_speed(animation_id: str, speed: float)`**
  Alters the playback speed factor (e.g. `2.0` for double speed).
* **`set_time(animation_id: str, time: float)`**
  Scrubs the animation to a specific timeline time point (in seconds).
* **`timeline(sequence: list, default_options: Optional[dict] = None) -> Optional[str]`**
  Executes a sequential or overlapping list of animations. Returns the timeline ID.
* **`stagger_children(selector: str, keyframes: Keyframes, options: Optional[dict] = None)`**
  Triggers a staggered animation on all elements matching the CSS sub-selector relative to the container.
* **`destroy()`**
  Disposes all active controllers and listeners.

---

## 3. Easing & Spring presets (`easing.py`)

A set of static timing and preset properties wrapping Motion.dev's transition helpers.

### Easing Presets
* `LINEAR`
* `EASE_IN`, `EASE_OUT`, `EASE_IN_OUT`
* `CIRC_IN`, `CIRC_OUT`, `CIRC_IN_OUT`
* `BACK_IN`, `BACK_OUT`, `BACK_IN_OUT`
* `ANTICIPATE`

### Easing Methods
* **`cubic_bezier(x1: float, y1: float, x2: float, y2: float) -> List[float]`**: Generates custom cubic-bezier curves.
* **`steps(count: int, position: str = "start") -> dict`**: Creates step-based discrete easing paths.

### Spring Configurations (`SpringPreset`)
* `GENTLE`: `{"stiffness": 120, "damping": 14}`
* `WOBBLY`: `{"stiffness": 180, "damping": 12}`
* `STIFF`: `{"stiffness": 300, "damping": 20}`
* `SLOW`: `{"stiffness": 80, "damping": 20}`
* `BOUNCY`: `{"bounce": 0.4, "visual_duration": 0.5}`
* `SNAPPY`: `{"bounce": 0.1, "visual_duration": 0.3}`

---

## 4. Animation Option Configs (`types.py`)

Structured metadata classes passed to configure timing, repeating, target selectors, and spring physics.

### AnimationOptions
```python
@dataclass
class AnimationOptions:
    type: str = "tween"
    duration: float = 0.3
    delay: float = 0.0
    ease: Any = "easeOut"
    repeat: int = 0
    repeat_type: str = "loop"
    repeat_delay: float = 0.0
    direction: Optional[str] = None
    end_delay: Optional[float] = None
    bounce: Optional[float] = None
    stiffness: Optional[float] = None
    damping: Optional[float] = None
    mass: Optional[float] = None
    velocity: Optional[float] = None
    visual_duration: Optional[float] = None
    
    # Path coordinates (e.g. easing: arc)
    path: Optional[str] = None
    path_strength: Optional[float] = None
    path_peak: Optional[float] = None
    path_direction: Optional[str] = None
    path_rotate: Optional[bool] = None
    
    # WAAPI Target selector
    selector: Optional[str] = None
```

### ScrollOptions
```python
@dataclass
class ScrollOptions:
    target_selector: Optional[str] = None
    axis: str = "y"
    offset: List[str] = field(default_factory=lambda: ["start end", "end start"])
    container_selector: Optional[str] = None
    margin: str = "0px"
    amount: Union[float, str] = 0.1
```

### InViewOptions
```python
@dataclass
class InViewOptions:
    once: bool = True
    margin: str = "0px"
    amount: Union[float, str] = 0.1
    container_selector: Optional[str] = None
```

### TimelineStep
Represents a single step in a timeline sequence.
```python
@dataclass
class TimelineStep:
    target: Optional[str] = None
    keyframes: Optional[dict] = None
    options: Optional[dict] = None
    at: Optional[float] = None
```

---

## 5. Reactive Motion Values (`values.py`)

Allows storing values and creating live style bindings directly in the browser DOM, bypassing the Python bridge overhead for high-frequency interactive updates (e.g. from sliders or scrolling).

### `MotionValue`
* **`__init__(initial_value: float = 0.0)`**: Creates a new motion value holding the initial state.
* **`set(value: float)`**: Asynchronously updates the value directly inside QWebEngineView.
* **`map(input_range: List[float], output_range: List[Union[float, str]]) -> TransformValue`**: Returns a mapped `TransformValue` mapped linearly.

### `TransformValue`
Represents a mapped transform value derived from a parent `MotionValue` using `window.Motion.interpolate`.

---

## 6. SVG Widgets (`svg.py`)

Vectors graphics classes that compile to valid SVG elements within the reconciliation loop.

* **`Svg`**: Canvas root mapping to an `<svg>` element.
  * **`children`**: List of child shape widgets.
  * **`width`, `height`**: SVG canvas dimensions.
  * **`viewBox`**: SVG coordinate view boundary.
* **`SvgPath`**: Renders as a `<path>` element.
  * **`d`**: Path geometry coordinate string.
  * **`fill`, `stroke`, `strokeWidth`, `strokeDasharray`, `strokeDashoffset`**: Path styling options.
* **`SvgCircle`**: Renders as a `<circle>` element.
  * **`cx`, `cy`**: Center coordinates.
  * **`r`**: Circle radius.
* **`SvgRect`**: Renders as a `<rect>` element.
  * **`x`, `y`, `width`, `height`, `rx`, `ry`**: Rectangle position, dimension, and rounding.
* **`SvgLine`**: Renders as a `<line>` element.
  * **`x1`, `y1`, `x2`, `y2`**: Starting and ending coordinates.
* **`SvgGroup`**: Renders as a `<g>` group container element.

---

## 7. Spring Solver (`spring.py`)

A synchronous solver bridge allowing python code to query calculated motion value points directly.

* **`solve_spring(keyframes, stiffness, damping, mass, velocity, time_ms, window_id) -> Union[float, List[float]]`**
  Synchronously evaluates the spring equation at the given time (in milliseconds) and returns the corresponding value point.
* **`solve_spring_details(keyframes, stiffness, damping, mass, velocity, times_ms, window_id) -> dict`**
  Returns calculated spring progress coordinates along with the overall visual animation duration.
