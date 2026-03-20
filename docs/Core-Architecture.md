# Core Architecture
Relevant source files
- [CHANGELOG.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md)
- [pyproject.toml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml)
- [src/pythra/pythra/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py)
- [src/pythra/pythra/__pycache__/base.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/base.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/core.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/core.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/widgets.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/widgets.cpython-312.pyc)
- [src/pythra/pythra/core.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py)
- [src/pythra/pythra/project_template/render/js/pythra_bridge.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js)
- [src/pythra/pythra/widgets.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py)
- [src/pythra/setup.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py)

The PyThra Framework implements a declarative UI model where the user interface is a function of the application state. It bridges a high-level Python API with a high-performance web-based rendering layer. The architecture is centered around a singleton orchestrator that manages a recursive diffing engine and a bidirectional communication bridge.

### System Overview

The following diagram illustrates the high-level relationship between the Python-side logic and the Browser-side DOM updates.

**Architecture Flow: State to DOM**

```
Browser Environment (QWebEngineView)

Python Environment

setState()

reconcile()

Generate Patches

run_js(applyPatches)

QWebChannel

DOM Manipulation

Serve Assets

Framework (core.py)

StatefulWidget (state.py)

State (state.py)

Reconciler (reconciler.py)

AssetServer (server.py)

PythraBridge (pythra_bridge.js)

Browser DOM

Api (api.py)
```

Sources: [src/pythra/pythra/core.py81-119](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L81-L119)[src/pythra/pythra/state.py10-50](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L10-L50)[src/pythra/pythra/reconciler.py5-60](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L5-L60)[src/pythra/pythra/project_template/render/js/pythra_bridge.js1-39](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L1-L39)

---

### 2.1 Framework Lifecycle and Orchestration

The `Framework` class in `core.py` acts as the central hub. It initializes the environment, including the `AssetServer` for static files and the `PackageManager` for plugins. It manages the root widget tree via `set_root()` and handles the main event loop through PySide6.

**Key Responsibilities:**

- **Initialization:** Detects project root, loads `config.yaml`, and ensures default CSS/JS assets exist in the `render/` directory [src/pythra/pythra/core.py105-152](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L105-L152)
- **Window Management:** Creates the `webwidget` (QWebEngineView) and handles platform-specific windowing logic [src/pythra/pythra/core.py31-35](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L31-L35)
- **Execution:** The `run()` method starts the Qt event loop and the local asset server [src/pythra/pythra/core.py81-94](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L81-L94)

For details, see [Framework Lifecycle and Orchestration](/pythra-toolkit/pythra-toolkit/2.1-framework-lifecycle-and-orchestration).

---

### 2.2 State Management

PyThra uses a `StatefulWidget` and `State` pattern similar to Flutter. When a user calls `setState()`, the framework marks a subtree as "dirty" and queues it for the next reconciliation cycle.

**State Lifecycle:**

- **`initState()`**: Called when the state object is first created [src/pythra/pythra/state.py22-25](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L22-L25)
- **`didUpdateWidget()`**: Called when the widget configuration changes but the state persists.
- **`dispose()`**: Called when the widget is removed from the tree.

For details, see [State Management](/pythra-toolkit/pythra-toolkit/2.2-state-management).

Sources: [src/pythra/pythra/state.py22-35](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L22-L35)[src/pythra/pythra/base.py73-100](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L73-L100)

---

### 2.3 Reconciler and Diffing Engine

The `Reconciler` is the "intelligence" of the framework. Instead of re-rendering the entire DOM on every change, it performs a recursive diff between the `old_tree` and `new_tree` to generate a list of `Patch` objects.

**Entity Mapping: Python Logic to Patch Generation**

```
invokes

produces

Framework

+Reconciler reconciler

+set_root(Widget)

+reconcile()

Reconciler

+reconcile(old_node, new_node)

+_diff_node_recursive()

+_diff_children_recursive()

Patch

+str action

+str html_id

+dict data
```

Sources: [src/pythra/pythra/reconciler.py5-61](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L5-L61)[src/pythra/pythra/core.py36-41](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L36-L41)

The engine supports five primary actions: `INSERT`, `REMOVE`, `UPDATE`, `MOVE`, and `REPLACE`[src/pythra/pythra/reconciler.py32-37](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L32-L37) To maximize performance, PyThra utilizes a Cython-accelerated layer (`reconciler_cython`) for heavy tree traversals [src/pythra/setup.py17-29](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L17-L29)

For details, see [Reconciler and Diffing Engine](/pythra-toolkit/pythra-toolkit/2.3-reconciler-and-diffing-engine).

---

### 2.4 Python–JavaScript Bridge

The bridge facilitates communication between the Python backend and the Chromium-based frontend. It consists of the `AssetServer` for file delivery and a `QWebChannel` for real-time execution.

**Bridge Components:**

- **`AssetServer`**: A local server that handles requests for CSS, JS, and project assets [src/pythra/pythra/server.py29-35](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/server.py#L29-L35)
- **`Api` Class**: Exposes Python methods to JavaScript via `pywebview` callbacks [src/pythra/pythra/api.py49-55](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/api.py#L49-L55)
- **`PythraBridge.js`**: The client-side executor that receives JSON patches and applies them to the DOM using `handleInsert`, `handleUpdate`, and `handleRemove`[src/pythra/pythra/project_template/render/js/pythra_bridge.js17-39](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L17-L39)

For details, see [Python–JavaScript Bridge](/pythra-toolkit/pythra-toolkit/2.4-python-javascript-bridge).

Sources: [src/pythra/pythra/core.py29-30](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L29-L30)[src/pythra/pythra/project_template/render/js/pythra_bridge.js41-118](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L41-L118)