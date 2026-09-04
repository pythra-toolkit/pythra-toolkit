# PyThra Hot Reload Implementation Plan

We will implement a state-preserving Hot Reload system for PyThra. This will allow code modifications (like editing a widget's build method or styling) to be injected into the running app instantly without process restarts, retaining all user/widget states.

## User Review Required

> [!IMPORTANT]
> The hot reload watches Python source files in the project root (`lib/` directory) and reloads modified modules dynamically. We use a standard polling-based watch thread in the parent process (`pythra run`) and send hot reload instructions to the PySide app via `stdin`.

---

## Proposed Changes

### [CLI and Runtime Control]

#### [MODIFY] [pythra_cli/main.py](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/pythra_cli/main.py)
- Update `run` command to start a simple polling file watcher thread that walks the project root and checks `.py` modification times.
- If a file change occurs, push `"auto_hot_reload"` to the event queue.
- If `"auto_hot_reload"` or manual `'h'` keypress is processed, write `"hot_reload\n"` to the spawned process's stdin.
- Enable `stdin=subprocess.PIPE` when spawning the child Python process.

---

### [Core Framework & Reconciler]

#### [MODIFY] [webwidget.py](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/window/webwidget.py)
- Register `hot_reload_from_ui()` slot on the `Api` class to allow triggering hot reloads directly from the interactive debug banner.

#### [MODIFY] [core.py](file:///home/red-x/Documents/pythra-toolkit/src/pythra/pythra/core.py)
- Add a daemon stdin listener thread in `Framework.__init__` that reads from `sys.stdin`. When it receives `"hot_reload\n"`, it schedules a `hot_reload()` execution on the main Qt thread.
- Implement `_adopt_tree_identities(self, previous_map, new_widget)` which aligns child identities (UUIDs) recursively by position/type when explicit keys are absent, ensuring State preservation.
- Implement the framework-level `hot_reload(self)` method:
  1. Detect and reload modified project modules using `importlib.reload`.
  2. Reconstruct the root widget instance.
  3. Pre-process the new widget tree using `_adopt_tree_identities`.
  4. Perform partial tree reconciliation.
  5. Apply generated patches to the webview DOM.
- Update the interactive debug banner:
  - Add a **Hot Reload** button (SVG icon) calling `window.pywebview.hot_reload_from_ui()`.
  - Adjust styling to support 3 buttons and correct expansion hover dimensions.

## Verification Plan

Since we are prohibited from running tests or launching the app for verification unless instructed, verification will be done via:
- Verifying code syntax, logic loops, and local socket/channel paths.
- Checking that the stdin redirection handles streams correctly.
