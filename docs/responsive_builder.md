# ResponsiveBuilder: Adaptive Layouts in PyThra

The `ResponsiveBuilder` is a powerful layout widget in the PyThra toolkit that enables dynamic, adaptive user interfaces. It listens to window resize events and rebuilds its child widget tree with the latest dimensions, allowing your application to respond seamlessly to screen size changes.

## When to Use It

Use `ResponsiveBuilder` whenever you need your UI to fundamentally change its layout or component structure based on the available screen space. 

**Typical Use Cases:**
- Switching between a sidebar layout (desktop) and a bottom navigation bar (mobile/small screen).
- Changing the number of columns in a grid based on window width.
- Hiding or showing supplementary panels when the window is resized.
- Adjusting component sizes or rendering entirely different widgets for specific breakpoint sizes.

> [!TIP]
> **CSS vs. ResponsiveBuilder**
> If you only need to change styles (like widths, colors, or CSS grid gaps), use standard CSS properties or media queries. Use `ResponsiveBuilder` when the **widget tree itself needs to change**—for example, replacing a `Row` with a `Column`, or mounting a completely different set of components.

## How to Use It

The `ResponsiveBuilder` takes a single argument: a `builder` function. This function receives the current `width` and `height` of the window and must return a PyThra `Widget`.

### Basic Example

```python
from pythra import ResponsiveBuilder, Text, Column, Colors
from pythra.styles import TextStyle

def my_responsive_layout(width, height):
    # Define breakpoints
    if width > 800:
        return Text(f"Desktop View: {width}x{height}", style=TextStyle(color=Colors.blue))
    else:
        return Text(f"Mobile View: {width}x{height}", style=TextStyle(color=Colors.red))

# Use it in your UI tree
ResponsiveBuilder(
    key=Key("my_responsive_section"),
    builder=my_responsive_layout
)
```

### Inline Lambda Example

For simple changes, you can use an inline lambda function:

```python
ResponsiveBuilder(
    key=Key("video_container"),
    builder=lambda w, h: Column(
        children=[
            Text(f"Current Size: {w} x {h}"),
            VideoPlayer(
                key=Key("main_video"),
                video_path="/path/to/video.mp4"
            )
        ]
    )
)
```

## Architecture and Core Engine Integration

The `ResponsiveBuilder` is built as a `StatefulWidget` to hook directly into PyThra's reactive state engine and component lifecycle. Here is how it works under the hood:

### 1. Initialization and Event Listening
When a `ResponsiveBuilder` is mounted, its `ResponsiveBuilderState` is created. During `initState()`, the state retrieves the current window dimensions from the `Framework` singleton and registers a resize listener (`framework.register_resize_listener`).

The `Framework` itself receives continuous resize events from the client-side JavaScript (typically via a `ResizeObserver` or window `resize` event) over the WebSockets bridge.

### 2. Debouncing and Performance
Handling resize events on every pixel change can cause severe performance degradation. To prevent this, `ResponsiveBuilderState` implements a **100ms debounce** using PySide6's `QTimer`. 

When the user drags the window to resize it:
- The framework fires resize events rapidly.
- `ResponsiveBuilderState._on_resize` captures the time of the event.
- It schedules a check 100ms later.
- If 100ms have passed without another resize event, it checks if the dimensions have actually changed. If they have, it calls `self.setState()`.

### 3. Reconciliation and Rendering
When `setState()` is called, PyThra schedules an update for the `ResponsiveBuilder`:
- The framework calls `ResponsiveBuilderState.build()`.
- The state invokes your `builder(width, height)` function, generating a brand new widget tree for that section.
- PyThra's **Reconciler** diffs this new widget tree against the previous one.
- Rather than destroying the whole UI, the Reconciler smartly calculates the exact changes (e.g., updating text, moving elements, or swapping a Row for a Column) and generates minimal DOM patches.
- These patches are sent across the WebSocket bridge to update the live browser DOM instantly.

> [!IMPORTANT]  
> **Widget Keys and Re-renders**
> Because `ResponsiveBuilder` frequently rebuilds its children during resizing, **always assign stable `Key` objects** to stateful children inside your builder function. 
> 
> If you have a state-heavy widget (like a `VideoPlayer`, `VirtualList`, or `TextField`) inside the builder, giving it a stable key ensures PyThra's reconciler reuses its existing state instead of destroying and recreating it on every resize.

## Best Practices

1. **Keep Builders Pure**: Your builder function should only construct widgets. Do not mutate global application state or trigger side effects inside the builder function.
2. **Stable Keys**: Always use explicit `Key("my_widget")` assignments for nested widgets to ensure the Reconciler correctly maps them across layout shifts.
3. **Avoid Deep Nesting**: If you have a massively complex UI, try to place `ResponsiveBuilder` as close to the target changing elements as possible, rather than wrapping your entire application in a single `ResponsiveBuilder`. This localizes the rebuilds and improves performance.
