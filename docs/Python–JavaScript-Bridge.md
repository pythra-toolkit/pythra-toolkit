# Python–JavaScript Bridge
Relevant source files
- [assets/pythra.png](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/assets/pythra.png)
- [src/pythra/pythra/__pycache__/base.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/base.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/core.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/core.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/widgets.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/widgets.cpython-312.pyc)
- [src/pythra/pythra/core.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py)
- [src/pythra/pythra/project_template/render/js/pythra_bridge.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js)
- [src/pythra/pythra/render_template/js/pythra_bridge.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js)
- [src/pythra/pythra/widgets.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py)
- [src/pythra/pythra/window/ind.html](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/ind.html)
- [src/pythra/pythra/window/main.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/main.py)
- [src/pythra/pythra/window/qwebchannel.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/qwebchannel.js)

The Python–JavaScript Bridge is the critical communication layer that enables PyThra's hybrid architecture. It facilitates the flow of declarative UI updates from the Python-based Reconciler to the browser's Document Object Model (DOM) and routes user interactions (events) back to Python logic.

## Communication Pipeline Overview

The bridge operates as a bi-directional pipeline using **QWebChannel** for message passing and **JSON patches** for state synchronization.

1. **Python to JavaScript**: When `setState()` triggers a reconciliation, the `Reconciler` generates a list of `Patch` objects. These are serialized into JSON and sent via `QWebEngineView.page().runJavaScript()` to the `PythraBridge.applyPatches()` function in the browser.
2. **JavaScript to Python**: User interactions (clicks, inputs, scrolls) are captured by JS event listeners. These listeners call methods on the `pywebview` object (provided by `QWebChannel`), which maps directly to the `Api` class in Python.

### System Architecture Diagram

"Data Flow from Python State to Browser DOM"

```

```

Sources: `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L71-L74" min=71 max=74 file-path="src/pythra/pythra/core.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L82-L85" min=82 max=85 file-path="src/pythra/pythra/reconciler.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L1-L15" min=1 max=15 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/ind.html#L86-L91" min=86 max=91 file-path="src/pythra/pythra/window/ind.html">Hii</FileRef>`

---

## Server and API Layer

### AssetServer (`server.py`)

The `AssetServer` handles the delivery of static files (HTML, CSS, JS) to the `QWebEngineView`. It ensures that the browser can resolve local project assets and PyThra's internal rendering engine scripts.

### Api Class (`api.py`)

The `Api` class acts as the gateway for JS-to-Python communication. It is registered with the `QWebChannel` and exposed to the window as `window.pywebview`.

- **Callback Registration**: Python functions are registered via `api.register_callback(name, func)``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/main.py#L18-L20" min=18 max=20 file-path="src/pythra/pythra/window/main.py">Hii</FileRef>`.
- **Event Handling**: JavaScript calls functions like `window.pywebview.on_pressed(name, ...args)``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/ind.html#L96-L100" min=96 max=100 file-path="src/pythra/pythra/window/ind.html">Hii</FileRef>`, which triggers the corresponding Python callback.

Sources: `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L29-L30" min=29 max=30 file-path="src/pythra/pythra/core.py">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/main.py#L4-L15" min=4 max=15 file-path="src/pythra/pythra/window/main.py">Hii</FileRef>`

---

## Serialization and Patching

### JSON Serialization via orjson

To maintain high-performance updates, PyThra uses `orjson` for serializing the `Patch` list. The `_dumps` function in `core.py` provides a fast path for converting complex Python widget structures into a compact JSON format readable by the JavaScript bridge.

- **Default Handler**: `_json_default_handler` handles non-standard types like `Widget`, `weakref`, and `set` during serialization `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L50-L65" min=50 max=65 file-path="src/pythra/pythra/core.py">Hii</FileRef>`.
- **Performance**: `orjson` is preferred over the standard library `json` for its speed-critical execution during UI updates `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L68-L74" min=68 max=74 file-path="src/pythra/pythra/core.py">Hii</FileRef>`.

### PythraBridge (`pythra_bridge.js`)

The `PythraBridge` object is the primary executor in the browser. It receives the patch array and iterates through it to perform granular DOM mutations.

- **applyPatches(patches)**: The entry point that loops through incoming instructions `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L2-L15" min=2 max=15 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`.
- **processPatch(patch)**: Dispatches to specific handlers based on the `PatchAction` (INSERT, REMOVE, UPDATE, MOVE, REPLACE) `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L17-L39" min=17 max=39 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`.

"Mapping Reconciler Patches to DOM Actions"
Patch ActionJavaScript HandlerDOM Operation`INSERT``handleInsert``document.createElement` + `insertBefore` / `appendChild``REMOVE``handleRemove``parentNode.removeChild` + Instance cleanup`UPDATE``handleUpdate`Selective attribute/property sync via `updateProps``MOVE``handleMove`Re-insertion at new index using `insertBefore``REPLACE``handleReplace``parentNode.replaceChild` with new HTML stub
Sources: `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L20-L35" min=20 max=35 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L55-L60" min=55 max=60 file-path="src/pythra/pythra/reconciler.py">Hii</FileRef>`

---

## DOM Execution Details

### Incremental Property Updates

The `updateProps` function is designed to prevent "state loss" (such as losing text cursor position) by only updating properties if they have changed.

- **Input Handling**: For `TextField` widgets, `el.value` is only set if the incoming value differs from the current one to avoid cursor jumps `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L159-L163" min=159 max=163 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`.
- **CSS Class Management**: Shared styles are managed by splitting class strings and using `classList.add/remove` for efficiency `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L141-L152" min=141 max=152 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`.
- **Dynamic Styles**: Inline styles are injected using `el.style.setProperty(key, value)``<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L169-L176" min=169 max=176 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`.

### Widget Initializers

Certain widgets require JavaScript-side initialization (e.g., Sliders, Custom ClipPaths).

- **Dispatch**: `handleInsert` checks for `init_gradient_clip_border` and similar flags in the `props` object to instantiate the corresponding JS engine class `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L73-L80" min=73 max=80 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`.
- **Cleanup**: `handleRemove` deletes instances from `window._pythra_instances` to prevent memory leaks `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L87-L90" min=87 max=90 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`.

Sources: `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/pythra_bridge.js#L137-L179" min=137 max=179 file-path="src/pythra/pythra/render_template/js/pythra_bridge.js">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L63-L83" min=63 max=83 file-path="src/pythra/pythra/project_template/render/js/pythra_bridge.js">Hii</FileRef>`

---

## JS-to-Python Event Interface

The bridge utilizes the `pywebview` global object (initialized via `QWebChannel`) to send signals back to Python.

"Code Entity Interaction for User Events"

```

```

Sources: `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/ind.html#L93-L104" min=93 max=104 file-path="src/pythra/pythra/window/ind.html">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/qwebchannel.js#L176-L180" min=176 max=180 file-path="src/pythra/pythra/window/qwebchannel.js">Hii</FileRef>`, `<FileRef file-url="https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L81-L103" min=81 max=103 file-path="src/pythra/pythra/core.py">Hii</FileRef>`