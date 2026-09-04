# PyThra Hot Reload Design Report

This report outlines the technical design and architectural path for implementing **Hot Reload** in the PyThra Framework. 

Unlike a **Hot Restart** (which terminates and restarts the Python process, losing all application state), a **Hot Reload** dynamically injects code updates, re-executes the build cycle, and performs a tree reconciliation while **preserving the state of all StatefulWidgets**.

---

## Architectural Challenges

To implement hot reload in PyThra, we must solve three key challenges:
1. **Dynamic Module Reloading**: Detecting file edits and reload Python modules without killing the process.
2. **Identity Stability (Positional Reconciliation)**: Mapping newly instantiated widgets to their old counterparts so their state objects are reused.
3. **Tree Reassembly**: Triggering a full rebuild of the widget tree from the root after a code reload.

---

## Proposed Design & Implementation Strategy

### 1. Code Reloading via File Watcher

We can extend the [pythra_cli/main.py](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/pythra_cli/main.py) tool with a file watcher (e.g. using `watchdog` or a simple polling-based watcher in a daemon thread) that monitors files in the `lib/` directory.

When a change is detected:
1. The watcher notifies the running application via a socket or a local IPC channel, OR the watcher runs directly inside the child PySide process.
2. The PySide process intercepts the reload request and reloads the modified modules:
   ```python
   import importlib
   import sys
   
   def reload_user_modules():
       # Find all modules belonging to the user's project
       modules_to_reload = [
           name for name, mod in list(sys.modules.items())
           if hasattr(mod, '__file__') and mod.__file__ and 'lib/' in mod.__file__
       ]
       for name in modules_to_reload:
           try:
               importlib.reload(sys.modules[name])
               print(f"🔄 Reloaded module: {name}")
           except Exception as e:
               print(f"❌ Failed to reload module {name}: {e}")
   ```

---

### 2. Positional Reconciliation (State Preservation)

Currently, widgets without explicit keys generate a random UUID:
`self._internal_id = str(uuid.uuid4())` (see [base.py](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/base.py)). 

During hot reload, new instances of these widgets get new UUIDs, causing the reconciler to treat them as entirely new elements, destroying their states and recreating their DOM nodes.

#### The Positional Matching Strategy
To align with React/Flutter matching behaviors, we can update [reconciler.py](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/reconciler.py) to match child widgets by position and type when explicit keys are absent:

```python
def _adopt_child_identities(old_children_keys, new_children_widgets, previous_map):
    # Iterate and match widgets at the same index
    for idx, new_child in enumerate(new_children_widgets):
        if new_child.key is None and idx < len(old_children_keys):
            old_key = old_children_keys[idx]
            old_data = previous_map.get(old_key)
            if old_data and old_data.get("widget_type") == type(new_child).__name__:
                # Adopt the old widget's UUID
                new_child._internal_id = old_key
```

When [_build_widget_tree](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/core.py) executes, it will find the old state object in the context map because the unique IDs match:

> [!NOTE]
> By adopting the identity of the old node, PyThra's state rescue logic in `core.py` (lines 1121–1138) will automatically reuse the existing `State` object and invoke [didUpdateWidget](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/state.py) instead of reconstructing the state.

---

### 3. Tree Reassembly and UI Diffing

After reloading the modules and updating the class definitions:
1. We instantiate the root widget again using the reloaded class definition.
2. We run the build and reconciliation pipeline:
   ```python
   def hot_reload(self):
       print("⚡ Initiating Hot Reload...")
       
       # 1. Reload code modules
       reload_user_modules()
       
       # 2. Re-create the root widget instance
       new_root = self.root_widget_class()
       
       # 3. Adopt child identities from the previous render map to stabilize UUIDs
       # 4. Build and Reconcile the new tree
       built_tree = self._build_widget_tree(new_root, context_map=self.reconciler.context_maps["main"])
       
       result = self.reconciler.reconcile(
           previous_map=self.reconciler.context_maps["main"],
           new_widget_root=built_tree,
           parent_html_id="root-container",
           is_partial_reconciliation=True
       )
       
       # 5. Apply the generated DOM patches to the webview
       if result.patches and self.window:
           patches_json = _dumps([p.__dict__ for p in result.patches])
           self.window.evaluate_js(self.id, f"window.PythraBridge.applyPatches({patches_json});")
   ```

---

## Benefits of This Approach

- **State Retention**: Users don't lose form fields, counter values, or scroll offsets while tweaking visual layouts.
- **Speed**: Generating and sending DOM patches is significantly faster than restarting PySide, rendering from scratch, and reloading the Chromium view.
- **Flutter Parity**: Achieves true developer experience parity with Flutter and modern web workflows.
