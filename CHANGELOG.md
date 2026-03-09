# PyThra Framework - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [0.1.22] - 2026-03-10

Cross-platform icon system, CLI project management commands, widget enhancements, TextField styling overhaul, and Cython Key extension.

### ✨ New Features

* **Cross-Platform Icon System:**
  * New `pythra generate-icons <source.png>` CLI command — one-step generation of all platform icons from a single PNG.
  * Creates Windows `.ico` (7 sizes: 16–256px), macOS `.icns` (7 sizes: 16–1024px), and Linux FreeDesktop hicolor PNGs (8 sizes: 16–512px).
  * Flutter-style platform directories: `windows/`, `macos/`, `linux/` added to project template alongside `assets/`, `render/`, `plugins/`.
  * `.desktop` and `Info.plist` metadata files generated with project-specific values (not hardcoded placeholders).
  * New `app_id` field in `config.yaml` (default: `com.pythra.{project-name}`) for Windows `AppUserModelID`, Linux `StartupWMClass`, and macOS `CFBundleIdentifier`.

* **`pythra upgrade` CLI Command:**
  * Brings existing PyThra projects up to date with the current template version.
  * **Render sync:** Updates JS engines, CSS, and loaders from the installed template. Skips `index.html`/`styles.css` (user-generated). Only replaces files whose content actually differs.
  * **Platform icon generation:** Generates `windows/`, `macos/`, `linux/` dirs dynamically with project-specific `app_name` and `app_id` derived from the directory name. Respects user-set config values.
  * **Config merge:** Adds new config keys (e.g. `app_id`) to `config.yaml` without overwriting existing user values. Derives `app_name` from project directory name (e.g. `new-app` → `New App`).
  * Supports `--dry-run`, `--force`, `--skip-render`, `--skip-icons`, `--skip-config` flags.

* **`pythra install-linux` CLI Command:**
  * Installs `.desktop` file to `~/.local/share/applications/` and hicolor icons to `~/.local/share/icons/hicolor/`.
  * Rewrites `Exec=` to point to the actual executable (`python3 /path/to/lib/main.py` during dev, or `--exec /path/to/binary` for compiled builds).
  * Renames icon files to `{app_id}.png` for FreeDesktop theme lookup.
  * Runs `gtk-update-icon-cache` if available.

* **`pythra create-project` Enhanced:**
  * Now generates platform dirs dynamically with project-specific identity instead of copying hardcoded templates.
  * Customize `config.yaml` with real `app_name` and `app_id` derived from the project directory name at creation time.

### 🎨 Widget Improvements

* **`Container`:** Added `cssPosition` parameter for explicit CSS `position` control (e.g. `relative`, `absolute`, `fixed`, `sticky`).
* **`IconButton`:** Added `zAxisIndex` parameter (default: `1000`) for z-index control. Included in style key and CSS generation.
* **`TextField` / `InputDecoration` Overhaul:**
  * Added `inputStyle` parameter to `InputDecoration` for controlling the input text's font size, family, and color independently from the label.
  * Added `hintStyle.fontFamily` and `hintStyle.color` support — previously only `fontSize` was extracted.
  * Added `labelStyle.color` support — label color now respects `labelStyle.color` with fallback to `labelColor`.
  * **Filled vs Outlined mode:** Border rendering now respects the `filled` property — `filled=True` only shows bottom border (Material filled style), `filled=False` shows full outline borders on all sides including focus states.
  * Placeholder visibility: When a `label` is present, placeholder is hidden until focus. When no label, placeholder shows immediately with configured hint styles.
  * Focus borders now rendered on all sides for outlined (non-filled) text fields.

### 🐛 Bug Fixes

* **`Switch`:** Fixed `onPressed` handler — was incorrectly referencing `self.onChanged` instead of `self.onPressed` in `get_interactivity()`.
* **`State`:** Removed unused `syncState()` method.
* **`webwidget.py`:** Fixed `NameError: name 'Path' is not defined` crash in `_setup_platform_icon()`. Added `app is None` guard for CLI-only invocations.

### 🚀 Performance & Architecture

* **`Key_cython` Cython Extension:**
  * Renamed `key.pyx` → `key_cython.pyx` and `Key` → `Key_cython` class to follow Cython naming convention (matching `reconciler_cython`).
  * Added to both `pythra-toolkit/setup.py` and `pythra-toolkit/src/pythra/setup.py` for compilation with `-O3` optimization.

* **Linux Wayland Auto-Install (`webwidget.py`):**
  * `_setup_platform_icon()` now auto-installs `.desktop` file and hicolor icons to `~/.local/share/` on each app startup.
  * Eliminates the Wayland gear icon — `setWindowIcon()` is ignored by Wayland, so full FreeDesktop integration is required.
  * Detects compiled binaries via `sys.frozen` and uses the binary path for `Exec=` in the .desktop file.

* **Build Command Enhancements (`pythra build`):**
  * Auto-detects platform icons if `--icon` not provided (`windows/appIcon.ico` on Windows, `macos/appIcon.icns` on macOS).
  * macOS builds use `--macos-create-app-bundle` + `--macos-app-icon` for native `.app` bundles.
  * Platform directories auto-included in the build alongside `assets/`, `render/`, `plugins/`.

### 📦 Packaging & Cleanup

* Added `Pillow>=10.0.0` as a dependency for icon generation.
* Updated `pyproject.toml` package-data with platform directory patterns (`.icns`, `.desktop`, `.plist`, `.png`).
* Updated `MANIFEST.in` to include platform directories in source distributions.
* Removed unused `pythra/cli/` directory (old duplicate of `pythra_cli/`).

---
## [0.1.21] - 2026-02-20

Performance updates: Optimized ClipPath generation and Responsive VirtualGridViews

- **VirtualGridView**:
    - **UI Responsiveness:** Virtual grids now fluidly shrink and expand their column capacity on the client-side based on the `childMinWidth` parameter, bypassing static limits.
    - **Reconciliation Streamlining:** Converted grid element debug messages from standard `print` statements into wrapped `debug_print` commands, silencing heavy terminal spam while virtual items lazy load.

- **ClipPath**:
    - **Pro Blueprint Pattern**: Resolved massive client-side sluggishness and unstyled items loading from memory. The framework now serializes each ClipPath structure identically (hashing `viewBox`, `radius`, `points`, `width`, `height`), attaching exactly *one* shared layout ruleset `<style>` tag and *one* Javascript `ResizeObserver` per unique configuration.
    - **Network Caching:** The core Python engine caches successfully transmitted rendering hashes inline via `_clip_blueprint_registry`, entirely terminating duplicate Javascript generation cycles across arbitrarily large datasets.

---
## [0.1.20] - 2026-02-16

Feature updates: VirtualGridView, Responsive Layouts, and Core Enhancements

- **VirtualGridView**:
    - Implemented `VirtualGridView` widget for high-performance rendering of large grids.
    - Added `VirtualGridController` for programmatic control.
    - Created `PythraVirtualGrid` JS engine (`virtual_grid.js`) for client-side virtualization.
    - Added `childMinWidth` support for responsive grid layouts.

- **GridView**:
    - Added `childMinWidth` support to enabling responsive column calculations using CSS Grid `minmax`.

- **Scrollbar**:
    - Updated `render_props` to support `VirtualGridView` initialization.

- **Transform**:
    - Implemented `Transform` widget and `Matrix4` helper class.

- **VirtualListView**:
    - Applied fixes and improvements to virtualization logic.

- **ProgressIndicator**:
    - Fixed initialization and visibility toggling issues.

- **Core**:
    - Updated `core.py` to correctly analyze and load required JS engines.
    - Fixed JS engine loading logic in `_analyze_required_js_engines`.

- **Window**:
    - Added support for `min_win_width` and `min_win_height` configuration.

- **Styles**:
    - Added `Double` class for CSS constants.
    - Implemented `Border` class.
    - Updated `BoxDecoration` to support `Border`.
    - Added `Matrix4` helper.

- **State Management**:
    - Refactored `State` class to use `@property` for `widget` access.

- **Config**:
    - Added `min_win_width` and `min_win_height` to `config.yaml`.

---
## [0.1.19] - 2026-01-06

This release implements a major architectural overhaul of the bridge communication system, implementing a "Data-Driven" approach for vastly improved performance and stability during dynamic UI updates.

### 🚀 Performance & Architecture

* **Data-Driven Bridge:**
  * **Problem:** Previous versions generated large strings of JavaScript code on the Python side for every UI update, which was slow to generate and expensive for the browser to parse and execute.
  * **Solution:** Replaced ad-hoc JS generation with a structured JSON patch system. Python now sends a lightweight JSON payload describing the changes (patches), which is processed by a dedicated client-side `PythraBridge`.

* **High-Speed Serialization (`orjson`):**
  * **Optimization:** Swapped the standard `json` library for `orjson` (when available) for critical data paths. This results in significantly faster serialization of UI trees and bridge payloads.
  * **Sanitization:** Replaced the slow, recursive `_sanitize_for_json` method with a highly efficient `default` hook, eliminating a major bottleneck in the rendering loop.

* **Reconciler Cache Optimization:**
  * **Optimization:** The reconciler's HTML stub cache now uses deterministic, sorted JSON keys generated by `orjson`, reducing cache misses and ensuring consistent behavior.

### 🛠️ Fixed

* **Dynamic Widget Initialization:**
  * **Problem:** Interactive widgets like `ClipPath`, `Slider`, `VirtualList`, `Dropdown`, and `GestureDetector` were failing to initialize correctly after dynamic updates (e.g., navigation) because the bridge was not executing their specific JS initializers.
  * **Solution:** The `_generate_dom_patch_script` logic was expanded to fully support all interactive widget types, ensuring they are correctly hydrated on the client side after every patch.

---
## [0.1.18] - 2026-01-06

This release brings significant performance optimizations to navigation and rendering, including background page pre-building and persistent asset caching.

### 🚀 Performance & Optimizations

* **Navigator Preloading:**
  * Added `navigator.preload(route)`: Allows pre-building complex page widgets in the background thread *before* navigation occurs, making transitions instant.
  * Added `navigator.preloadPrevious()`: Automatically pre-builds the previous page in the stack, ensuring "Go Back" actions are immediate without re-rendering delay.
  * Implemented `Framework.build_subtree_async`: A core utility to safely build widget trees in background threads without blocking the UI.

* **Persistent Web Cache:**
  * Enabled persistent disk caching for `QtWebEngine`.
  * Fonts (like Material Icons) and other remote assets are now cached on disk, reducing network usage and speeding up subsequent app launches.

---
## [0.1.17] - 2026-01-06

This release introduces the new `DerivedDropdown` widget system with enhanced theming capabilities and fixes critical package structure issues that affected CLI functionality.

### ✨ New Features

* **Derived Menu & Theming System:**
  * **DerivedDropdown:** A new, highly customizable dropdown widget (`derived_widgets`) has been added.
  * **DerivedDropdownTheme:** Introduces `DerivedDropdownTheme` for consistent and flexible styling of dropdown menus, allowing developers to "start with the theme we created" for uniform UI design.
  * **Controller Support:** Added `DerivedDropdownController` for programmatic control over dropdown state.

### 🛠️ Fixed

* **CLI Module Import Errors:**
  * **Problem:** Running `pythra run` caused a `ModuleNotFoundError` for `pythra.pythra_cli` because the CLI module was incorrectly located as a sibling to the main package.
  * **Solution:** Moved `pythra_cli` inside the `pythra` package (`src/pythra/pythra/pythra_cli`) and updated the `pyproject.toml` entry point to `pythra.pythra_cli.main:app` (relative to the new package root).

* **Package Installation Structure:**
  * **Problem:** `setup.py` and `pyproject.toml` incorrectly treated `src` as the package root, causing internal import failures (e.g., `pythra.styles`) during editable installs.
  * **Solution:** Updated packaging configuration to use `src/pythra` as the package root directory.

* **Typo in Imports:**
  * Fixed a typo in `__init__.py` where `derived_widgets` was misspelled as `drived_widgets`.

---
## [0.1.16] - 2026-01-04

This release improves Linux compatibility by fixing Windows-specific import errors and handling optional power management dependencies gracefully.

### 🐛 Fixed

* **Crash on Linux due to Windows-specific imports:**
  * **Problem:** The application would crash on startup on Linux because `wmi` (a Windows-only library) was being imported unconditionally in `webwidget.py`.
  * **Solution:** The `wmi` import was moved inside the `watch_for_power_events` function, which is only executed on Windows.

* **Missing DBus Dependency Handling:**
  * **Problem:** On Linux systems without `dbus-python` installed, the application would crash due to a `ModuleNotFoundError` in `window_manager.py`.
  * **Solution:** Wrapped `dbus` imports in a try-except block. If `dbus-python` is missing, the application now logs a warning and disables sleep/resume detection instead of crashing. Added `dbus-python` as an optional dependency for Linux.

---
## [0.1.15] - 2025-11-19

This release addresses critical packaging configuration errors that prevented valid distribution metadata from being generated, and fixes the CI/CD pipeline triggers.

### 🐛 Fixed

* **Invalid Distribution Metadata:**
  * **Problem:** The build system was failing to associate the `src/` directory structure with the package metadata defined in `pyproject.toml` when `setup.py` was present. This resulted in wheels being built without a Name or Version (Metadata-Version issues).
  * **Solution:** Added `package_dir={'': 'src'}` to `setup.py` and configured `[tool.setuptools.packages.find]` in `pyproject.toml`. This forces `setuptools` to correctly map the source code to the package definition.

* **CI/CD Release Trigger:**
  * **Problem:** The GitHub Actions workflow was configured to check for release events but was not actually triggered by them. Creating a GitHub Release did not start the build/upload process.
  * **Solution:** Added `release: types: [published]` to the workflow triggers, ensuring deployment pipelines run automatically when a new release is published.

---
## [0.1.14] - 2025-11-18

This release brings significant performance improvements by ensuring the optimized C-extension is correctly built and distributed, alongside visual polish to icon rendering.

### 🚀 Performance & Build

* **Enabled Cython Reconciler Compilation:**
  * **Problem:** The high-performance Cython version of the reconciler (`reconciler_cython`) was not being compiled or included in the distribution wheel due to missing build configuration. This forced the framework to fall back to the slower pure-Python implementation.
  * **Solution:** Added a dedicated `setup.py` and updated `pyproject.toml` build-system requirements to include `Cython`. The build pipeline now correctly compiles the `.pyx` source into binary extensions (`.pyd`/`.so`), ensuring users get the intended high-speed UI updates.

### 🎨 UI & Rendering

* **Zero-Latency Icon Loading (Base64 Embedding):**
  * **Problem:** Material Icons were previously loaded via local HTTP requests. This caused a brief "Flash of Unstyled Text" (FOUT) where icon names (like "menu" or "home") were visible as text before the font file finished loading.
  * **Solution:** Font files are now read from the assets directory, converted to Base64 strings, and embedded directly into the generated CSS. This eliminates the file I/O delay during the render phase, ensuring icons appear instantly alongside the layout.

---

## [0.1.13] - 2025-11-17

This release fixes missing template assets in the installed package so that `pythra create-project` can correctly scaffold new projects.

### 🛠️ Fixed

* **Project template assets not included in distribution:**
   * __Problem:__ The HTML, CSS, JavaScript, fonts, and icon assets under `project_template/render` and `project_template/assets` were not being bundled into the published wheel. As a result, `pythra create-project` produced projects with missing frontend files, causing the generated apps to fail or render with broken UI.
   * **Solution:** Updated packaging configuration (`MANIFEST.in` and `pyproject.toml`) to include all required template assets (e.g. `*.html`, `*.css`, `*.js`, `*.yaml`, `*.yml`, `*.ttf`, `*.ico`, `*.json`, `*.in`, plus nested asset folders). These files are now shipped inside the wheel, ensuring that freshly created PyThra projects have all required frontend resources available out of the box.

---

## [0.1.6] - 2025-11-17

This release focuses on improving stability and user experience on Windows systems, specifically addressing critical rendering bugs that occurred when resuming a machine from sleep or hibernation.

### 🛠️ Fixed

* **WebView Content Shrinking After System Resume:**

   * **Problem:** On resuming from sleep, the `QWebEngineView` content would often fail to reflow, appearing "shrunken" or incorrectly sized within the application window. This required a manual window resize to fix.
   * __Solution:__ A robust viewport synchronization routine (`_sync_webview_viewport`) has been implemented. It is automatically triggered when the application becomes active after a system resume. This function forces the underlying Chromium engine's viewport to match the Qt widget's dimensions and then dispatches a JavaScript `resize` event, ensuring all web content (CSS and JavaScript layouts) correctly recalculates and fills the window as intended.

* **DPI Scaling Reset to 96 on Resume:**

   * **Problem:** On systems with high-DPI displays (e.g., 125% or 150% scaling), resuming from sleep could cause the application to lose its awareness of the correct scaling factor, defaulting to a base of 96 DPI. This made all content appear too small.
   * **Solution:** The resume handler now intelligently re-probes the browser's actual `window.devicePixelRatio` after waking up. It compares this value to the baseline established at startup and dynamically applies the correct `zoomFactor` to the `QWebEnginePage`. This restores the proper content scale, overriding any incorrect DPI information reported by the operating system post-resume.

### ✨ Changed

* **Enhanced System Power Event Handling on Windows:**
   * The WMI-based power event watcher (`watch_for_power_events`) has been improved to detect both "suspend" (entering sleep) and "resume" (waking up) events. This allows for more sophisticated state management, such as the automatic minimizing and restoring of windows during sleep cycles.
