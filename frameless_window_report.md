# Frameless Window Report

## Current State

### How it works now

The `frameless: true` flag in `config.yaml` flows through:

1. `config.yaml` → `core.py:501` reads it → `core.py:561` passes to `create_window()`
2. `webwidget.py:1455` receives it → `WebWindow.__init__()` at line 817
3. `WebWindow.__init__()` lines 841-843:
   ```python
   self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
   self.setAttribute(Qt.WA_TranslucentBackground)
   ```

**What happens:** The native OS title bar and window frame are removed. The window becomes a bare surface with no chrome. Transparency is enabled.

**What's missing:** There is **zero** move or resize logic anywhere in the codebase:
- No `mousePressEvent` / `mouseMoveEvent` overrides on `WebWindow`
- No CSS `-webkit-app-region` drag region
- No custom resize border or edge grip
- No custom minimize/maximize/close buttons in the HTML template

Result: once frameless, the window cannot be moved or resized at all.

---

## Approach Options (do NOT implement, just evaluate)

### Option A: PySide6 mouse events on `WebWindow`

Override `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent` in `webwidget.py`'s `WebWindow` class. Detect drag on the window body for moving. Detect edges (e.g. 5px border) for resizing.

| Pros | Cons |
|------|------|
| Full control, works before JS loads | Harder to customize per-app |
| Reliable, native feel | Need to handle DPI / multi-monitor |
| Can set resize cursors | Edge detection competes with webview interaction |

**Key implementation points:**
- On `mousePressEvent`: record click position, detect if on edge for resize.
- On `mouseMoveEvent`: if edge-resize, call `self.setGeometry(...)` with new size; if body-drag, call `self.move(...)`.
- Use `Qt.CursorShape` constants to show resize cursors at edges.
- Need to distinguish between a window drag and a web interaction (e.g. JS slider drag). A hit-test might be needed: if mouse is over the QWebEngineView, don't intercept.

### Option B: CSS `-webkit-app-region` in the HTML/JS

Add a draggable region via CSS in `project_template/render/index.html` (and the runtime-generated HTML).

| Pros | Cons |
|------|------|
| Declarative, simple | **Not supported** in Qt WebEngine (Chromium < 106). Qt 6 uses older Chromium. |
| Works well in Electron | No resize capability — only move. |
| App-level control | WebEngine may ignore it silently. |

**Key implementation points:**
- Add `<meta name="mobile-web-app-capable" content="yes">` or equivalent.
- Add CSS: `-webkit-app-region: drag;` on a title bar element.
- Add CSS: `-webkit-app-region: no-drag;` on interactive elements.
- Resize would still need PySide6 edge detection.

**Risk:** Qt WebEngine's Chromium version may not support `-webkit-app-region` at all. Should test first.

### Option C: Custom transparent resize borders (user's idea)

Create invisible `QWidget` overlays (2-5px wide) on each edge and corner of `WebWindow`. Each overlay handles its own mouse events for resizing. A visible title bar widget handles moving.

| Pros | Cons |
|------|------|
| Clean separation of concerns | More widgets to manage |
| Each overlay is simple | Needs position sync on resize |
| Resize cursors work naturally | Overlays can interfere with webview hit-testing |

**Key implementation points:**
- 8 invisible `QWidget` children: left, right, top, bottom, top-left, top-right, bottom-left, bottom-right.
- Each sets its own cursor and implements mouse events to resize.
- A 30-40px tall visible title bar `QWidget` at the top implements move.
- Title bar can embed custom min/max/close buttons (PySide6 buttons or an embedded mini-webview).

### Option D: Hybrid JS + PySide6

Let the HTML/JS handle the visual title bar (custom window buttons, title text, drag region) and communicate drag/resize intent back to PySide6 via the QWebChannel bridge.

| Pros | Cons |
|------|------|
| Fully customizable per-app | More complex bridge protocol |
| Drag region is part of the app's design | Resize must still be PySide6 side |
| Consistent look with app UI | Latency on bridge calls for every mouse move |

**Key implementation points:**
- In `index.html`, add a `<div id="titlebar">` with drag handles and buttons.
- JS sends `pywebview.startWindowDrag()` via QWebChannel on mousedown on title bar.
- PySide6 side receives the call, records position, and handles `mouseMoveEvent`.
- For resize, JS detects if mouse is near viewport edge and sends `pywebview.startWindowResize(edge)`.

---

## Recommendation (not implementation)

**Option A (PySide6 mouse events)** is the safest starting point:
- No dependency on WebEngine Chromium version.
- Works immediately, even before HTML/JS loads.
- Resize is straightforward with edge detection.
- Move can be enabled/disabled based on a CSS class in JS (e.g., `.app-drag-region` toggles a bridge call that tells PySide6 to intercept).

**Secondary improvement:** Once move works, extend to allow JS-to-PySide6 bridge calls for drag (Option D hybrid) so the app can declare custom drag regions in HTML.

**Not recommended:** Pure CSS `-webkit-app-region` (Option B) — too risky given Qt WebEngine's Chromium version is unknown and likely too old. Transparent borders (Option C) add widget management complexity without much benefit over simple edge hit-testing in `mouseMoveEvent`.
