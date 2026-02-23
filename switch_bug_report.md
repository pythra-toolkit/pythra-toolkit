# Switch Widget Toggle Bug — Diagnostic Report

## Summary

The `Switch` widget toggles correctly the first time but **disappears on the second toggle**. The root cause is a combination of two issues in the reconciler's patch logic — one in the **Cython-accelerated path** and one in the **CSS lifecycle management**.

---

## Bug Reproduction Path

```
Initial Render → Switch(value=True) → css_class="shared-switch-0"
                                        ✅ Visible, styled correctly

First Toggle   → Switch(value=False) → css_class="shared-switch-1"
                                        ✅ UPDATE patch swaps class, CSS regenerated

Second Toggle  → Switch(value=True)  → css_class="shared-switch-0"
                                        ❌ Widget disappears
```

---

## Root Cause Analysis

### Issue 1: Cython `cython_diff_node_recursive` Skips `_collect_details`

**File:** `pythra-toolkit/src/pythra/pythra/reconciler_cython.pyx` — `cython_diff_node_recursive` (line 66–149)

The **Python** fallback `_diff_node_recursive` in `reconciler.py` calls `self._collect_details(new_widget, new_props, result)` during the UPDATE path (lines 348, 379). This method is responsible for:

1. **Collecting CSS class details** into `result.active_css_details` — used later to determine if the stylesheet needs regeneration.
2. **Registering callbacks** into `result.registered_callbacks` — ensuring click handlers point to the *new* widget instance.

The **Cython** version `cython_diff_node_recursive` **never calls `_collect_details`**. It jumps straight to prop diffing, map updates, and child recursion. This means:

- `result.active_css_details` remains **empty** for all widgets processed through the Cython UPDATE path.
- `result.registered_callbacks` is **not populated** during updates.

### Issue 2: CSS Regeneration Skipped on Second Toggle

**File:** `pythra-toolkit/src/pythra/pythra/core.py` — `_process_reconciliation` (lines 806–822)

The CSS regeneration logic uses a guard:

```python
new_css_keys = set(all_active_css_details.keys())
if not hasattr(self, '_last_css_keys') or self._last_css_keys != new_css_keys:
    # Regenerate CSS...
    self._last_css_keys = new_css_keys
```

| Toggle | `all_active_css_details` (Cython mode) | `new_css_keys` | `_last_css_keys` | CSS Regenerated? |
|--------|---------------------------------------|----------------|-------------------|-------------------|
| 1st    | `{}` (Cython skipped collection)       | `set()`        | *(not set yet)*   | ✅ Yes (attribute missing) |
| 2nd    | `{}` (Cython skipped collection)       | `set()`        | `set()`           | ❌ No (sets are equal) |

On the **first toggle**, CSS is regenerated because `_last_css_keys` doesn't exist yet. The stylesheet is updated to include only `shared-switch-1` rules (the current state).

On the **second toggle**, `_last_css_keys == new_css_keys` (both empty sets), so **CSS is NOT regenerated**. The stylesheet still only contains `shared-switch-1` rules. The UPDATE patch tells the browser to swap classes from `shared-switch-1` → `shared-switch-0`, but `shared-switch-0` has **no CSS rule in the stylesheet**.

### Result

The Switch DOM element still exists, but it has **no styling** — no width, height, background-color, or positioning. The element collapses to zero size, making it appear to "disappear". This also explains why it *looks like* a REMOVE patch was triggered — the element becomes invisible, not removed.

---

## What Needs to Be Fixed

### Fix 1: Add `_collect_details` Calls to the Cython Path

**File to modify:** `pythra-toolkit/src/pythra/pythra/reconciler_cython.pyx`

In `cython_diff_node_recursive`, add calls to `reconciler._collect_details(new_widget, new_props, result)` at two points, matching the Python fallback:

```diff
 def cython_diff_node_recursive(...):
     if new_widget is None:
         return
 
     cdef dict old_data = previous_map.get(old_node_key)
 
     if old_data is None:
         reconciler._insert_node_recursive(new_widget, parent_html_id, parent_key, result, previous_map)
         return
 
     cdef str new_type = type(new_widget).__name__
     cdef str old_type = old_data.get("widget_type")
+    new_props = new_widget.render_props()
+    reconciler._collect_details(new_widget, new_props, result)  # ← ADD THIS
 
     if old_type != new_type or new_widget.key != old_data.get("key"):
+        new_props = new_widget.render_props()
+        reconciler._collect_details(new_widget, new_props, result)  # ← ADD THIS
         reconciler._insert_node_recursive(...)
         ...
         return
 
     # UPDATE path
     cdef str html_id = old_data["html_id"]
     new_props = new_widget.render_props()
+    reconciler._collect_details(new_widget, new_props, result)  # ← ADD THIS
     ...
```

> [!IMPORTANT]
> After modifying the `.pyx` file, you must **recompile the Cython module** for changes to take effect. If Cython compilation is not configured, the Python fallback in `reconciler.py` will be used instead — but the bug should still be verified in Python-only mode.

### Fix 2 (Defensive): Make CSS Regeneration Check More Robust

**File to modify:** `pythra-toolkit/src/pythra/pythra/core.py`

Even with Fix 1, the CSS regeneration guard is fragile — it relies on `_collect_details` being properly called everywhere. A defensive fix is to **always regenerate CSS when there are UPDATE patches that modify `css_class`**:

```diff
-new_css_keys = set(all_active_css_details.keys())
-if not hasattr(self, '_last_css_keys') or self._last_css_keys != new_css_keys:
+# Check if any patch modified css_class, requiring CSS regeneration
+css_changed_in_patches = any(
+    p.action == "UPDATE" and "css_class" in (p.data.get("props", {}) or {})
+    for p in all_patches
+)
+new_css_keys = set(all_active_css_details.keys())
+if css_changed_in_patches or not hasattr(self, '_last_css_keys') or self._last_css_keys != new_css_keys:
```

This ensures CSS is regenerated whenever a `css_class` change is patched, regardless of whether `_collect_details` was called.

### Fix 3 (Optional): Re-register Callbacks in Cython Path

The Cython version also skips callback registration. While the current `tog` method ignores the argument and works coincidentally, other widgets that depend on updated callback bindings could break silently. `_collect_details` handles both CSS and callbacks, so Fix 1 addresses this as well.

---

## Files Involved

| File | Role in Bug |
|------|------------|
| `src/pythra/pythra/reconciler_cython.pyx` | Missing `_collect_details` calls in `cython_diff_node_recursive` |
| `src/pythra/pythra/reconciler.py` | Python fallback works correctly (reference implementation) |
| `src/pythra/pythra/core.py` | CSS regeneration guard at `_process_reconciliation` is fragile |
| `src/pythra/pythra/widgets_more.py` | Switch widget itself is correctly implemented |
| `new-app/render/js/pythra_bridge.js` | PythraBridge `updateProps` CSS class swap is correct |

---

## Verification Plan

After applying the fixes:

1. Run the app, toggle the Switch **three or more times** — it should remain visible and correctly styled on every toggle
2. Verify that **both** `shared-switch-0` and `shared-switch-1` CSS rules exist in the stylesheet after toggling
3. Check the Python console output for `REMOVE` patches — there should be **none** for the Switch's `html_id` across toggles
