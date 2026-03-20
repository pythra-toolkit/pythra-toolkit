# Key Concepts and Terminology
Relevant source files
- [GEMINI.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/GEMINI.md)
- [README.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md)
- [assets/demo.gif](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/assets/demo.gif)
- [src/pythra/pythra/__pycache__/__init__.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/__init__.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/styles.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/styles.cpython-312.pyc)
- [src/pythra/pythra/base.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py)
- [src/pythra/pythra/key_cython.cpython-312-x86_64-linux-gnu.so](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/key_cython.cpython-312-x86_64-linux-gnu.so)
- [src/pythra/pythra/reconciler.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py)
- [src/pythra/pythra/reconciler_cython.c](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.c)
- [src/pythra/pythra/reconciler_cython.cpython-312-x86_64-linux-gnu.so](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.cpython-312-x86_64-linux-gnu.so)
- [src/pythra/pythra/reconciler_cython.pyx](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx)
- [src/pythra/pythra/reconciler_loader.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_loader.py)
- [src/pythra/pythra/window/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/__init__.py)
- [switch_bug_report.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/switch_bug_report.md)

This page defines the core vocabulary and architectural primitives of the PyThra framework. Understanding these concepts is essential for navigating the codebase and understanding how Python-defined UI structures are transformed into high-performance desktop applications.

## 1. The Widget Hierarchy

In PyThra, everything is a `Widget`. Inspired by Flutter, the UI is composed of a tree of immutable objects that describe the configuration of the interface at a specific point in time [src/pythra/pythra/base.py143-157](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L143-L157)

### Core Widget Types
ClassRoleLifecycle`Widget`The base class for all UI elements. Defines identity and parent-child relationships [src/pythra/pythra/base.py143-145](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L143-L145)Immutable configuration.`StatelessWidget`A widget that does not require mutable state. Its appearance is determined solely by its constructor arguments [src/pythra/pythra/state.py26-30](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L26-L30)Rebuilt when parent rebuilds.`StatefulWidget`A widget that maintains mutable state across rebuilds. It delegates its building logic to a separate `State` object [src/pythra/pythra/state.py33-40](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L33-L40)Persistent across tree updates.`State`The logic and internal data for a `StatefulWidget`. Contains lifecycle hooks like `initState` and `dispose`[src/pythra/pythra/state.py43-55](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L43-L55)Persistent until removed from tree.
### Widget Identity: The `Key`

A `Key` is an "ID card" for widgets [src/pythra/pythra/base.py17-19](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L17-L19) It allows the Reconciler to uniquely identify a widget across different render cycles, even if its position in a list changes. This is critical for preserving state in scrollable lists or form inputs [src/pythra/pythra/base.py31-34](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L31-L34) PyThra provides a Cython-accelerated `Key` implementation for high-speed hashing and comparison [src/pythra/pythra/base.py9-12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L9-L12)

**Sources:**[src/pythra/pythra/base.py9-173](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L9-L173)[src/pythra/pythra/state.py26-55](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L26-L55)

---

## 2. The Declarative Update Cycle

PyThra uses a reactive, declarative model. Developers do not manually manipulate DOM elements; instead, they trigger state changes that cause the framework to compute the difference between the "Old Tree" and the "New Tree".

### Update Cycle Diagram

This diagram maps the natural language flow of an update to the specific code entities involved.

Title: PyThra Declarative Update Pipeline

```
Code Entity Space

Natural Language Space

User Clicks Button

Update Data Variable

Request UI Refresh

onPressed Callback

State.setState()

_pending_state_updates

Framework._perform_reconciliation()

Reconciler.reconcile()
```

**Sources:**[src/pythra/pythra/state.py102-110](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L102-L110)[src/pythra/pythra/reconciler.py183-202](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L183-L202)[README.md26-29](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md#L26-L29)

---

## 3. Reconciliation and Patching

Reconciliation is the "smart brain" that identifies exactly what changed between two widget trees to avoid rebuilding the entire web page [src/pythra/pythra/reconciler.py4-9](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L4-L9)

### The Reconciler

The `Reconciler` class compares the `previous_map` (old tree state) with the `new_widget` (current configuration) [src/pythra/pythra/reconciler.py183-186](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L183-L186) To maximize performance, PyThra uses **Cython-accelerated** functions for the most frequent operations:

- `cython_diff_props`: Fast property comparison [src/pythra/pythra/reconciler_cython.pyx29-35](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L29-L35)
- `cython_diff_node_recursive`: Tree traversal and node comparison [src/pythra/pythra/reconciler_cython.pyx66-81](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L66-L81)

### Patch Actions

The output of reconciliation is a list of `Patch` objects [src/pythra/pythra/reconciler.py154-167](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L154-L167) These are precise instructions sent to the JavaScript bridge:
ActionDescriptionCode Entity**INSERT**Adds a new element to the DOM.`PatchAction.INSERT`**REMOVE**Deletes an element from the DOM.`PatchAction.REMOVE`**UPDATE**Modifies attributes/props of an existing element (e.g., text, color).`PatchAction.UPDATE`**MOVE**Changes the position of an element within its parent.`PatchAction.MOVE`**REPLACE**Swaps one widget type for another entirely.`PatchAction.REPLACE`
**Sources:**[src/pythra/pythra/reconciler.py29-35](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L29-L35)[src/pythra/pythra/reconciler_cython.pyx15-26](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L15-L26)

---

## 4. Styling and Hashing

PyThra uses a unique styling system that combines Python objects with an optimized CSS generation pipeline.

### Shared Styles and `style_key`

Instead of inline styles, widgets generate a `style_key` based on their properties.

1. **Hashing**: The `make_hashable` function converts complex objects (like `EdgeInsets` or `BoxDecoration`) into a stable tuple fingerprint [src/pythra/pythra/base.py84-102](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L84-L102)
2. **Shared Classes**: If multiple widgets share the same style properties, they receive the same `css_class` (e.g., `shared-style-abc`).
3. **CSS Injection**: The framework generates a single CSS rule for that class, significantly reducing the size of the DOM and the amount of data sent to the webview [README.md31](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md#L31-L31)

### Key Styling Primitives

- `EdgeInsets`: Handles padding and margins using pixel values [src/pythra/pythra/styles.py12-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L12-L20)
- `html_id`: A unique string (e.g., `fw_id_123`) generated by the `IDGenerator` to track the physical DOM element [src/pythra/pythra/reconciler.py145-151](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L145-L151)

**Sources:**[src/pythra/pythra/base.py84-120](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L84-L120)[src/pythra/pythra/styles.py12-42](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L12-L42)[src/pythra/pythra/reconciler.py145-151](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L145-L151)

---

## 5. Architectural Data Flow

This diagram shows how data entities move from the Python logic layer through the Reconciler into the JavaScript bridge.

Title: PyThra Data Entity Flow

```
JS Bridge (pythra_bridge.js)

Reconciliation (reconciler.py)

Python Logic (lib/main.py)

render_props()

diff against

generates

JSON (orjson)

document.getElementById(html_id)

Widget Instance

Props (dict)

Reconciler

previous_map

Patch Object

Browser DOM

applyPatches()
```

**Sources:**[src/pythra/pythra/reconciler.py23-28](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler.py#L23-L28)[src/pythra/pythra/reconciler_cython.pyx123-140](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/reconciler_cython.pyx#L123-L140)[README.md28-29](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md#L28-L29)