# Framework Lifecycle and Orchestration
Relevant source files
- [.gitignore](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/.gitignore)
- [MANIFEST.in](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/MANIFEST.in)
- [src/pythra.egg-info/PKG-INFO](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra.egg-info/PKG-INFO)
- [src/pythra.egg-info/SOURCES.txt](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra.egg-info/SOURCES.txt)
- [src/pythra/pythra/__pycache__/base.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/base.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/core.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/core.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/widgets.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/widgets.cpython-312.pyc)
- [src/pythra/pythra/core.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py)
- [src/pythra/pythra/project_template/render/js/pythra_bridge.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js)
- [src/pythra/pythra/widgets.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py)
- [src/pythra/pythra/window/__pycache__/webwidget.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/__pycache__/webwidget.cpython-312.pyc)
- [src/pythra/pythra/window/webwidget.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/webwidget.py)
- [src/pythra/pythra/window/window_manager.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/window_manager.py)

The `Framework` class is the central orchestrator of the PyThra toolkit. Implemented as a singleton in `core.py`, it manages the application lifecycle, coordinate between the Python state logic and the Chromium-based rendering engine, and ensures system-level resilience for desktop environments.

## Framework Initialization

The lifecycle begins when `Framework.instance()` is called, typically within an application's `main.py` entry point. The initialization process follows a strict sequence to prepare the hybrid environment.

1. **Project Root Discovery**: The framework identifies the project directory by inspecting `sys.argv[0]`. It accounts for standard PyThra layouts where `main.py` may reside in a `lib/` subdirectory. [src/pythra/pythra/core.py121-132](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L121-L132)
2. **Configuration Loading**: It initializes the `Config` object, reading `config.yaml` to determine ports, asset paths, and window settings. [src/pythra/pythra/core.py134-137](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L134-L137)
3. **Asset Preparation**: It ensures the existence of `render/` and `assets/` directories. PyThra's internal JavaScript bridge (`pythra_bridge.js`) and core CSS are copied into the project's `render/` folder if missing. [src/pythra/pythra/core.py138-153](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L138-L153)
4. **Subsystem Startup**:

- **PackageManager**: Scans for and loads plugins/packages. [src/pythra/pythra/core.py154-174](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L154-L174)
- **AssetServer**: Starts a local multi-threaded server to provide the WebEngine with access to local HTML/JS/CSS and user assets. [src/pythra/pythra/core.py192-202](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L192-L202)
- **ThemeManager**: Initializes the global styling and theme variables. [src/pythra/pythra/core.py204-205](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L204-L205)

### Initialization Data Flow

The following diagram illustrates the transition from the "Natural Language" intent of starting an app to the "Code Entity" execution path.

**Diagram: Framework Startup Sequence**

```
WebWidget (webwidget.py)
AssetServer (server.py)
PackageManager
Framework (core.py)
User (main.py)
WebWidget (webwidget.py)
AssetServer (server.py)
PackageManager
Framework (core.py)
User (main.py)
Framework.instance()
__init__()
discover_all_packages()
AssetServer(port, directory)
Server Thread Started
set_root(Widget)
run()
QApplication.exec()
```

**Sources:**[src/pythra/pythra/core.py98-210](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L98-L210)[src/pythra/pythra/server.py1-50](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/server.py#L1-L50)

---

## The Main Event Loop and WebEngine Creation

The `run()` method triggers the transition from Python setup to the interactive GUI phase. It initializes the `QApplication` and creates the `PythraWindow`.

### QWebEngineView and Asset Loading

The framework creates a `PythraWindow` (inheriting from `QWebEngineView`) which acts as the primary viewport. [src/pythra/pythra/core.py535-546](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L535-L546)

- **AssetServer**: The `AssetServer` serves files via `http://localhost:[port]`. The `QWebEngineView` loads the `index.html` from this local URL. [src/pythra/pythra/core.py554-558](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L554-L558)
- **QWebChannel**: A `QWebChannel` is established to allow the Python `Api` class to communicate with the JavaScript `PythraBridge`. [src/pythra/pythra/window/webwidget.py75-85](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/webwidget.py#L75-L85)

### Power and DPI Resilience

PyThra includes specific logic to handle desktop-specific events that often break webview-based apps:

- **High DPI Scaling**: Attributes `Qt.AA_EnableHighDpiScaling` and `Qt.AA_UseHighDpiPixmaps` are set before `QApplication` initialization to ensure crisp rendering on 4K displays. [src/pythra/pythra/window/webwidget.py135-136](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/webwidget.py#L135-L136)
- **Resume Events**: The `SystemSleepManager` (integrated via `webwidget.py`) monitors system-level sleep/resume signals. Upon resume, the framework can trigger a `force_update()` or re-sync the `AssetServer` to prevent "frozen" webviews. [src/pythra/pythra/window/webwidget.py98-100](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/webwidget.py#L98-L100)

**Sources:**[src/pythra/pythra/core.py528-570](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L528-L570)[src/pythra/pythra/window/webwidget.py135-150](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/webwidget.py#L135-L150)

---

## Orchestration Logic: set_root() and Build Pipeline

The `set_root()` method defines the entry point of the widget tree. This call triggers the first full build and reconciliation. [src/pythra/pythra/core.py488-510](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L488-L510)

### The Render Cycle

1. **Widget Instantiation**: The root widget and its children are created in Python.
2. **Initial Reconciliation**: The `Reconciler` performs an initial "diff" against an empty state, generating `INSERT` patches for the entire tree. [src/pythra/pythra/core.py270-285](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L270-L285)
3. **Patch Serialization**: The framework uses `orjson` (if available) for high-speed serialization of the widget tree into JSON patches. [src/pythra/pythra/core.py68-79](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L68-L79)
4. **JS Bridge Execution**: Patches are sent over the `QWebChannel`. The JavaScript `PythraBridge.applyPatches()` method receives these and performs DOM manipulations. [src/pythra/pythra/project_template/render/js/pythra_bridge.js1-15](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L1-L15)

**Diagram: Orchestration Bridge (Python to JS)**

```
JavaScript Render (pythra_bridge.js)

Communication Layer

Python Logic (core.py)

ReconciliationResult

Framework.instance()

Reconciler.reconcile()

Api.send_patch()

QWebChannel

PythraBridge.applyPatches()

document.getElementById().appendChild()
```

**Sources:**[src/pythra/pythra/core.py260-300](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L260-L300)[src/pythra/pythra/reconciler.py57-61](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L57-L61)[src/pythra/pythra/project_template/render/js/pythra_bridge.js17-39](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L17-L39)

---

## Key Framework Methods
MethodRoleImplementation Detail`instance()`Singleton AccessReturns `_instance` or creates it. [src/pythra/pythra/core.py98-103](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L98-L103)`set_root(widget)`Entry PointSets `self.root_widget` and triggers `_reconcile_and_update()`. [src/pythra/pythra/core.py488-510](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L488-L510)`run()`Main LoopStarts `AssetServer`, initializes `PythraWindow`, and calls `app.exec()`. [src/pythra/pythra/core.py528-570](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L528-L570)`_reconcile_and_update()`Diff PipelineCalls `Reconciler.reconcile()`, processes `active_css_details`, and sends patches to JS. [src/pythra/pythra/core.py260-310](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L260-L310)`force_update()`Full RefreshClears the `rendered_widgets_map` and performs a clean-slate build. [src/pythra/pythra/core.py312-325](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L312-L325)
**Sources:**[src/pythra/pythra/core.py81-570](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L81-L570)