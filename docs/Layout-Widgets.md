# Layout Widgets
Relevant source files
- [src/pythra/pythra/__pycache__/base.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/base.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/core.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/core.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/widgets.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/widgets.cpython-312.pyc)
- [src/pythra/pythra/core.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py)
- [src/pythra/pythra/project_template/render/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/dropdown.js)
- [src/pythra/pythra/project_template/render/js/pythra_bridge.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js)
- [src/pythra/pythra/render_template/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/dropdown.js)
- [src/pythra/pythra/styles.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py)
- [src/pythra/pythra/widgets.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py)
- [src/pythra/pythra/widgets_more.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py)

Layout widgets are the structural foundation of a PyThra application. They are responsible for sizing, positioning, and arranging child widgets within the UI. Inspired by Flutter's layout model, PyThra uses a combination of flexbox-based containers (Row, Column, Flex) and absolute positioning (Stack, Positioned) to build complex, responsive interfaces.

## Core Layout Concepts

PyThra's layout system relies on several key primitives to define spacing and alignment.

### BoxConstraints

`BoxConstraints` define the minimum and maximum allowable width and height for a widget [src/pythra/pythra/styles.py530-534](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L530-L534) During the render process, these constraints are passed down the widget tree. A widget must decide its own size within these boundaries.

### EdgeInsets

`EdgeInsets` represents offsets from the four cardinal directions: left, top, right, and bottom [src/pythra/pythra/styles.py17-25](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L17-L25) It is used to define both `padding` (internal space) and `margin` (external space) for widgets like `Container`[src/pythra/pythra/widgets.py168-174](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L168-L174)

- **`EdgeInsets.all(value)`**: Applies the same offset to all sides [src/pythra/pythra/styles.py50-53](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L50-L53)
- **`EdgeInsets.symmetric(horizontal, vertical)`**: Applies specific offsets to the horizontal and vertical axes [src/pythra/pythra/styles.py56-60](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L56-L60)
- **`EdgeInsets.only(...)`**: Allows specifying individual sides [src/pythra/pythra/styles.py63-72](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L63-L72)

### Alignment and Axis

PyThra uses `MainAxisAlignment` and `CrossAxisAlignment` enums to control how children are distributed along a layout's primary and secondary axes [src/pythra/pythra/styles.py246-302](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L246-L302)
Alignment TypeCSS MappingDescription`start``flex-start`Align to the start of the axis.`end``flex-end`Align to the end of the axis.`center``center`Align to the center of the axis.`spaceBetween``space-between`Distribute items evenly; first item at start, last at end.`spaceAround``space-around`Distribute items evenly with half-space on ends.`stretch``stretch`Force children to fill the cross-axis.
## Principal Layout Widgets

### Container

The `Container` is a multi-purpose widget that combines sizing, padding, and decoration [src/pythra/pythra/widgets.py73-137](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L73-L137) It can hold a single `child`. If a `Container` has no child and no fixed dimensions, it will attempt to expand to fill its parent.

**Implementation Detail:**`Container` styles are hashed into a `style_key` to optimize CSS generation. If multiple containers share identical properties, they share the same generated CSS class [src/pythra/pythra/widgets.py193-225](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L193-L225)

### Column and Row

These widgets arrange their `children` in a linear array. `Column` arranges children vertically [src/pythra/pythra/widgets.py347-350](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L347-L350) while `Row` arranges them horizontally [src/pythra/pythra/widgets.py440-443](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L440-L443) Both inherit from `Flex`.

### Flex and Expanded

`Flex` is the base class for `Row` and `Column`. It allows for flexible distribution of space using the `Expanded` widget. When a child is wrapped in `Expanded`, it is assigned a `flex` factor (defaulting to 1), which dictates what portion of the remaining main-axis space it should occupy [src/pythra/pythra/widgets.py575-585](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L575-L585)

### Stack and Positioned

`Stack` allows for overlapping widgets, painting them from back to front [src/pythra/pythra/widgets.py660-665](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L660-L665) Children are positioned relative to the Stack's edges. The `Positioned` widget is used within a `Stack` to specify exact coordinates (top, left, right, bottom) for a child [src/pythra/pythra/widgets.py730-740](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L730-L740)

### Wrap

`Wrap` displays its children in multiple horizontal or vertical "runs" [src/pythra/pythra/widgets.py820-825](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L820-L825) Unlike `Row` or `Column`, if there is insufficient space in the current run, `Wrap` will break to a new line or column.

## Layout System Architecture

The following diagram illustrates how Python layout widget definitions are translated into DOM structures and CSS rules.

### Layout to CSS Translation Flow

Title: Layout Widget Translation

```

```

**Sources:**[src/pythra/pythra/widgets.py73-225](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L73-L225)[src/pythra/pythra/styles.py17-188](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L17-L188)[src/pythra/pythra/reconciler.py57-61](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L57-L61)

### Layout Class Hierarchy

Title: Layout Widget Inheritance

```

```

**Sources:**[src/pythra/pythra/widgets.py73-137](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L73-L137)[src/pythra/pythra/widgets.py347-350](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L347-L350)[src/pythra/pythra/widgets.py440-443](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L440-L443)[src/pythra/pythra/widgets.py530-540](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L530-L540)[src/pythra/pythra/widgets.py660-665](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L660-L665)

## Specialized Layout Widgets

- **`Center`**: A shorthand for a `Container` with `alignment=Alignment.center`[src/pythra/pythra/widgets.py910-915](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L910-L915)
- **`Align`**: Positions a child within itself using an `Alignment` object [src/pythra/pythra/widgets.py965-970](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L965-L970)
- **`Padding`**: A widget that solely adds `EdgeInsets` around its child [src/pythra/pythra/widgets.py1020-1025](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L1020-L1025)
- **`SizedBox`**: A box with a specified fixed width and height. Used to create gaps or force child dimensions [src/pythra/pythra/widgets.py1075-1080](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L1075-L1080)
- **`AspectRatio`**: Attempts to size the child to a specific width-to-height ratio [src/pythra/pythra/widgets.py1140-1145](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L1140-L1145)
- **`FittedBox`**: Scales and positions its child within itself according to a `BoxFit` (e.g., contain, cover, fill) [src/pythra/pythra/widgets.py1260-1265](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L1260-L1265)
- **`FractionallySizedBox`**: Sizes its child to a fraction of the total available space [src/pythra/pythra/widgets.py1195-1200](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L1195-L1200)

## Implementation of Layout Updates

When a layout property (like a `Column`'s alignment) changes, the `Reconciler` identifies the change during the `_diff_node_recursive` process [src/pythra/pythra/reconciler.py26-36](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L26-L36)

1. **Diffing**: The `Reconciler` compares the `style_key` of the old and new widget instances [src/pythra/pythra/reconciler.py44-54](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L44-L54)
2. **Patch Generation**: If the layout properties differ, an `UPDATE` patch is generated [src/pythra/pythra/reconciler.py34-35](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L34-L35)
3. **DOM Application**: The `PythraBridge.js` receives the patch and calls `updateProps`. For layout changes, this usually involves swapping a CSS class or updating the `style` attribute of the corresponding HTML element [src/pythra/pythra/project_template/render/js/pythra_bridge.js118-127](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L118-L127)

**Sources:**[src/pythra/pythra/widgets.py1-1300](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L1-L1300)[src/pythra/pythra/styles.py1-600](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L1-L600)[src/pythra/pythra/reconciler.py1-60](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L1-L60)[src/pythra/pythra/project_template/render/js/pythra_bridge.js1-161](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L1-L161)