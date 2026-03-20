# Style Primitives
Relevant source files
- [src/pythra/pythra/__pycache__/__init__.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/__init__.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/styles.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/styles.cpython-312.pyc)
- [src/pythra/pythra/project_template/render/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/dropdown.js)
- [src/pythra/pythra/render_template/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/dropdown.js)
- [src/pythra/pythra/styles.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py)
- [src/pythra/pythra/widgets_more.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py)

The PyThra styling system uses a collection of primitive classes to represent visual properties. These primitives are designed to mimic the Flutter styling API while providing a bridge to the web-based rendering engine. Each primitive is responsible for transforming Python-based design definitions into CSS strings or hashable structures compatible with the framework's reconciliation engine.

## Core Transformation Methods

Every style primitive implements three critical methods to support the rendering pipeline:

1. `to_css()`: Generates a valid CSS string for the property [src/pythra/pythra/styles.py116-123](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L116-L123)
2. `to_tuple()`: Converts the object into a flat tuple of primitive values (floats, strings) for serialization [src/pythra/pythra/styles.py180-182](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L180-L182)
3. `__hash__`: Ensures the style object can be used as a key in the shared styles registry, preventing redundant CSS generation [src/pythra/pythra/styles.py145-146](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L145-L146)

### Style Transformation Flow

The following diagram illustrates how a Python style object travels from a Widget definition to a DOM element in the browser.

"Style-to-DOM-Pipeline"

```
Code Entity Space (JS/CSS)

Code Entity Space (Python)

Natural Language Space

'Padding of 10px'

'Blue Background'

EdgeInsets.all(10.0)

BoxDecoration(color=Colors.blue)

Widget.render_props()

Reconciler.generate_css_rule()

style_key (Hash)

.pythra-style-hash { ... }

DOM element.classList.add()
```

Sources: [src/pythra/pythra/styles.py17-53](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L17-L53)[src/pythra/pythra/styles.py201-215](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L201-L215)[src/pythra/pythra/widgets_more.py172-181](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L172-L181)

---

## Layout Primitives

### EdgeInsets

Represents padding or margin values. It supports standard Flutter-like constructors: `all()`, `symmetric()`, and `only()`[src/pythra/pythra/styles.py49-72](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L49-L72)
MethodDescriptionCSS Output Example`all(10)`Same value for all sides`10px``symmetric(v, h)`Vertical and Horizontal pairs`vpx hpx``only(top=5)`Specific side only`5px 0px 0px 0px`
Sources: [src/pythra/pythra/styles.py17-114](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L17-L114)

### BoxConstraints

Defines the size limits for a widget. The reconciler uses these to set `min-width`, `max-width`, `min-height`, and `max-height` CSS properties [src/pythra/pythra/styles.py456-465](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L456-L465)

### Alignment

Maps conceptual positions (e.g., `Alignment.center`) to Flexbox `justify-content` and `align-items` values [src/pythra/pythra/styles.py188-195](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L188-L195)

---

## Visual Primitives

### BoxDecoration

A complex primitive that aggregates color, border, border-radius, and shadows into a single container style [src/pythra/pythra/styles.py201-220](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L201-L220)

"BoxDecoration-Mapping"

```
CSS Properties

Python: BoxDecoration

color

border

borderRadius

boxShadow

background-color

border

border-radius

box-shadow
```

Sources: [src/pythra/pythra/styles.py201-240](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L201-L240)

### Border and BorderRadius

- **Border**: Encapsulates `BorderSide` objects for top, right, bottom, and left edges [src/pythra/pythra/styles.py534-545](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L534-L545)
- **BorderRadius**: Handles corner rounding via `BorderRadius.circular()` or `BorderRadius.only()`[src/pythra/pythra/styles.py640-655](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L640-L655)

### TextStyle

Documents font properties including `fontSize`, `fontWeight`, `fontStyle`, `letterSpacing`, and `color`. The `to_css()` implementation translates these into standard CSS font properties [src/pythra/pythra/styles.py480-500](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L480-L500)

### BoxShadow

Represents a single shadow entry. Multiple `BoxShadow` objects can be passed to a `BoxDecoration` to create layered shadows [src/pythra/pythra/styles.py380-395](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L380-L395)

---

## Utility Primitives

### Matrix4

Provides 4x4 matrix transformation capabilities. It includes helper methods like `identity()`, `rotationZ()`, `translationValues()`, and `diagonal3Values()`[src/pythra/pythra/styles.py1150-1175](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L1150-L1175) These are converted to the CSS `transform: matrix3d(...)` property.

### Colors

A utility class providing access to the Material Design 3 color palette. It supports hex strings and handles dynamic theme variables (e.g., `var(--primary)`) [src/pythra/pythra/styles.py400-410](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L400-L410)

### BoxFit

An Enum-like primitive that determines how an image or content should fit its container, mapping to the CSS `object-fit` property [src/pythra/pythra/styles.py1100-1110](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L1100-L1110)

---

## Implementation Details for Reconciler

To maintain high performance, the framework avoids recalculating CSS for every frame.

1. **Hashing**: Every primitive implements `__hash__` by hashing its internal values (e.g., `EdgeInsets` hashes the tuple of its four sides) [src/pythra/pythra/styles.py145-146](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L145-L146)
2. **Shared Styles**: The `Widget` base class uses these hashes to generate a `style_key`. If multiple widgets share the same style primitives, they share a single CSS class in the generated HTML [src/pythra/pythra/base.py110-125](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L110-L125)
3. **make_hashable**: A utility function used to recursively convert lists and dictionaries within style definitions into hashable tuples, ensuring complex props can be compared by the diffing engine [src/pythra/pythra/base.py45-60](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L45-L60)

Sources: [src/pythra/pythra/styles.py1-1200](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L1-L1200)[src/pythra/pythra/base.py40-130](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L40-L130)