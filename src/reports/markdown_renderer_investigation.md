# Pythra Markdown Renderer Widget Investigation

**Date**: 2026-03-23
**Objective**: Investigate the optimal Markdown rendering library for the Pythra "Markdown Renderer Widget" plugin.

The three candidates requested for evaluation are:
1. `markdown-it-py` (Python)
2. `marked` (JavaScript)
3. `markdown-it` (JavaScript)

---

## 1. Architectural Context: The Pythra Framework
Based on an analysis of `core.py`, `window/webwidget.py`, `base.py`, and the existing `plugins/markdown` editor, Pythra operates on a **decoupled Backend-Frontend Architecture**:
- **Backend**: Python manages the Widget tree, state (`Reconciler`, `State`, `StatefulWidget`), and application logic.
- **Frontend**: QtWebEngine (Chromium) handles the DOM rendering via injected JavaScript and CSS.
- **The Bridge**: The `Api` class utilizes `QWebChannel` and `evaluate_js` to send data between Python and JS.

In the current `MarkdownEditorState` plugin, markdown conversion is handled entirely in Python (`markdown` and `markdownify` packages). The Python backend serializes the generated HTML into a string and sends it over the bridge to be injected into the DOM instance (`innerHTML = html_js`).

## 2. Library Evaluation

### Option 1: `markdown-it-py` (Python)
- **Repo**: [executablebooks/markdown-it-py](https://github.com/executablebooks/markdown-it-py)
- **How it works within Pythra**: Python receives/holds the raw Markdown string -> `markdown-it-py` parses it into an AST and renders HTML in Python -> The HTML string is serialized and sent to QtWebEngine via `evaluate_js`.
- **Pros**:
  - **Single Source of Truth**: The Markdown processing logic remains entirely in Python, aligning with Pythra's goal of being a Python-first framework.
  - **Pythra Integration**: It is much easier to write custom Python AST plugins (e.g., if you want to support a custom syntax like `[Widget:MyButton]` and replace it with a Pythra `Key` / `html_id` during compilation).
- **Cons**:
  - **Performance**: Parsing massive Markdown files on the Python main thread will block the Qt event loop, potentially causing the UI to stutter during renders.
  - **Bridge Payload**: Sending large, fully constructed HTML strings over the `QWebChannel` bridge is heavy compared to sending raw markdown.

### Option 2: `marked` (JavaScript)
- **Repo**: [markedjs/marked](https://github.com/markedjs/marked)
- **How it works within Pythra**: Python holds the raw Markdown string -> Python sends the raw Markdown string over the bridge to QtWebEngine -> `marked.js` runs in the browser, recompiles to HTML, and updates the element. 
- **Pros**:
  - **Extreme Performance**: `marked` is built specifically for speed. Offloading the parsing to the Chromium V8 JS engine ensures the Python main thread is never blocked.
  - **Lightweight Bridge**: The payload sent from Python to JS is just the raw markdown string, which is highly efficient.
- **Cons**:
  - **Less Python Control**: If you want to create custom Markdown extensions or syntax rules, you must write them in JavaScript and inject them via `js_init` scripts instead of writing them natively in Python.
  - Security considerations (requires a sanitizer like DOMPurify in the JS layer, per their docs).

### Option 3: `markdown-it` (JavaScript)
- **Repo**: [markdown-it/markdown-it](https://github.com/markdown-it/markdown-it)
- **How it works within Pythra**: Similar to `marked`, parsing happens in the JS frontend.
- **Pros**: 
  - Offloads parsing to the JS engine (unblocking Python).
  - 100% CommonMark compliance and a massive ecosystem of JS plugins for syntax highlighting, math, tables, etc.
- **Cons**:
  - Slightly heavier script size than `marked`.
  - Same constraint as `marked`: customizing the parser requires writing JavaScript plugins rather than Python.

---

## 3. Recommendation based on Pythra

The optimal choice depends entirely on the **level of pythonic extensibility** you need for the widget:

### **Recommendation A: Use `marked` (JS) if...**
If the goal is simply a **Read-Only Markdown Previewer** (as hinted in `todo.md`: *"implement a native-like Markdown preview/renderer widget"*). 
Sending raw markdown strings to `marked` running inside the JS frontend is the **most performant approach**. It avoids blocking Pythra's Python execution thread during heavy DOM updates and keeps the inter-process messaging payload small. Code syntax highlighting (e.g., `highlight.js` or `Prism.js`) can also be processed entirely in the JS frontend smoothly.

### **Recommendation B: Use `markdown-it-py` (Python) if...**
If you plan to allow users to **embed native Pythra widgets inside Markdown**. 
For example, if you want developers to write `{{ @MyCustomButton }}` in markdown and have Pythra render a real Python Qt interactive button inside the markdown preview. To achieve this, you need access to the Abstract Syntax Tree (AST) in Python to map markdown tokens to Pythra `Key` IDs. `markdown-it-py` is perfect for this due to its highly extensible token-based architecture in pure Python.

**Conclusion Summary**: For a high-performance standard Markdown viewer, use **`marked`** (JS) to offload work to Chromium. For an advanced markdown renderer that integrates deeply with Pythra Python widgets, use **`markdown-it-py`** (Python).
