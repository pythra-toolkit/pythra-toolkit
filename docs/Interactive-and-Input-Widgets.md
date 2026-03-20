# Interactive and Input Widgets
Relevant source files
- [src/pythra/pythra/derived_widgets/dropdown/controller.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/controller.py)
- [src/pythra/pythra/derived_widgets/dropdown/dropdown.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/dropdown.py)
- [src/pythra/pythra/derived_widgets/dropdown/style.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/style.py)
- [src/pythra/pythra/navigation.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py)
- [src/pythra/pythra/project_template/render/js/slider.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/slider.js)
- [src/pythra/pythra/project_template/render/js/textfield.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/textfield.js)
- [src/pythra/pythra/render_template/js/slider.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/slider.js)
- [src/pythra/pythra/render_template/js/textfield.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/textfield.js)
- [textfield_and_widgets_report.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/textfield_and_widgets_report.md)

Interactive widgets in PyThra facilitate user input and event handling by bridging Python-defined state logic with browser-side DOM events. This section documents the core input components, their controllers, and the JavaScript engines that handle high-frequency interactions like dragging and text input.

### Interaction Architecture

PyThra uses a hybrid approach for interactivity:

1. **Low-latency feedback**: Handled by JavaScript engines (e.g., `PythraSlider`, `PythraTextField`) to ensure smooth UI updates (like slider thumb movement) without waiting for a Python round-trip.
2. **State Synchronization**: Significant events (e.g., `onChanged`, `onPressed`) are serialized and sent via the `pywebview` bridge to the Python `Framework`, where `setState()` triggers the reconciliation loop.

#### Data Flow: JavaScript to Python

The following diagram illustrates how a user interaction in the browser propagates to a Python state change.

**Interaction Propagation Path**

```
User Interaction (Click/Drag/Type)

JS Engine (slider.js / textfield.js)

Local DOM Update (Immediate UI Feedback)

window.pywebview.on_drag_update / on_event

PythraBridge (Python side)

Widget Callback (onChanged / onPressed)

State.setState()

Reconciler.reconcile()
```

Sources: [src/pythra/pythra/render_template/js/slider.js80-82](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/slider.js#L80-L82)[src/pythra/pythra/derived_widgets/dropdown/dropdown.py110-129](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/dropdown.py#L110-L129)

---

### Text Input: TextField

The `TextField` widget handles text entry and provides Material Design-style floating labels.

- **TextEditingController**: Manages the current text value and selection state.
- **Leading/Trailing Icons**: Supports `Icon` widgets placed at the start or end of the input field [textfield_and_widgets_report.md6-19](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/textfield_and_widgets_report.md#L6-L19)
- **Visual Masking**: The `PythraTextField` JS class calculates the background color of parent elements to create a "cutout" effect for outlined labels sitting on the top border [src/pythra/pythra/render_template/js/textfield.js28-61](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/textfield.js#L28-L61)

PropertyTypeDescription`controller``TextEditingController`Controls the text being edited.`onChanged``Callable[[str], None]`Called when the user changes the text.`decoration``InputDecoration`Defines border, label, and icon styles.`obscureText``bool`Whether to hide the text (for passwords).
Sources: [textfield_and_widgets_report.md1-29](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/textfield_and_widgets_report.md#L1-L29)[src/pythra/pythra/render_template/js/textfield.js1-18](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/textfield.js#L1-L18)

---

### Selection Widgets: Checkbox, Switch, and Radio

These widgets represent boolean or mutually exclusive choices. They utilize native HTML input states (`:checked`) for performance while mapping events to Python callbacks.

- **Switch**: A toggle switch. The `onChanged` callback is triggered when the user clicks the toggle.
- **Checkbox**: A standard tick box.
- **Radio**: Used for selecting a single value from a set.

Sources: [textfield_and_widgets_report.md79-82](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/textfield_and_widgets_report.md#L79-L82)

---

### Sliders: PythraSlider

The `PythraSlider` (implemented in Python as `Slider`) provides a draggable track for numeric input.

- **SliderController**: Manages the `min`, `max`, and `current_value`.
- **JS Engine**: High-frequency drag updates are handled in `slider.js` using `mousemove` and `touchmove` listeners to update the CSS variable `--slider-percentage`[src/pythra/pythra/render_template/js/slider.js63-73](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/slider.js#L63-L73)
- **Keyboard Support**: Supports `ArrowLeft`, `ArrowRight`, `ArrowUp`, and `ArrowDown` for accessibility, calculating steps based on the `divisions` property [src/pythra/pythra/render_template/js/slider.js99-130](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/slider.js#L99-L130)

**Slider Entity Mapping**

```
uses

initialized in DOM

Slider

+SliderController controller

+Callable onChanged

+int divisions

SliderController

+float value

+float min

+float max

+set_value(val)

PythraSliderJS

+options.onDragName

+updatePosition(event)

+handleKeyDown(event)
```

Sources: [src/pythra/pythra/render_template/js/slider.js5-30](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/slider.js#L5-L30)[src/pythra/pythra/render_template/js/slider.js112-120](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/slider.js#L112-L120)

---

### Dropdowns: VirtualDropdown

The `VirtualDropdown` is a complex interactive widget designed for selecting items from a list, supporting virtualization for large datasets.

- **VirtualDropdownController**: Stores the list of `items` and the currently selected `value`. It notifies listeners when the value is updated programmatically via `set_value()`[src/pythra/pythra/derived_widgets/dropdown/controller.py8-24](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/controller.py#L8-L24)
- **State Management**: `_VirtualDropdownState` tracks whether the menu is open (`is_open`) and handles the logic for item selection [src/pythra/pythra/derived_widgets/dropdown/dropdown.py63-76](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/dropdown.py#L63-L76)
- **Item Builder**: Uses a `vlist_item_builder` to render each row, allowing for custom styling of selected vs. unselected items [src/pythra/pythra/derived_widgets/dropdown/dropdown.py131-160](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/dropdown.py#L131-L160)

ComponentRole`VirtualDropdown`The widget definition (props like `theme`, `itemBuilder`).`_VirtualDropdownState`Manages `is_open` and triggers `setState()`.`VirtualDropdownController`External interface for getting/setting the dropdown value.`VirtualDropdownTheme`Styling properties for the panel, items, and margins.
Sources: [src/pythra/pythra/derived_widgets/dropdown/dropdown.py24-60](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/dropdown.py#L24-L60)[src/pythra/pythra/derived_widgets/dropdown/style.py8-16](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/style.py#L8-L16)

---

### Gesture Detection

The `GestureDetector` widget wraps other widgets to intercept low-level pointer events.

- **onTap**: Triggered on a simple click/touch release.
- **onPanUpdate**: Provides `PanUpdateDetails` (delta X/Y) for drag-based interactions.
- **onDoubleTap**: Triggered on rapid successive clicks.

The framework uses `onTapName` and `onTapArg` properties internally to route JS events back to the correct Python instance methods [src/pythra/pythra/derived_widgets/dropdown/dropdown.py153-155](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/dropdown.py#L153-L155)

---

### Buttons and Navigation

PyThra provides several button variants (`ElevatedButton`, `TextButton`, `IconButton`) which primarily serve as wrappers for `onPressed` callbacks.

- **Navigation Integration**: Buttons are frequently used with `NavigatorState` to change routes.
- **Navigator.push/pop**: `NavigatorState` maintains a `history` stack of `PageRoute` objects. Calling `push(route)` appends to the stack and triggers a rebuild of the navigator subtree [src/pythra/pythra/navigation.py38-46](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L38-L46)
- **Preloading**: The `preload()` method on `NavigatorState` allows background construction of widgets to reduce latency during transitions [src/pythra/pythra/navigation.py48-58](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L48-L58)

Sources: [src/pythra/pythra/navigation.py9-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L9-L20)[src/pythra/pythra/navigation.py70-77](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L70-L77)