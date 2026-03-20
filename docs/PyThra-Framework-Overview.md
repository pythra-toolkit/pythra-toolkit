# PyThra Framework Overview
Relevant source files
- [CHANGELOG.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md)
- [README.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md)
- [assets/demo.gif](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/assets/demo.gif)
- [pyproject.toml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml)
- [src/pythra/pythra/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py)
- [src/pythra/pythra/__pycache__/__init__.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/__init__.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/styles.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/styles.cpython-312.pyc)
- [src/pythra/pythra/window/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/__init__.py)
- [src/pythra/setup.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py)

PyThra is a declarative UI framework for building modern desktop applications using Python. It employs a hybrid architecture where the application logic and state management reside in Python, while the UI is rendered via a high-performance HTML/CSS/JS engine within a PySide6 `QWebEngineView`.

Inspired by **Flutter**, PyThra uses a reactive component model where the UI is described as a function of the application state. When state changes occur, the framework performs a "reconciliation" (diffing) process to apply only the necessary patches to the DOM, ensuring high performance and a smooth developer experience.

## Core Philosophy

- **Declarative UI:** You describe *what* the UI should look like for a given state, not *how* to change it.
- **Composition over Inheritance:** Build complex interfaces by nesting small, reusable widgets.
- **Python-First:** Logic, styling, and structure are defined in pure Python, abstracting away the underlying web technologies.
- **Performance:** Utilizes Cython-accelerated diffing and a specialized JS bridge to minimize overhead between the Python backend and the webview frontend.

## High-Level Architecture

The framework consists of three primary layers: the **Python Framework Layer**, the **Communication Bridge**, and the **JavaScript Rendering Layer**.

### System Map: Python to Code Entity

The following diagram maps the high-level system concepts to the specific classes and files that implement them in the codebase.

```

```

Sources: [src/pythra/pythra/__init__.py10-36](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py#L10-L36)[src/pythra/pythra/core.py11-12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L11-L12)[src/pythra/pythra/base.py16-21](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L16-L21)

## Major Subsystems

### 1. The Framework Orchestrator

The `Framework` class is a singleton that manages the application lifecycle. It initializes the PySide6 application, starts the local `AssetServer` to provide HTML/JS resources, and maintains the main `QWebEngineView` window.

- **Key Entry Point:**`Framework().run()` starts the event loop.
- **Root Management:**`Framework().set_root(widget)` defines the top-level UI component.

For details, see [Framework Lifecycle and Orchestration](/pythra-toolkit/pythra-toolkit/2.1-framework-lifecycle-and-orchestration).

### 2. Declarative Model & State Management

PyThra uses `StatelessWidget` and `StatefulWidget` to define UI components.

- **StatelessWidget:** Immutable widgets that only depend on their configuration.
- **StatefulWidget:** Widgets that maintain a persistent `State` object across rebuilds. Calling `self.setState()` triggers the reconciliation pipeline.

For details, see [Key Concepts and Terminology](/pythra-toolkit/pythra-toolkit/1.2-key-concepts-and-terminology) and [State Management](/pythra-toolkit/pythra-toolkit/2.2-state-management).

### 3. Reconciliation and Patching

The `Reconciler` compares the "Old Widget Tree" with the "New Widget Tree" generated after a state change. It produces a list of `Patch` operations (INSERT, REMOVE, UPDATE, MOVE, REPLACE). These patches are serialized via `orjson` and sent to the browser.

- **Optimization:** Critical diffing logic is implemented in Cython (`reconciler_cython.pyx`) for near-native performance.

For details, see [Reconciler and Diffing Engine](/pythra-toolkit/pythra-toolkit/2.3-reconciler-and-diffing-engine).

### 4. Hybrid Rendering Bridge

The bridge facilitates bi-directional communication:

- **Python to JS:** Patches are sent via `QWebChannel` and executed by `pythra_bridge.js` to manipulate the DOM.
- **JS to Python:** User events (clicks, input) are captured in the browser and routed back to Python handlers via the `Api` class.

For details, see [Python–JavaScript Bridge](/pythra-toolkit/pythra-toolkit/2.4-python-javascript-bridge).

## Code Entity Space: Widget Implementation

This diagram shows how a Python Widget definition relates to the generated HTML and the JavaScript logic that manages interactivity.

```
Web Space

Bridge

Python Space

render_props()

to_css()

applyPatches()

event

callback

Widget (widgets.py)

Style (styles.py)

Patch (JSON)

HTML Element

CSS Rule

JS Engine (e.g., slider.js)
```

Sources: [src/pythra/pythra/widgets.py101-174](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L101-L174)[src/pythra/pythra/styles.py41-84](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L41-L84)

## Framework Directory Structure

When you create a project using `pythra create-project`, the following structure is generated:
Directory/FilePurpose`lib/main.py`The application entry point where the root widget is defined.`assets/`Static files like images, fonts, and local icons.`render/`The webview environment: `index.html`, `styles.css`, and `js/` engines.`config.yaml`Metadata including `app_id`, `app_name`, and window settings.`windows/`, `macos/`, `linux/`Platform-specific metadata and icon files.
For details, see [Getting Started](/pythra-toolkit/pythra-toolkit/1.1-getting-started).

## Navigation and Tooling

- **Navigation:** A stack-based `Navigator` manages `PageRoute` objects, supporting asynchronous preloading of views to eliminate transition latency. See [Navigator and PageRoute API](/pythra-toolkit/pythra-toolkit/5.1-navigator-and-pageroute-api).
- **CLI:** The `pythra` command-line tool handles project scaffolding, icon generation, and packaging via PyInstaller. See [CLI and Project Tooling](/pythra-toolkit/pythra-toolkit/7-cli-and-project-tooling).

---

**Next Steps:**

- To set up your environment, go to [Getting Started](/pythra-toolkit/pythra-toolkit/1.1-getting-started).
- To learn about the core building blocks, see [Key Concepts and Terminology](/pythra-toolkit/pythra-toolkit/1.2-key-concepts-and-terminology).