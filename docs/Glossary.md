# Glossary
Relevant source files
- [CHANGELOG.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md)
- [GEMINI.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/GEMINI.md)
- [README.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md)
- [assets/demo.gif](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/assets/demo.gif)
- [pyproject.toml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml)
- [src/pythra/pythra/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py)
- [src/pythra/pythra/__pycache__/__init__.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/__init__.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/base.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/base.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/core.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/core.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/styles.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/styles.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/widgets.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/widgets.cpython-312.pyc)
- [src/pythra/pythra/core.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py)
- [src/pythra/pythra/key_cython.cpython-312-x86_64-linux-gnu.so](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/key_cython.cpython-312-x86_64-linux-gnu.so)
- [src/pythra/pythra/project_template/render/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/dropdown.js)
- [src/pythra/pythra/project_template/render/js/pythra_bridge.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js)
- [src/pythra/pythra/reconciler.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py)
- [src/pythra/pythra/reconciler_cython.c](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.c)
- [src/pythra/pythra/reconciler_cython.cpython-312-x86_64-linux-gnu.so](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.cpython-312-x86_64-linux-gnu.so)
- [src/pythra/pythra/reconciler_cython.pyx](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx)
- [src/pythra/pythra/reconciler_loader.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_loader.py)
- [src/pythra/pythra/render_template/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/dropdown.js)
- [src/pythra/pythra/styles.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py)
- [src/pythra/pythra/widgets.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py)
- [src/pythra/pythra/widgets_more.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py)
- [src/pythra/pythra/window/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/__init__.py)
- [src/pythra/setup.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py)
- [switch_bug_report.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/switch_bug_report.md)

This page provides a comprehensive technical reference for the specific terminology, architectural components, and domain concepts used within the PyThra Framework. It serves as a bridge between the high-level Flutter-inspired design patterns and their specific implementations in the Python/Webview hybrid environment.

## Core Architectural Terms

### Framework (Singleton)

The central orchestrator of the PyThra lifecycle. It manages the `AssetServer`, initializes the `QWebEngineView` (via `webwidget`), and maintains the global state of the application. It is implemented as a singleton to ensure a single event loop and resource manager exists per process.

- **Implementation:**`Framework` class in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L81-L115" min=81 max=115 file-path="src/pythra/pythra/core.py">Hii</FileRef>`.
- **Key Method:**`Framework.run()` starts the PySide6 event loop and serves the UI `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L341-L350" min=341 max=350 file-path="src/pythra/pythra/core.py">Hii</FileRef>`.

### Reconciliation

The process of comparing a "New" widget tree with an "Old" widget tree to determine the minimum set of changes (Patches) required to update the browser DOM. This avoids full page reloads and preserves ephemeral web state (like scroll position or input focus).

- **Implementation:**`Reconciler` class in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L82-L120" min=82 max=120 file-path="src/pythra/pythra/reconciler.py">Hii</FileRef>`.
- **Fast Path:** PyThra utilizes a Cython-accelerated version for high-performance diffing `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L1-L50" min=1 max=50 file-path="src/pythra/pythra/reconciler_cython.pyx">Hii</FileRef>`.

### Patch

A discrete instruction generated by the `Reconciler` and sent to the JavaScript `PythraBridge`. Patches describe specific DOM manipulations.

- **Action Types:**`INSERT`, `REMOVE`, `UPDATE`, `MOVE`, `REPLACE``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L61-L65" min=61 max=65 file-path="src/pythra/pythra/reconciler.py">Hii</FileRef>`.
- **Data Structure:**`Patch` dataclass `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L68-L73" min=68 max=73 file-path="src/pythra/pythra/reconciler.py">Hii</FileRef>`.

### Python-JS Bridge

The communication layer using `QWebChannel`. Python serializes `Patch` objects into JSON (via `orjson` for speed) and calls `applyPatches()` in the JavaScript runtime.

- **Python Side:**`Api` class in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/api.py#L10-L40" min=10 max=40 file-path="src/pythra/pythra/api.py">Hii</FileRef>`.
- **JS Side:**`pythra_bridge.js``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L1-L100" min=1 max=100 file-path="src/pythra/pythra/project_template/render/js/pythra_bridge.js">Hii</FileRef>`.

### Bridge Data Flow: Python to DOM

The following diagram illustrates how a Python state change travels through the system to become a visible DOM update.

```

```

**Sources:**`<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L81-L120" min=81 max=120 file-path="src/pythra/pythra/core.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L82-L150" min=82 max=150 file-path="src/pythra/pythra/reconciler.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/api.py#L10-L50" min=10 max=50 file-path="src/pythra/pythra/api.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L1-L50" min=1 max=50 file-path="src/pythra/pythra/project_template/render/js/pythra_bridge.js">Hii</FileRef>`.

---

## Widget & State Terminology

### Widget

The immutable description of a UI element. Every visual component in PyThra inherits from the `Widget` base class.

- **Implementation:**`Widget` class in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L10-L50" min=10 max=50 file-path="src/pythra/pythra/base.py">Hii</FileRef>`.

### StatefulWidget & State

A widget that can change over time. The `StatefulWidget` is the configuration, while the `State` object persists across rebuilds and holds the logic and data.

- **Implementation:**`StatefulWidget` and `State` in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L10-L100" min=10 max=100 file-path="src/pythra/pythra/state.py">Hii</FileRef>`.
- **Lifecycle:** Includes `initState()`, `build()`, and `dispose()``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L45-L70" min=45 max=70 file-path="src/pythra/pythra/state.py">Hii</FileRef>`.

### Key

An identifier used by the `Reconciler` to track widgets across rebuilds. Keys are essential for preserving state in dynamic lists (e.g., when items are reordered).

- **Implementation:**`Key` class in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L21-L25" min=21 max=25 file-path="src/pythra/pythra/base.py">Hii</FileRef>`.
- **Optimization:** PyThra uses a Cython-optimized `Key` for faster hashing and comparison `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L10-L30" min=10 max=30 file-path="src/pythra/pythra/reconciler_cython.pyx">Hii</FileRef>`.

### html_id

A unique string assigned to every rendered widget instance. This ID is used as the `id` attribute in the HTML DOM to target specific elements for updates.

- **Generation:** Managed by `IDGenerator` in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L130-L150" min=130 max=150 file-path="src/pythra/pythra/reconciler.py">Hii</FileRef>`.

---

## Styling & Layout Concepts

### Style Key & Shared Styles

To optimize CSS delivery, PyThra hashes the properties of a widget (color, padding, etc.) into a `style_key`. If multiple widgets share the same key, they share a single CSS class in the generated stylesheet.

- **Logic:**`make_hashable` utility in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L100-L120" min=100 max=120 file-path="src/pythra/pythra/base.py">Hii</FileRef>`.
- **Usage:**`Container.style_key` generation in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L193-L215" min=193 max=215 file-path="src/pythra/pythra/widgets.py">Hii</FileRef>`.

### EdgeInsets

A utility class for defining offsets (padding/margins) for the four sides of a box.

- **Implementation:**`EdgeInsets` in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L17-L184" min=17 max=184 file-path="src/pythra/pythra/styles.py">Hii</FileRef>`.
- **CSS Conversion:**`to_css()` converts the object to a CSS shorthand string (e.g., `10px 5px`) `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L116-L124" min=116 max=124 file-path="src/pythra/pythra/styles.py">Hii</FileRef>`.

### BoxDecoration

Defines how to paint a box, including borders, border radius, and box shadows.

- **Implementation:**`BoxDecoration` in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L400-L450" min=400 max=450 file-path="src/pythra/pythra/styles.py">Hii</FileRef>`.

### Alignment

Uses Flexbox concepts to position children within a parent.

- **Implementation:**`Alignment` in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L188-L250" min=188 max=250 file-path="src/pythra/pythra/styles.py">Hii</FileRef>`.

---

## Domain Concepts

### Virtualization (VirtualListView / VirtualGridView)

A technique where only the visible items in a large list or grid are rendered to the DOM. As the user scrolls, the JavaScript engine requests new items from Python.

- **Python Controller:**`VirtualListController` / `VirtualGridController``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/controllers.py#L50-L100" min=50 max=100 file-path="src/pythra/pythra/controllers.py">Hii</FileRef>`.
- **JS Engine:**`virtual_list.js` and `virtual_grid.js``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/virtual_grid.js#L1-L200" min=1 max=200 file-path="src/pythra/pythra/project_template/render/js/virtual_grid.js">Hii</FileRef>`.

### ClipPath Blueprints

A caching mechanism that prevents redundant SVG path generation. Unique clip paths are hashed and stored in a registry.

- **Implementation:**`_clip_blueprint_registry` in `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L3000-L3050" min=3000 max=3050 file-path="src/pythra/pythra/widgets.py">Hii</FileRef>` (referenced in `CHANGELOG.md``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L89-L92" min=89 max=92 file-path="CHANGELOG.md">Hii</FileRef>`).

### System Component Mapping

This diagram bridges natural language concepts to the specific Python classes and JavaScript files that implement them.

```

```

**Sources:**`<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L1-L50" min=1 max=50 file-path="src/pythra/pythra/base.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L1-L100" min=1 max=100 file-path="src/pythra/pythra/reconciler.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L81-L150" min=81 max=150 file-path="src/pythra/pythra/core.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L1-L50" min=1 max=50 file-path="src/pythra/pythra/project_template/render/js/pythra_bridge.js">Hii</FileRef>`.

---

## Abbreviations
AbbreviationMeaningContext**DOM**Document Object ModelThe browser-side representation of the UI.**M3**Material 3Design system guidelines followed by widgets `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L168-L170" min=168 max=170 file-path="src/pythra/pythra/widgets_more.py">Hii</FileRef>`.**CLI**Command Line InterfaceThe `pythra` command utility `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L36-L37" min=36 max=37 file-path="pyproject.toml">Hii</FileRef>`.**IPC**Inter-Process CommunicationThe bridge between Python and the Webview process.**Hicolor**High ColorLinux icon standard generated by CLI `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L15-L20" min=15 max=20 file-path="CHANGELOG.md">Hii</FileRef>`.
**Sources:**`<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L1-L200" min=1 max=200 file-path="src/pythra/pythra/widgets_more.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L1-L40" min=1 max=40 file-path="pyproject.toml">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L1-L50" min=1 max=50 file-path="CHANGELOG.md">Hii</FileRef>`.