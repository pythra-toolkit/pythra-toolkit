# Creating and Using Plugins in PyThra

This guide provides a comprehensive, production-grade reference for authoring, structuring, and consuming PyThra plugins. It is based directly on production plugins within the ecosystem, including **`pythra_motion`** (client-side animation engine), **`pythra-markdown-render`** (sanitized Markdown & syntax highlighting engine), and **`pythra-video-player`** (hardware-accelerated canvas/streaming media engine).

---

## 1. Architecture & Plugin Ecosystem Overview

PyThra features a modular package and plugin architecture inspired by Flutter and `pub.dev`. Rather than bloating the core framework with domain-specific features (such as Markdown parsing, media decoding, or heavy animation libraries), PyThra delegates these capabilities to self-contained plugins.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          PyThra Application                            │
│  config.yaml:                                                          │
│    plugins:                                                            │
│      - pythra_motion                                                   │
│      - markdown_render                                                 │
└──────────────────┬──────────────────────────────────┬──────────────────┘
                   │                                  │
         Runtime Import Guard                  Package Discovery
        (sys.meta_path Check)             (PackageManager & Sources)
                   │                                  │
┌──────────────────▼──────────────────────────────────▼──────────────────┐
│                   Python Plugin Layer (`plugins/<name>/`)               │
│  - package.json (Manifest)                                             │
│  - widget.py (StatefulWidget / StatelessWidget)                         │
│  - controller.py (Imperative API & Callback Management)                │
│  - state.py (js_init Bridge & Lifecycle Hooks)                         │
└──────────────────┬──────────────────────────────────┬──────────────────┘
                   │                                  │
              props._js_init                     AssetServer
         (Reconciler Initializer)           (/packages/<name>/...)
                   │                                  │
┌──────────────────▼──────────────────────────────────▼──────────────────┐
│                 Web Engine Layer (QWebEngineView / DOM)                │
│  - CSS Injection (css_files from manifest)                             │
│  - Vendor Script Ingestion (marked.js, motion.js, highlight.js)        │
│  - Engine Class Instantiation (`new window[engineName](el, options)`)  │
│  - Global Instance Registry (`window._pythra_instances[instanceId]`)   │
│  - Bidirectional IPC (evaluate_js <---> pywebview.api)                 │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Concepts:
1. **Separation of Concerns**: Python manages business logic, application state, and widget composition. JavaScript handles high-frequency DOM manipulation, CSS transforms, canvas rendering, and browser events.
2. **Declarative Whitelisting**: Plugins must be explicitly declared under `plugins` in the application's `config.yaml`. Unlisted plugins are barred from discovery, asset serving, and Python runtime import.
3. **Generic `js_init` Protocol**: Widgets attach a lightweight `js_init` specification to their rendered output. PyThra's DOM Reconciler automatically injects required scripts and instantiates the client-side JavaScript engine.
4. **Lifecycle Synchronization**: When widgets mount, update, or dispose, their counterpart JavaScript instances are instantiated, updated, or cleaned up via `destroy()`.

---

## 2. Directory Structure of a PyThra Plugin

A standard PyThra plugin lives in `plugins/<plugin_folder_name>/` or is distributed as an installed Python package.

```
plugins/my_custom_plugin/
├── package.json              # Plugin manifest (metadata, dependencies, JS/CSS assets)
├── __init__.py               # Public API exports
├── widget.py                 # Primary StatefulWidget or StatelessWidget
├── controller.py             # User-facing controller for imperative manipulation
├── state.py                  # Widget State managing the js_init bridge
├── style.py                  # Typed style classes (optional)
└── render/                   # Asset directory served by PyThra's AssetServer
    ├── css/
    │   ├── vendor/           # Third-party styles (e.g. highlight.js themes)
    │   └── my_plugin.css     # Plugin custom styles
    └── js/
        ├── vendor/           # Third-party libraries (e.g. marked.min.js, purify.min.js)
        └── my_engine.js      # Client-side engine class implementing PyThra's contract
```

---

## 3. The Plugin Manifest (`package.json`)

The `package.json` file is the contract between your plugin and the PyThra Framework. It defines metadata, Python module exports, client-side JavaScript entry points, CSS stylesheets, and dependency versions.

### Manifest Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | `string` | Unique identifier (e.g., `"pythra_motion"`, `"pythra-markdown-render"`). |
| `version` | `string` | Semantic version string (e.g., `"1.0.0"`). |
| `package_type` | `string` | Must be `"plugin"`, `"widgets"`, `"theme"`, or `"utility"`. |
| `description` | `string` | Human-readable explanation of plugin capabilities. |
| `dependencies` | `object` | PyThra and plugin dependency version constraints. |
| `python_modules` | `array` | List of Python module names in the folder to load (e.g., `["__init__", "widget", "controller"]`). |
| `asset_dir` | `string` | Directory containing static assets to serve via the asset server (typically `"render"`). |
| `js_modules` | `object` | Map of Global JS Variable / Engine names to their file paths relative to `asset_dir`. |
| `css_files` | `array` | List of CSS stylesheets relative to `asset_dir` to auto-inject into the HTML `<head>`. |
| `tags` | `array` | Keywords for categorization and search. |

---

### Real-World Manifest Examples

#### Example 1: Animation Engine (`pythra_motion/package.json`)
Demonstrates registering multiple JavaScript modules where one is a vendor dependency (`motion.js`) and the other is the PyThra engine (`animation_engine.js`):

```json
{
    "name": "pythra_motion",
    "version": "1.0.0",
    "description": "A Flutter-style animation plugin for Pythra powered by motion.dev",
    "package_type": "plugin",
    "dependencies": {
        "pythra": ">=0.1.0"
    },
    "author": {
        "name": "itsredx",
        "email": "ambashir02@gmail.com"
    },
    "license": "MIT",
    "python_modules": [
        "__init__",
        "widget",
        "controller",
        "motion_state",
        "easing",
        "types",
        "spring"
    ],
    "asset_dir": "render",
    "js_modules": {
        "Motion": "js/motion.js",
        "PythraMotion": "js/animation_engine.js"
    },
    "tags": ["animation", "motion", "transition", "gesture"]
}
```

#### Example 2: Markdown Renderer with Styles & Vendor Libs (`markdown_render/package.json`)
Demonstrates injecting vendor libraries (`marked`, `DOMPurify`, `hljs`), custom styles, and the main rendering engine:

```json
{
    "name": "pythra-markdown-render",
    "version": "1.0.0",
    "description": "A high-performance Markdown renderer plugin for Pythra using marked.js",
    "package_type": "plugin",
    "dependencies": {
        "pythra": ">=0.1.0"
    },
    "python_modules": [
        "__init__", 
        "widget", 
        "controller", 
        "renderer_state", 
        "style"
    ],
    "asset_dir": "render",
    "js_modules": {
        "marked": "js/vendor/marked.umd.js",
        "DOMPurify": "js/vendor/purify.min.js",
        "hljs": "js/vendor/highlight.min.js",
        "PythraMarkdownRender": "js/marked_engine.js"
    },
    "css_files": [
        "css/vendor/github-dark.min.css", 
        "css/styles.css"
    ],
    "tags": ["renderer", "markdown", "marked"]
}
```

---

## 4. Developing the Python Widget Layer

A PyThra plugin widget typically falls into one of two patterns:
1. **Container Wrapper Widget** (e.g. `MotionWidget`): Takes any existing PyThra `Widget` as a child and wraps it in interactive behavior.
2. **Dedicated Surface Widget** (e.g. `MarkdownRender`, `PythraVideoPlayer`): Provides a self-contained rendering surface with custom styles and properties.

### 4.1. Creating the `StatefulWidget` (`widget.py`)

The widget class provides the public constructor, stores immutably configured properties, and instantiates its `State`.

```python
# plugins/my_plugin/widget.py
from typing import Optional, Callable
from pythra import StatefulWidget, Key, Widget
from .state import MyPluginState
from .controller import MyPluginController
from .style import MyPluginStyle


class MyPluginWidget(StatefulWidget):
    """A custom interactive plugin widget for PyThra."""

    def __init__(
        self,
        key: Key,
        child: Optional[Widget] = None,
        controller: Optional[MyPluginController] = None,
        width: str = "100%",
        height: str = "auto",
        style: Optional[MyPluginStyle] = None,
        on_event: Optional[Callable[[dict], None]] = None,
    ):
        self.child = child
        self.controller = controller or MyPluginController()
        self.width = width
        self.height = height
        self.style = style or MyPluginStyle()
        self.on_event = on_event
        super().__init__(key=key)

    def createState(self):
        return MyPluginState()
```

---

### 4.2. Creating the `State` and `js_init` Bridge (`state.py`)

The `State` class coordinates:
- Attaching and detaching the controller.
- Registering event callbacks with PyThra's IPC bridge (`framework.api.register_callback`).
- Generating the `_cached_js_init` specification.
- Rendering a `Container` with the `js_init` parameter.

```python
# plugins/my_plugin/state.py
import json
from typing import Optional
from pythra import State, Container, Key, Framework

framework = Framework.instance()


class MyPluginState(State):
    def __init__(self):
        super().__init__()
        self._cached_js_init = None
        self._callback_name = None

    def initState(self):
        widget = self.widget
        if not widget:
            return

        # 1. Attach controller to this State instance
        if widget.controller:
            widget.controller._attach(self)

        # 2. Register callback with PyThra IPC if listening for JS events
        self._callback_name = f"my_plugin_cb_{widget.key.value}"
        if framework and hasattr(framework, "api") and framework.api:
            framework.api.register_callback(
                self._callback_name, 
                self._handle_client_event
            )

    def dispose(self):
        widget = self.widget
        # Detach controller
        if widget and widget.controller:
            widget.controller._detach()

        # Unregister callback
        if widget and framework and hasattr(framework, "api") and framework.api:
            cb_id = f"my_plugin_cb_{widget.key.value}"
            if cb_id in framework.api.callbacks:
                del framework.api.callbacks[cb_id]

        super().dispose()

    def _handle_client_event(self, event_json_or_data):
        """Dispatches incoming IPC data from JavaScript to Python listeners."""
        try:
            event = json.loads(event_json_or_data) if isinstance(event_json_or_data, str) else event_json_or_data
            widget = self.widget
            if widget and widget.on_event:
                widget.on_event(event)
            if widget and widget.controller:
                widget.controller._notify_listeners(event.get("type"), event.get("data"))
        except Exception as e:
            print(f"Error handling event in MyPluginState: {e}")

    def execute_action(self, action_name: str, payload: dict):
        """Sends an imperative command to the JavaScript engine."""
        if not framework or not framework.window:
            return

        widget = self.widget
        if not widget:
            return

        instance_name = f"{widget.key.value}_MyPluginEngine"
        payload_js = json.dumps(payload)

        # Evaluate JavaScript directly on the client instance
        js = f"""
            (function(){{
                const inst = (window._pythra_instances && window._pythra_instances['{instance_name}']);
                if (inst && typeof inst.{action_name} === 'function') {{
                    inst.{action_name}({payload_js});
                }} else {{
                    console.warn("MyPlugin instance '{instance_name}' not ready or missing method '{action_name}'");
                }}
            }})();
        """
        window_id = getattr(self, "_window_id", framework.id)
        framework.window.evaluate_js(window_id, js)

    def build(self):
        widget = self.widget
        if not widget:
            return Container(width=0, height=0)

        # Memoize the js_init configuration
        if self._cached_js_init is None:
            instance_name = f"{widget.key.value}_MyPluginEngine"
            self._cached_js_init = {
                "engine": "MyPluginEngine",        # Matches the global window[engine] class name
                "instance_name": instance_name,    # Registered in window._pythra_instances
                "options": {
                    "instanceId": instance_name,
                    "callback": self._callback_name,
                    "style": widget.style.to_dict() if hasattr(widget.style, "to_dict") else {},
                }
            }

        return Container(
            key=Key(f"{widget.key.value}_container"),
            width=widget.width,
            height=widget.height,
            js_init=self._cached_js_init,
            child=widget.child,
        )
```

---

### 4.3. Implementing the Controller (`controller.py`)

A clean controller isolates framework internals from developers who use your plugin:

```python
# plugins/my_plugin/controller.py
from typing import Optional, Callable, Dict, List


class MyPluginController:
    """Controller for programmatically interacting with MyPluginWidget."""

    def __init__(self):
        self._state = None
        self._listeners: Dict[str, List[Callable]] = {}

    def _attach(self, state):
        self._state = state

    def _detach(self):
        self._state = None

    def add_listener(self, event_type: str, callback: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def _notify_listeners(self, event_type: str, data: any):
        for callback in self._listeners.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Error in MyPluginController listener: {e}")

    def trigger_action(self, action_name: str, payload: Optional[dict] = None):
        """Invoke an action on the active client-side engine."""
        if self._state:
            self._state.execute_action(action_name, payload or {})
        else:
            print("Warning: MyPluginController is not attached to any mounted widget.")
```

---

## 5. Developing the JavaScript Engine Layer

PyThra's DOM Reconciler relies on a standardized JavaScript contract. When a widget containing `js_init` is mounted into the DOM, the Framework automatically executes:

```javascript
window._pythra_instances[instance_name] = new window[engine_name](targetElement, options);
```

### 5.1. Engine Class Contract

Create your engine file in `render/js/my_engine.js`:

```javascript
// plugins/my_plugin/render/js/my_engine.js

(function () {
    "use strict";

    class MyPluginEngine {
        /**
         * @param {HTMLElement|string} elementOrId - The DOM element or HTML element ID
         * @param {Object} options - Configuration options passed from Python's js_init
         */
        constructor(elementOrId, options) {
            this.elementOrId = elementOrId;
            this.options = options || {};
            this.instanceId = options.instanceId;
            this.callbackName = options.callback;

            // Wait for DOM to finish settling before accessing elements
            setTimeout(() => this.init(), 0);
        }

        init() {
            this.container = typeof this.elementOrId === 'string'
                ? document.getElementById(this.elementOrId)
                : this.elementOrId;

            if (!this.container) {
                console.error(`[MyPluginEngine] Container not found:`, this.elementOrId);
                return;
            }

            // Register this instance globally for Python IPC lookups
            window._pythra_instances = window._pythra_instances || {};
            window._pythra_instances[this.instanceId] = this;

            // Build UI or initialize third-party library
            this._setupDOM();
            this._attachEvents();
        }

        _setupDOM() {
            this.innerView = document.createElement("div");
            this.innerView.className = "my-plugin-inner-surface";
            
            if (this.options.style) {
                Object.assign(this.innerView.style, this.options.style);
            }
            
            this.container.appendChild(this.innerView);
        }

        _attachEvents() {
            this._clickHandler = (e) => {
                // Send event data back to Python
                this.emitToPython("click", {
                    clientX: e.clientX,
                    clientY: e.clientY,
                    target: e.target.tagName
                });
            };

            this.innerView.addEventListener("click", this._clickHandler);
        }

        /**
         * Dispatches events to Python via PyThra IPC.
         */
        emitToPython(type, data) {
            if (!this.callbackName) return;

            const payload = JSON.stringify({ type: type, data: data });

            // Support both standard QWebChannel and PyWebView APIs
            if (typeof QWebChannel !== "undefined" && window._pywebviewChannel?.objects?.pywebview) {
                window._pywebviewChannel.objects.pywebview.call_callback(this.callbackName, payload);
            } else if (window.pywebview && typeof window.pywebview.call_callback === "function") {
                window.pywebview.call_callback(this.callbackName, payload);
            } else {
                console.warn("[MyPluginEngine] PyThra Bridge not ready. Event dropped:", type, data);
            }
        }

        /**
         * Method called imperatively from Python via evaluate_js
         */
        updateData(payload) {
            if (this.innerView) {
                this.innerView.textContent = JSON.stringify(payload);
            }
        }

        /**
         * Mandatory cleanup method called before reconciliation replaces/destroys the widget
         */
        destroy() {
            if (this.innerView && this._clickHandler) {
                this.innerView.removeEventListener("click", this._clickHandler);
            }
            if (this.container && this.innerView) {
                this.innerView.remove();
            }
            this.container = null;
            this.innerView = null;
        }
    }

    // Register on the global window scope
    window.MyPluginEngine = MyPluginEngine;
})();
```

---

## 6. Real-World Case Studies

### Case Study 1: `pythra_motion` (Declarative Animations & Gestures)
- **Problem**: Python cannot drive 60 FPS animations directly over IPC due to bridge latency.
- **Solution**: Python defines declarative keyframe specifications (`entrance_animation`, `hover_animation_enter`, `scroll_animation`). The Python widget emits these configurations into `js_init`. On the browser side, `animation_engine.js` runs `motion.dev` compiled into JavaScript.
- **Controller Features**: `controller.start_animation(...)`, `controller.start_stagger(...)`, and `controller.stop_animation(...)` evaluate single-line JavaScript commands targeting the registered instance:
  ```python
  js = f"window._pythra_instances['{instance_name}'].startAnimation({kf_json}, {opts_json});"
  framework.window.evaluate_js(window_id, js)
  ```

### Case Study 2: `markdown_render` (XSS Sanitization & Syntax Highlighting)
- **Problem**: Rendering complex Markdown with client-side syntax highlighting without stalling Python.
- **Solution**: The plugin manifest defines 3 vendor scripts and 2 CSS stylesheets:
  ```json
  "js_modules": {
      "marked": "js/vendor/marked.umd.js",
      "DOMPurify": "js/vendor/purify.min.js",
      "hljs": "js/vendor/highlight.min.js",
      "PythraMarkdownRender": "js/marked_engine.js"
  },
  "css_files": [
      "css/vendor/github-dark.min.css", 
      "css/styles.css"
  ]
  ```
- **Dynamic Updates**: When the document text changes, Python calls `controller.set_markdown(new_text)`. The JavaScript engine calls `marked.parse()`, cleanses with `DOMPurify.sanitize()`, injects the HTML, and highlights code blocks with `hljs.highlightElement()`.

### Case Study 3: `pythra_video_player` (Media Streaming & Canvas Overlay)
- **Problem**: Fast multimedia rendering across Linux, Windows, and macOS without desktop window tearing.
- **Solution**: A local WebSocket server streams encoded frames directly to an HTML5 Canvas. The plugin's JavaScript engine listens to WebSocket binary messages, constructs an `ImageBitmap`, and paints to `<canvas>` via `requestAnimationFrame`.
- **Bidirectional Controls**: When the user seeks or changes volume using mouse gestures in the browser, `sendCommand("seek", ratio)` sends the event straight to Python using `pywebview.on_video_command(...)`.

---

## 7. Enabling and Consuming Plugins in Applications

### 7.1. Declarative Registration in `config.yaml`

PyThra enforces declarative plugin whitelisting. Place your plugin inside the `plugins/` directory of your project, and then declare it in `config.yaml`:

```yaml
# config.yaml
app_name: My Awesome App
win_width: 1280
win_height: 720
Debug: true

# Declare all active plugins here:
plugins:
  - pythra_motion
  - markdown_render
  - my_custom_plugin
```

> [!IMPORTANT]
> **Whitelisting Enforcement & Import Guard**:
> If a plugin is present in the `plugins/` folder but **omitted** from `config.yaml`:
> 1. It is **skipped** during discovery and will not be loaded into the framework.
> 2. Its static assets will **not** be served by `AssetServer` (requests return HTTP 404).
> 3. Its JavaScript modules will **not** be injected into the page.
> 4. Python attempts to import it (`from plugins.my_custom_plugin import ...`) are intercepted by [`PluginImportGuard`](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/package_manager.py) and raise an `ImportError`.

---

### 7.2. Using the Plugin in Application Code

Import the plugin directly from the `plugins` namespace:

```python
# lib/main.py
from pythra import StatelessWidget, Container, Column, Text, Key, runApp
from plugins.my_custom_plugin.widget import MyPluginWidget
from plugins.my_custom_plugin.controller import MyPluginController


class HomePage(StatelessWidget):
    def __init__(self):
        self.controller = MyPluginController()
        super().__init__()

    def _on_plugin_event(self, event):
        print("Received event from client:", event)

    def build(self):
        return Container(
            padding="24px",
            child=Column(
                children=[
                    Text("PyThra Plugin Demo", style={"fontSize": "24px"}),
                    MyPluginWidget(
                        key=Key("my_plugin_demo"),
                        controller=self.controller,
                        width="100%",
                        height="300px",
                        on_event=self._on_plugin_event,
                    ),
                ]
            )
        )

if __name__ == "__main__":
    runApp(HomePage())
```

---

## 8. Hot Reload Behavior with Plugins

PyThra supports state-preserving hot reload for plugins:
- **Configuration Reloading**: Saving changes to `config.yaml` automatically reloads the whitelist via `package_manager.set_enabled_plugins()`.
- **Python Logic Updates**: Edits to plugin Python code are immediately reloaded into `sys.modules`, and widget classes are rebound to existing states.
- **Client DOM Reconciliation**: When a widget rebuilds with modified `js_init` options or style properties, PyThra's reconciler cleanly dispatches updates to the DOM without tearing down unrelated components.

---

## 9. Plugin Development Checklist & Best Practices

1. **Naming Conventions**:
   - Directory name in `plugins/` should use `snake_case` (e.g., `pythra_motion`, `markdown_render`).
   - Package name in `package.json` can use `kebab-case` or `snake_case`. Both are recognized by PyThra's whitelist matcher.
2. **Stable Keys**:
   - Always assign explicit, unique `Key` instances to plugin widgets (e.g. `key=Key("editor_view")`) to ensure the DOM Reconciler preserves state and doesn't recreate the container.
3. **DOM Cleanup**:
   - Always implement a `destroy()` method on your JavaScript engine class to remove event listeners, close WebSockets/timers, and avoid client memory leaks.
4. **XSS & Security**:
   - Never inject unsanitized HTML into the DOM. Use libraries like `DOMPurify` before writing to `innerHTML`.
5. **Asset Paths**:
   - Place all web files inside `render/` and reference them in `package.json` relative to `asset_dir`. They will be served at `http://localhost:<port>/packages/<plugin_name>/...`.