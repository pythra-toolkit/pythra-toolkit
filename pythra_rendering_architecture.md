# Pythra Rendering Architecture

This document outlines the architectural design of the Pythra rendering pipeline, detailing the flow from Python widget definitions to the final HTML/JS output in the browser.

## 1. High-Level Flow

The rendering process transforms a tree of Python `Widget` objects into a corresponding tree of HTML elements, managed by a Virtual DOM-like structure called the `context_map`.

**The flow involves:**
1.  **Build Phase**: Constructing the widget tree in Python.
2.  **Reconciliation**: Comparing the new tree against the previous state to generate a minimal set of updates (`Patches`).
3.  **Asset Generation**: Creating HTML, CSS, and JS based on the reconciliation result.
4.  **Client-Side Hydration**: Executing JS initializers to attach behavior to the static HTML.

## 2. From Key to Widget

The `Key` is the primary mechanism for maintaining identity across rebuilds.

*   **Definition**: A `Key` ensures that a specific widget instance corresponds to a specific DOM element across updates. It is defined in `reconciler.py`.
*   **Usage**:
    *   When a `Widget` is created, it can be assigned a `key`.
    *   The `Reconciler` uses this key during the diffing process (`_diff_node_recursive`).
    *   **Logic**:
        *   If `new_widget.key == old_data.key` AND `type(new_widget) == old_data.type`: The widget is **Updated**. Properties are diffed, and the DOM element is preserved.
        *   If keys or types differ: The old widget is **Removed** and the new one is **Inserted** (Replaced).

## 3. The Reconciler & ID Generator

The `Reconciler` is the core engine (`reconciler.py`) responsible for generating the "blueprint" for the UI.

### ID Generator
*   **Role**: Assigns stable, unique HTML IDs (`id="..."`) to every rendered element.
*   **Mechanism**: A simple counter (`fw_id_1`, `fw_id_2`, ...) in `IDGenerator.next_id()`.
*   **Persistence**: Initial IDs are generated during the first render. During updates, if a widget's `Key` matches, its `html_id` is reused from the `previous_map`, ensuring DOM stability.

### The Algorithm (`reconcile` method)
1.  **Input**: `previous_map` (old state) and `new_widget_root` (new state).
2.  **Traversal**: Recursively walks the new widget tree.
3.  **Diffing**:
    *   **Insert**: If a node doesn't exist in the map, generate a new `html_id` and create an `INSERT` patch.
    *   **Update**: If it exists (matching key), compare `render_props()`. If changed, create an `UPDATE` patch.
    *   **Remove**: If a key from the old map is not in the new tree, create a `REMOVE` patch.
    *   **Move**: (In lists) If child order changes, create a `MOVE` patch.
4.  **Output**: A `ReconciliationResult` containing:
    *   `patches`: List of operations (INSERT, UPDATE, REMOVE).
    *   `new_rendered_map`: The new state of the virtual DOM.
    *   `js_initializers`: Metadata for widgets requiring JS logic.

## 4. JS Initializers & Engine Loading

Pythra uses a "Just-in-Time" approach to load JavaScript logic.

### Detection
*   Widgets define their JS needs in `render_props()`.
    *   **Flags**: `init_slider`, `init_dropdown`, `responsive_clip_path`.
    *   **Generic**: `_js_init` dictionary pointing to a specific engine.
*   The `Reconciler` collects these requirements into `result.js_initializers`.

### Loading (`core.py`)
*   **Analysis**: `_analyze_required_js_engines` scans the initializers and props to determine which JS files are needed (e.g., `PythraSlider` needs `slider.js`).
*   **Bundling**: `_get_js_utility_functions` reads the required JS files, wraps them to avoid global scope pollution (except for necessary exports), and bundles them.
*   **Injection**:
    *   **Initial Render**: The bundled JS is written directly into `index.html`.
    *   **Updates**: If a new widget type appears (e.g., first usage of a Slider), the framework dynamically sends the JS code to the browser via `window.evaluate_js`.

## 5. Writing Initial Content

The initial render is handled by `_performing_initial_render` in `core.py`.

1.  **Build**: The full widget tree (`root_widget`) is built.
2.  **Reconcile**: called with an empty `previous_map`.
    *   All widgets generate `INSERT` actions.
    *   Stable HTML IDs are assigned.
3.  **Generate HTML**: `_generate_html_from_map` constructs the raw HTML string using the `html_id`s and tags derived from widget types.
4.  **Generate CSS**: `_generate_css_from_details` creates the `<style>` block, deduplicating styles using shared classes.
5.  **Generate JS**:
    *   Embeds the bundled engine code (`_get_js_utility_functions`).
    *   Generates instantiation logic:
        ```javascript
        window._pythra_instances['fw_id_1'] = new PythraSlider('fw_id_1', {...options});
        ```
6.  **Write Files**:
    *   `index.html`: Contains the HTML structure, CSS, and initial JS.
    *   `styles.css`: (Optional external stylesheet).
    *   The browser loads this file, rendering the initial UI instantly without waiting for a WebSocket connection.
