# Dropdown Re-render Investigation

Summary
- Symptom: `Dropdown` menu items disappear or show literal `{children}` text when the dropdown is inserted/updated after the initial render (i.e., non-initial reconciliation).

Root cause
- On initial render, the Framework generates full HTML by calling `Framework._generate_html_from_map`, which calls `Reconciler._generate_html_stub` for each node and then replaces `{children}` server-side: `if "{children}" in stub: return stub.replace("{children}", children_html)` (see `src/pythra/pythra/core.py`).
- For incremental reconciliations, the Reconciler emits `INSERT` patches containing the widget stub HTML (from `_generate_html_stub`) and then issues separate `INSERT` patches for the widget's children. The client `pythra_bridge.js` sets `tempContainer.innerHTML = html.trim()` and appends the parent stub as-is, without sanitizing or replacing the `{children}` placeholder.
- When a parent stub contains the literal `{children}` token (used by `DropdownMenuItem._generate_html_stub`), the parent is inserted containing that literal text node. Later, the child elements are appended into the parent node — but the literal `{children}` text node remains, producing the visible garbage seen in the UI.

Relevant code locations
- `src/pythra/pythra/widgets_more.py` — `DropdownMenuItem._generate_html_stub` returns:
  `return f'<li class="dropdown-item{ " disabled" if widget_instance.disabled else ""}" id="{html_id}" data-value="{value_escaped}"{label_attr}{disabled_attr}>{{children}}</li>'`
- `src/pythra/pythra/core.py` — server-side replacement on initial render:
  `if "{children}" in stub: return stub.replace("{children}", children_html)`
- `src/pythra/pythra/reconciler.py` — `Reconciler._insert_node_recursive` produces `INSERT` patches with `data['html'] = stub_html` and then inserts children with their own `INSERT` patches.
- `src/pythra/project_template/render/js/pythra_bridge.js` — `handleInsert` sets `tempContainer.innerHTML = html.trim()` and appends `insertedEl` without removing the literal `{children}` token.

Why the `DropdownMenuItem` string is implicated
- `DropdownMenuItem` deliberately emits `{children}` in its stub to allow the server-side generator to inline complex child widget HTML (text, icons, styled widgets) during the initial render. This works only because the initial renderer replaces `{children}` with the fully-generated children HTML before writing `index.html`.
- During reconciliation/INSERT paths, no server-side replacement is performed for the single stub string, so the literal placeholder persists in the DOM on the client.

Possible fixes (prioritized)
1. Client-side: strip `{children}` placeholder text nodes on INSERT
   - Modify `pythra_bridge.js:handleInsert` to remove any child text node whose trimmed text equals `{children}` from `insertedEl` before appending or after appending.
   - Pros: minimal change, backwards-compatible, fixes all widgets using `{children}` placeholders.
   - Cons: slight JS change; behavior depends on placeholder token string.

2. Server-side reconciler: emit empty placeholder instead of `{children}` for incremental inserts
   - In `Reconciler._insert_node_recursive`, detect generated `stub_html` containing `{children}` and replace that token with an empty string (`''`) before adding the INSERT patch. Children will still be inserted by subsequent patches.
   - Pros: no client changes; children will be inserted cleanly and no literal token remains.
   - Cons: initial render still needs server-side inlining. Must ensure initial `_generate_html_from_map` still performs replacement.

3. Widget-level: change `DropdownMenuItem._generate_html_stub` to not use `{children}` but instead use a dedicated placeholder element (e.g., `<span data-pythra-children></span>`)
   - Then update client or reconciler to target and replace that placeholder when children are inserted.
   - Pros: explicit placeholder reduces accidental visible tokens and is more robust.
   - Cons: more invasive changes across widget templates and client handling.

Recommended immediate action
- Apply fix (2) in `Reconciler._insert_node_recursive`: when creating the INSERT patch, if the generated `stub_html` contains `"{children}"`, replace it with an empty string before putting it into `data['html']`. This keeps server-side behavior consistent and requires only a single small patch in Python.

Short patch sketch (server-side, minimal):
```python
# after stub_html = self._generate_html_stub(new_widget, html_id, new_props)
if "{children}" in stub_html:
    stub_html = stub_html.replace("{children}", "")
```

Alternative quick patch (client-side): in `pythra_bridge.js:handleInsert` after `const insertedEl = tempContainer.firstElementChild;` add:
```javascript
// remove literal {children} text nodes that may have been left from server stubs
for (const node of Array.from(insertedEl.childNodes)) {
    if (node.nodeType === Node.TEXT_NODE && node.textContent.trim() === '{children}') {
        insertedEl.removeChild(node);
    }
}
```

Next steps I can take
- I can open a PR or apply the minimal server-side patch in `src/pythra/pythra/reconciler.py` (recommended).
- Or, if you prefer the client-side quick fix, I can patch `src/pythra/project_template/render/js/pythra_bridge.js` and the corresponding template copies.

Which fix should I implement now? (server-side minimal patch recommended)