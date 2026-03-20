# Theming and Dynamic Colors
Relevant source files
- [src/pythra/pythra/__pycache__/__init__.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/__init__.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/base.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/base.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/core.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/core.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/styles.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/styles.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/widgets.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/widgets.cpython-312.pyc)
- [src/pythra/pythra/core.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py)
- [src/pythra/pythra/project_template/render/js/pythra_bridge.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js)
- [src/pythra/pythra/widgets.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py)

The PyThra styling system is a Flutter-inspired declarative model that bridges Python-defined theme objects to web-standard CSS variables and classes. It enables dynamic light/dark mode switching, animated backgrounds, and efficient CSS delivery through a shared-style registry.

## ThemeData and ThemeManager

The `ThemeData` class serves as the central configuration for an application's visual identity, defining color roles (primary, secondary, surface), typography, and component-specific themes (e.g., `SliderTheme`, `SwitchTheme`) [src/pythra/pythra/__init__.py10](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py#L10-L10)

The `ThemeManager` is a singleton responsible for managing the active `ThemeData` and coordinating the injection of these styles into the `QWebEngineView`.

### Data Flow: Theme to CSS

When a theme is applied, the `ThemeManager` converts the `ThemeData` attributes into a block of CSS root variables. This process ensures that widgets can reference abstract roles like `--md-sys-color-primary` rather than hardcoded hex values.
ComponentRoleSource`ThemeData`Holds color palettes and component styles.[src/pythra/pythra/__init__.py10](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py#L10-L10)`ThemeManager`Tracks current theme (Light/Dark) and generates CSS.[src/pythra/pythra/core.py41](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L41-L41)`Color.adaptive()`Registers colors that change based on the active theme.[src/pythra/pythra/styles.py1-5](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L1-L5)
**Sources:**[src/pythra/pythra/__init__.py10](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py#L10-L10)[src/pythra/pythra/core.py41](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L41-L41)[src/pythra/pythra/styles.py1-5](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L1-L5)

## Dynamic Colors and Adaptive Registration

PyThra supports dynamic color updates through `Color.adaptive()`. This mechanism registers a CSS variable in the webview that can be updated globally without re-rendering the entire widget tree.

### Adaptive Color Implementation

1. **Registration**: When `Color.adaptive(light, dark)` is called, it generates a unique CSS variable name.
2. **Injection**: The `ThemeManager` includes these variable definitions in the global `<style>` tag injected into the `index.html`[src/pythra/pythra/core.py151-152](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L151-L152)
3. **Switching**: When the framework toggles between light and dark modes, the values assigned to these CSS variables are updated, causing an immediate visual change in the browser layer.

**Sources:**[src/pythra/pythra/styles.py1-5](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L1-L5)[src/pythra/pythra/core.py151-152](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L151-L152)

## Animated Backgrounds: GradientTheme

The `GradientTheme` class allows for the creation of complex, animated linear or radial gradients. These are specifically integrated into the `Container` widget [src/pythra/pythra/widgets.py122-126](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L122-L126)

### Gradient Properties

- **gradientColors**: A list of colors to transition between [src/pythra/pythra/widgets.py123](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L123-L123)
- **animationSpeed**: Defines the duration of the CSS animation (e.g., "3s") [src/pythra/pythra/widgets.py124](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L124-L124)
- **to_css()**: Converts the Python parameters into a `linear-gradient` or `radial-gradient` string with associated CSS animation keyframes.

**Sources:**[src/pythra/pythra/widgets.py122-126](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L122-L126)[src/pythra/pythra/widgets.py179](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L179-L179)

## CSS Injection and Shared Styles

To optimize performance, PyThra uses a "Shared Style" registry. Instead of inlining styles on every HTML element, the `Reconciler` and `Widget` classes collaborate to generate unique CSS classes based on a hash of the widget's properties.

### The Style Pipeline

The following diagram illustrates how a Python `Container` definition is transformed into a CSS rule and injected into the webview.

**Theme Injection Pipeline**

```
Webview Space (DOM)

Bridge Layer

Python Space (Logic)

make_hashable()

Lookup/Register

Generate

Framework.css_file_path

Root Variables

Link Tag

applyPatches

classList.add()

Container(decoration=BoxDecoration)

style_key (Tuple)

shared_styles (Dict)

CSS Rule (.shared-container-hash)

styles.css

ThemeManager

index.html

PythraBridge.js

DOM Element

Applied Style
```

**Sources:**[src/pythra/pythra/widgets.py139-160](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L139-L160)[src/pythra/pythra/core.py152](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L152-L152)[src/pythra/pythra/project_template/render/js/pythra_bridge.js161-176](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L161-L176)

### Shared Style Logic

- **Style Hashing**: Every `Container` or styled widget generates a `style_key` by hashing its visual properties using `make_hashable`[src/pythra/pythra/widgets.py194-213](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L194-L213)
- **Registry**: If the hash exists in `shared_styles`, the widget reuses the existing class name [src/pythra/pythra/widgets.py139](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L139-L139)
- **Patching**: The `PythraBridge.js` receives the class name in the `UPDATE` or `INSERT` patch and applies it via `el.classList.add(newClass)`[src/pythra/pythra/project_template/render/js/pythra_bridge.js174](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L174-L174)

## System Entity Mapping

The following table maps conceptual theming components to their implementation entities in the codebase.
ConceptCode EntityFile Path**Theme Registry**`ThemeManager`[src/pythra/pythra/theme.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/theme.py)**Style Hashing**`make_hashable`[src/pythra/pythra/base.py53-87](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L53-L87)**CSS Injection**`Framework._ensure_default_assets`[src/pythra/pythra/core.py149](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L149-L149)**DOM Styling**`PythraBridge.updateProps`[src/pythra/pythra/project_template/render/js/pythra_bridge.js161](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L161-L161)**Animated Gradients**`GradientTheme`[src/pythra/pythra/styles.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py)
**Theming Architecture Diagram**

```
Styles injected for

Updates classList

Framework

+ThemeManager theme_manager

+Config config

+_ensure_default_assets()

ThemeManager

+ThemeData current_theme

+set_theme(ThemeData)

+get_css_variables()

Container

+GradientTheme gradient

+BoxDecoration decoration

+style_key : Tuple

+generate_css_rule()

PythraBridge_JS

+updateProps(el, props)

+handleUpdate(html_id, data)

Widget
```

**Sources:**[src/pythra/pythra/core.py81-105](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/core.py#L81-L105)[src/pythra/pythra/widgets.py73-137](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets.py#L73-L137)[src/pythra/pythra/project_template/render/js/pythra_bridge.js1-15](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/pythra_bridge.js#L1-L15)