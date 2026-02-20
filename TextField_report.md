# Architectural Design Report: TextField Widget

## 1. Architectural Design Overview
The `TextField` widget in the Pythra framework is designed as a controlled input component that acts as a bridge between the frontend (HTML/CSS/JS) and the Python backend. Based on the `pythra_rendering_architecture.md` and the implementation in `widgets.py`, the architecture has the following characteristics:

- **State Management (Controllers):** 
  Instead of holding its own internal text state, it delegates state management to a `TextEditingController`. Changes on the client side trigger an `oninput` event, which fires a `handleInput` JS function that sends the new value to Python. The Python callback (`onChangedName`) simply updates the controller using `setattr()`.
- **Reconciliation & Identity:**
  A mandatory `Key` is required. This is critical for the `Reconciler` to match the exact DOM node and maintain input focus across UI rebuilds. If the widget lacked a key, typing might cause the node to be unmounted and remounted, losing the cursor position.
- **Dynamic CSS & Style Caching:**
  The `TextField` features a sophisticated CSS generation method (`generate_css_rule`). Since inputs can have varied styles `InputDecoration` (like floating labels, error borders, outline thicknesses), the class generates CSS dynamically. To avoid duplicate rules, it hashes the decoration tuple (`self.style_key = make_hashable(self.decoration)`) and caches it in `TextField.shared_styles`.
- **Component HTML Structure:**
  It renders via a structural stub (`_generate_html_stub`) composing a root container, an input field, a floating label (handled via CSS sibling selectors), an outline, and a helper text element.

## 2. Possible Bugs
1. **Unregistered Callbacks:** 
   In `__init__`, the central callback registration is commented out:
   `# Api.instance().register_callback(self.onChangedName, self.onChanged)`
   If the framework does not automatically pick up `self.onChangedName` and register it during the reconciliation phase, any keystroke leading to `handleInput` on the frontend will trigger an "Unregistered callback" error, and the Python controller won't update.
2. **Conditional Rendering Syntax Error in HTML Stub:** 
   In `_generate_html_stub`, the following string interpolation is brittle and potentially wrong: 
   `{ '' if not helper_text or None else html.escape(helper_text) }`
   The expression `not helper_text or None` is a bit unusual and can lead to unexpected behaviors. For example, if `helper_text` is `False` or empty, it could resolve cleanly, but writing it as `html.escape(helper_text) if helper_text else ""` is much safer.
3. **Controller ID as Event Name:** 
   The widget creates a callback name using `id(self.controller)`. The `id()` is only guaranteed to be unique for the *lifetime* of the object. If a controller is garbage collected and a new one is created inheriting the same memory address, it might lead to event name collisions and broken callback mappings.
4. **Input Loss of Focus or Cursor Jumping:** 
   If `setattr(self.controller, 'text', new_value)` triggers a full widget tree rebuild *on every keystroke*, and the DOM nodes are updated via the Reconciler, the HTML input might get its `value="..."` attribute rewritten. Browsers often reset the text cursor to the end (or start) of the input during such direct DOM attribute manipulations.

## 3. Performance Bottlenecks
1. **Keystroke Network Saturation (No Debounce):** 
   The `oninput="handleInput(..., this.value)"` attribute fires a WebSocket event (or similar bridge call) on *every single keystroke*. For fast typists, or on high-latency networks, this floods the backend queue, causing lag. Each event potentially queues a full virtual DOM layout/reconciliation cycle in Python.
2. **Memory Leak in Shared Styles:** 
   `TextField.shared_styles` caches CSS classes based on `make_hashable(self.decoration)`. If an application dynamically generates fields with slightly altered decorations (e.g., dynamic colors on validation, arbitrary widths), the dictionary and the inline `<style>` tag will grow indefinitely. There is no cache eviction/garbage collection for unused CSS rules.
3. **Unoptimized String Replacements:** 
   In `_generate_html_stub`, there are recurrent chain calls like `{css_class.replace('textfield-root-container', '')}` executed multiple times per single Textfield render. While minor, for large lists of input fields, this adds unnecessary CPU overhead.

## 4. How They Can Be Improved
1. **Debouncing / Throttle on the Frontend:**
   Instead of using `oninput` directly tied to a synchronous Python update, adjust the generated JS stub to debounce the `handleInput` call (e.g., waiting 150-300ms after the last stroke) or rely on `onchange` (which fires only on blur) depending on use cases. Alternatively, rely on an optimized differential patching that doesn't overwrite the native input value if it matches the current DOM state, avoiding cursor jumps.
2. **Safer Event Naming:** 
   Instead of `id(self.controller)`, give the `TextEditingController` a generated UUID internally at initialization (e.g., `self.uuid = str(uuid.uuid4())`) and use that for the callback. This guarantees uniqueness across the entire application lifecycle and avoids memory reuse edge cases.
3. **Refactoring the HTML Generation:** 
   Pre-calculate the cleaned classes in `_generate_html_stub` instead of performing `.replace()` inside every template brace:
   ```python
   base_class = css_class.replace('textfield-root-container', '').strip()
   ```
   Furthermore, rewrite the helper text logic cleanly:
   ```python
   helper_safe = html.escape(helper_text) if helper_text else ""
   ```
4. **CSS Cache Eviction:** 
   Introduce a reference counting system or an LRU (Least Recently Used) cache for `shared_styles`. When widgets are removed during reconciliation, decrement the rule usage, and remove the CSS rule from the DOM when unused to keep the stylesheet lightweight.
5. **Callback Registration Assurance:** 
   Verify if the `Reconciler` automatically maps properties ending in `Name`/`onChanged` to their corresponding function variables. If not, the `# Api.instance().register_callback` line needs to be properly reintroduced, likely handled during the `Build Phase` to avoid memory leaks.
