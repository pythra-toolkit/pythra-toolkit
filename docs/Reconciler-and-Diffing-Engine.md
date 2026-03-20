# Reconciler and Diffing Engine
Relevant source files
- [GEMINI.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/GEMINI.md)
- [src/pythra/pythra/key_cython.cpython-312-x86_64-linux-gnu.so](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/key_cython.cpython-312-x86_64-linux-gnu.so)
- [src/pythra/pythra/reconciler.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py)
- [src/pythra/pythra/reconciler_cython.c](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.c)
- [src/pythra/pythra/reconciler_cython.cpython-312-x86_64-linux-gnu.so](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.cpython-312-x86_64-linux-gnu.so)
- [src/pythra/pythra/reconciler_cython.pyx](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx)
- [src/pythra/pythra/reconciler_loader.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_loader.py)
- [switch_bug_report.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/switch_bug_report.md)

The **Reconciler** is the core "intelligence" of the PyThra framework. It implements a declarative UI update strategy inspired by Flutter and React, ensuring that only the necessary parts of the browser DOM are updated when Python state changes. By comparing the previous widget tree with the newly generated one, it produces a minimal set of instructions called **Patches**.

## Architecture Overview

The reconciliation process transforms a high-level widget tree change into low-level DOM manipulations. It operates as a bridge between the Python-side widget definitions and the JavaScript-side `applyPatches()` function in the webview.

### Core Data Flow

"Natural Language Space" to "Code Entity Space" mapping:
ConceptCode EntityRole**Old State**`self.context_maps['main']`Storage of the previous tree's metadata and HTML IDs [src/pythra/pythra/reconciler.py185](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L185-L185)**New State**`new_widget`The root of the freshly built widget tree passed to `reconcile()`[src/pythra/pythra/reconciler.py220](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L220-L220)**Instructions**`Patch` / `CythonPatch`Dataclasses representing a single DOM operation (INSERT, UPDATE, etc.) [src/pythra/pythra/reconciler.py158-168](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L158-L168)**Result**`ReconciliationResult`Container for all patches, new metadata map, and JS initializers [src/pythra/pythra/reconciler.py174-180](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L174-L180)
### The Reconciliation Loop

The `Reconciler.reconcile()` method is the entry point for the diffing engine. It initializes a recursive traversal that compares nodes based on their **Key** and **Type**.

Title: Reconciler Traversal Logic

```

```

Sources: [src/pythra/pythra/reconciler.py220-250](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L220-L250)[src/pythra/pythra/reconciler.py328-340](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L328-L340)[src/pythra/pythra/reconciler.py408-420](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L408-L420)

---

## The Diffing Engine

The engine uses a depth-first search (DFS) to identify changes. It relies heavily on `html_id` tracking to maintain a stable reference to DOM elements across updates.

### Recursive Functions

1. **`_diff_node_recursive`**: Compares a single `new_widget` against its counterpart in the `previous_map`.

- If the widget is new (no entry in `previous_map`), it calls `_insert_node_recursive`[src/pythra/pythra/reconciler.py333-335](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L333-L335)
- If the `widget_type` or `key` has changed, it generates a `REPLACE` patch [src/pythra/pythra/reconciler.py343-365](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L343-L365)
- If types match, it calculates property differences using `_diff_props`[src/pythra/pythra/reconciler.py377-385](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L377-L385)
2. **`_diff_children_recursive`**: Synchronizes lists of child widgets.

- It builds a map of `old_keys` to identify moved or removed elements [src/pythra/pythra/reconciler.py423-440](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L423-L440)
- It handles the **MOVE** action when a widget with the same key appears at a different index [src/pythra/pythra/reconciler.py465-475](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L465-L475)
- Any old keys not present in the new tree result in **REMOVE** patches [src/pythra/pythra/reconciler.py488-495](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L488-L495)
3. **`_insert_node_recursive`**: Handles the creation of new DOM structures. It generates the initial HTML string for a widget and its entire subtree [src/pythra/pythra/reconciler.py510-530](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L510-L530)

### Patch Action Types

The engine emits five specific actions defined in the `PatchAction` literal [src/pythra/pythra/reconciler.py154](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L154-L154):
ActionDescriptionTrigger**INSERT**Adds a new element to the DOM.New widget key detected in child list [src/pythra/pythra/reconciler.py455-460](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L455-L460)**REMOVE**Deletes an element from the DOM.Widget key from previous tree is missing in new tree [src/pythra/pythra/reconciler.py490-495](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L490-L495)**UPDATE**Modifies attributes (style, text, etc.).Property diff detected between same-type widgets [src/pythra/pythra/reconciler.py380-390](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L380-L390)**MOVE**Changes the order of siblings.Existing key found at a new position in the list [src/pythra/pythra/reconciler.py465-470](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L465-L470)**REPLACE**Swaps an element for a different type.Key matches but `widget_type` has changed [src/pythra/pythra/reconciler.py345-350](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L345-L350)
Sources: [src/pythra/pythra/reconciler.py154-168](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L154-L168)[src/pythra/pythra/reconciler.py328-500](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L328-L500)

---

## Optimization Layers

### Cython Acceleration

To handle large widget trees, PyThra provides a Cython-accelerated layer in `reconciler_cython.pyx`. When available, these C-extensions replace the Python implementations of hot functions for a 5-20x speedup [src/pythra/pythra/reconciler_cython.pyx10-11](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L10-L11)

- **`cython_diff_props`**: Fast dictionary comparison that ignores non-renderable keys like `widget_instance` or `itemBuilder`[src/pythra/pythra/reconciler_cython.pyx29-63](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L29-L63)
- **`cython_diff_node_recursive`**: Optimized version of the node diffing logic [src/pythra/pythra/reconciler_cython.pyx66-163](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L66-L163)
- **`cython_diff_children_recursive`**: Optimized child list synchronization [src/pythra/pythra/reconciler_cython.pyx165-200](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L165-L200)

The `reconciler_loader.py` handles the graceful fallback if the `.so` or `.pyd` files are missing [src/pythra/pythra/reconciler_loader.py9-23](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_loader.py#L9-L23)

### HTML Stub Caching

The Reconciler maintains an LRU cache (`_html_stub_cache`) for HTML templates.

- **Key**: `(widget_class_name, stable_props_json)`
- **Value**: HTML string with a `{id}` placeholder for the `html_id`.
This prevents expensive string formatting and template generation for widgets that appear frequently with the same static properties [src/pythra/pythra/reconciler.py194-197](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L194-L197)

Title: Reconciler Implementation Components

```

```

Sources: [src/pythra/pythra/reconciler.py183-210](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L183-L210)[src/pythra/pythra/reconciler_cython.pyx1-11](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L1-L11)[src/pythra/pythra/reconciler_loader.py35-57](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_loader.py#L35-L57)

---

## Known Behaviors and Lifecycle

### CSS and Callback Collection

During the diffing process, the reconciler calls `_collect_details()`. This method extracts CSS class requirements and registers Python-side callbacks (like `onPressed`) to the specific `html_id`[src/pythra/pythra/reconciler.py280-315](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L280-L315)

### Regression Note: The Switch Bug

A critical diagnostic identified that the Cython implementation must explicitly call `_collect_details()` during the `UPDATE` path. Failure to do so leads to empty `active_css_details`, causing the framework to skip CSS regeneration, which can make widgets (like the `Switch`) appear to "disappear" because their styles are missing from the stylesheet [switch_bug_report.md26-64](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/switch_bug_report.md#L26-L64)

Sources: [src/pythra/pythra/reconciler.py280-315](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L280-L315)[src/pythra/pythra/reconciler_cython.pyx97-105](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L97-L105)[switch_bug_report.md26-64](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/switch_bug_report.md#L26-L64)