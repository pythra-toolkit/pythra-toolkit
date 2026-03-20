# Widget Library
Relevant source files
- [src/pythra/pythra/__pycache__/__init__.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/__init__.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/base.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/base.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/core.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/core.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/styles.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/styles.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/widgets.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/widgets.cpython-312.pyc)
- [src/pythra/pythra/core.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py)
- [src/pythra/pythra/project_template/render/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/dropdown.js)
- [src/pythra/pythra/project_template/render/js/pythra_bridge.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js)
- [src/pythra/pythra/render_template/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/dropdown.js)
- [src/pythra/pythra/styles.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py)
- [src/pythra/pythra/widgets.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py)
- [src/pythra/pythra/widgets_more.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py)

The PyThra Widget Library is a collection of declarative "LEGO blocks" used to construct user interfaces. Every visual element in a PyThra application—from a simple line of text to complex scrolling grids—is a `Widget`[src/pythra/pythra/widgets.py8-16](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L8-L16) These widgets are translated into HTML/CSS by the reconciler and rendered within a high-performance webview.

## Widget Structure and Lifecycle

All widgets inherit from the base `Widget` class [src/pythra/pythra/base.py107-111](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L107-L111) They are designed to be immutable configurations that the framework uses to build the actual DOM tree.

### Core Mechanisms

- **`render_props()`**: Every widget must define how its Python properties (like colors, sizes, or alignment) map to HTML attributes and inline styles [src/pythra/pythra/widgets_more.py172-183](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L172-L183)
- **`get_children()`**: Defines the hierarchy by returning a list of nested widgets [src/pythra/pythra/base.py186-191](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L186-L191)
- **`generate_css_rule()`**: To optimize performance, PyThra uses a **Shared Styles** system. Instead of repeating identical CSS for every instance of a widget, the framework generates a single CSS class for widgets with identical style properties [src/pythra/pythra/widgets.py221-235](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L221-L235)
- **`style_key`**: A hashable representation of a widget's visual properties used by the reconciler to determine if a CSS update is necessary [src/pythra/pythra/widgets.py194-215](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L194-L215)

### From Python to Browser DOM

The following diagram illustrates how a Python Widget definition is transformed into a rendered element in the browser.

**Widget Rendering Pipeline**

```
Browser (JS Engine Space)

Reconciler (Core Architecture)

Python (Code Entity Space)

render_props()

style_key

Lookup

generate_css_rule()

applyPatches()

Link

class='shared-container-hash'

Widget Instance (e.g., Container)

Props Dict

Style Hash

shared_styles Registry

Patch Generation

styles.css

DOM Element

CSS Object Model
```

Sources: [src/pythra/pythra/widgets.py139-235](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L139-L235)[src/pythra/pythra/reconciler.py7-36](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L7-L36)[src/pythra/pythra/base.py107-130](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L107-L130)

---

## Widget Categories

PyThra organizes widgets into specialized categories to balance ease of use with powerful layout capabilities.

### 1. Layout Widgets

These widgets arrange other widgets in space. They handle alignment, spacing, and sizing constraints.

- **Primary Widgets**: `Container`, `Column`, `Row`, `Stack`, `Expanded`, `SizedBox`.
- **Concepts**: Main-axis vs. Cross-axis alignment, `EdgeInsets` for padding/margins, and `BoxConstraints`.

For details, see [Layout Widgets](/pythra-toolkit/pythra-toolkit/3.1-layout-widgets).

### 2. Material Design Components

High-level structural widgets that follow Material 3 guidelines. These provide the "skeleton" of a modern application.

- **Primary Widgets**: `Scaffold`, `AppBar`, `Drawer`, `FloatingActionButton`, `Card`, `ListTile`.
- **Concepts**: M3 color roles, elevation, and modal behavior.

For details, see [Material Design Components](/pythra-toolkit/pythra-toolkit/3.2-material-design-components).

### 3. Interactive and Input Widgets

Widgets that capture user input or respond to gestures. Many of these utilize a dedicated JavaScript "Engine" for high-fidelity interaction.

- **Primary Widgets**: `TextField`, `Button`, `PythraSlider`, `PythraDropdown`, `GestureDetector`.
- **Concepts**: Controllers (e.g., `TextEditingController`), event callbacks (`onChanged`, `onPressed`), and the Python-JS bridge.

For details, see [Interactive and Input Widgets](/pythra-toolkit/pythra-toolkit/3.3-interactive-and-input-widgets).

### 4. Display and Collection Widgets

Used for showing content or managing large lists of data efficiently.

- **Primary Widgets**: `Text`, `Icon`, `Image`, `ListView`, `GridView`, `ProgressIndicator`.
- **Concepts**: List virtualization (rendering only visible items) and asset management.

For details, see [Display and Collection Widgets](/pythra-toolkit/pythra-toolkit/3.4-display-and-collection-widgets).

---

## The Widget-Engine Relationship

Interactive widgets in PyThra often consist of a Python class and a corresponding JavaScript class. The Python class defines the state and properties, while the JS class handles immediate UI feedback (like dragging a slider or opening a dropdown menu) before syncing back to Python.

**Interactive Widget Synchronization**

```
JS Space

Python Space

js_init props

new PythraDropdown()

on_input_changed

setState()

PythraDropdown (Widget)

DropdownController

PythraDropdown (JS Engine)

pythra_bridge.js
```

Sources: [src/pythra/pythra/project_template/render/js/dropdown.js7-42](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/dropdown.js#L7-L42)[src/pythra/pythra/widgets.py183-211](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L183-L211)[src/pythra/pythra/core.py180-189](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L180-L189)

## Shared Styles Optimization

PyThra minimizes the size of the generated HTML by moving styles into a shared CSS registry.
FeatureDescriptionFile Reference**Style Hashing**Uses `make_hashable` to create a unique key based on all style-related props.[src/pythra/pythra/base.py53-87](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L53-L87)**Class Injection**The Reconciler injects generated CSS rules into the `index.html` head dynamically.[src/pythra/pythra/reconciler.py57-61](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L57-L61)**CSS Re-use**Multiple widgets with the same `style_key` share the same CSS class.[src/pythra/pythra/widgets.py139-140](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L139-L140)
Sources: [src/pythra/pythra/widgets.py139-235](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L139-L235)[src/pythra/pythra/styles.py17-25](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L17-L25)[src/pythra/pythra/base.py53-87](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L53-L87)