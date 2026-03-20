# Creating and Using Plugins
Relevant source files
- [PACKAGE_SYSTEM_README.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md)

PyThra features a comprehensive package management system inspired by `pub.dev`, allowing developers to extend the framework with custom widgets, themes, and interactive JS-driven components. Plugins are self-contained directories containing metadata, Python logic, and JavaScript engines that the Framework orchestrates to provide rich functionality like the Markdown Editor.

### Plugin Architecture Overview

The plugin system relies on the `PackageManager` to discover, validate, and load external modules. A plugin typically consists of a manifest file, a Python implementation of widgets, and a JavaScript engine to handle client-side interactivity.

#### Data Flow: Plugin Initialization to Execution

The following diagram illustrates how the `Framework` interacts with the `PackageManager` and `AssetServer` to load a plugin.

**Plugin Loading and Registration Pipeline**

```

```

Sources: [pythra/core.py150-180](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/core.py#L150-L180)[pythra/package_manager.py45-80](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/package_manager.py#L45-L80)[pythra/package_security.py20-50](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/package_security.py#L20-L50)

---

### 1. The Plugin Manifest (`package.json`)

Every modern PyThra plugin must include a `package.json` file. This replaces the legacy `pythra_plugin.py` format and provides structured metadata for dependency resolution and security.
FieldDescription`name`Unique identifier for the package (e.g., `pythra_markdown_editor`).`version`Semantic version string.`package_type`Enum value: `plugin`, `widgets`, `theme`, or `utility`.`js_modules`Mapping of Global JS Variable names to their local file paths.`dependencies`Dictionary of required packages and version constraints.`checksums`SHA256 hashes of files for integrity verification.
**Example Manifest Structure:**[PACKAGE_SYSTEM_README.md103-125](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L103-L125)

Sources: [pythra/package_system.py15-45](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/package_system.py#L15-L45)[PACKAGE_SYSTEM_README.md103-125](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L103-L125)

---

### 2. Python Widget Implementation

Plugins define widgets by inheriting from `StatelessWidget` or `StatefulWidget`. For interactive components, the Python class serves as a bridge, passing properties to the JavaScript engine via `render_props`.

#### The Markdown Editor Pattern

The `MarkdownEditor` plugin demonstrates a complex interaction between a Python `StatefulWidget` and a specialized controller.

- **MarkdownEditingController**: Manages the text state and selection. It provides methods like `insert_text` or `toggle_bold` which update the internal `TextEditingController`.
- **MarkdownToolbarItem**: A helper widget that triggers controller actions.

**Class Relationship: Markdown Editor**

```

```

Sources: [plugins/markdown/widgets.py10-150](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/plugins/markdown/widgets.py#L10-L150)[pythra/material/input.py20-60](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/material/input.py#L20-L60)

---

### 3. JavaScript Engine Integration

For widgets requiring direct DOM manipulation (like a Markdown previewer or a code editor), a JS engine is required.

1. **JS Module Registration**: Defined in `package.json` under `js_modules`.
2. **Initialization**: The `Framework` detects the widget type in the render tree and ensures the corresponding JS file is loaded in the `QWebEngineView`.
3. **Event Bridge**: JS components use `PythraBridge` to communicate events (like `on_change`) back to the Python `State` via `pywebview.api`.

**JS Engine Communication Flow**

```

```

Sources: [render/js/pythra_bridge.js50-120](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/render/js/pythra_bridge.js#L50-L120)[pythra/api.py30-55](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/api.py#L30-L55)[pythra/core.py400-430](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/core.py#L400-L430)

---

### 4. Step-by-Step: Authoring a Plugin

To create a new plugin (e.g., a custom Charting widget):

1. **Create Directory**: Place it in the `plugins/` directory of your project.
2. **Define Manifest**: Create `package.json`.

- Specify `package_type: "plugin"`.
- Map `MY_CHART_ENGINE: "js/charts.js"`.
3. **Write Python Logic**:

- Create `widgets.py`.
- Implement a class `PythraChart(Widget)`.
- In `render_props()`, include a `type: "my_chart"` key so the JS bridge can identify it.
4. **Write JS Engine**:

- Create `js/charts.js`.
- Add a listener or initializer to the global `PythraBridge` to handle the `my_chart` type.
5. **Security Validation**:

- Run `pythra package validate <path>` to ensure the plugin meets safety standards.

**Validation Logic**:
The `PackageSecurity` module performs AST (Abstract Syntax Tree) scanning on the Python code to block dangerous calls like `os.system` or `eval` before the plugin is allowed to load.

Sources: [pythra/package_security.py85-115](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/package_security.py#L85-L115)[pythra/package_manager.py110-130](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/package_manager.py#L110-L130)[PACKAGE_SYSTEM_README.md134-138](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L134-L138)

---

### 5. Using Plugins in an App

Once a plugin is discovered, it can be imported like any other Python module. The `Framework` handles the injection of necessary CSS and JS assets automatically during the first render of the widget.

```

```

**Plugin Discovery Mechanism**:
The `PackageManager` searches three locations in order:

1. The local `plugins/` folder in the project root.
2. Python `site-packages` (for pip-installed plugins).
3. The internal `pythra` package directory.

Sources: [pythra/package_manager.py150-185](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/package_manager.py#L150-L185)[pythra/core.py160-175](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pythra/core.py#L160-L175)