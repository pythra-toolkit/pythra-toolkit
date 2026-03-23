# Architectural Report: Implementing Interactive States (Hover, Focus, Pressed)

**Date**: March 2026
**Topic**: Should widgets handle their own interactive states (hover, focus) dynamically via callbacks/`GestureDetector`, or should it be offloaded to child styles or a dedicated wrapper?

---

## 1. How Flutter Handles It

Flutter renders everything onto a generic 2D HTML/Skia canvas. Because a canvas has no native concept of a "button" or "hover state" baked into the renderer like CSS does, Flutter *must* process these input events manually in Dart logic.

The responsibilities in Flutter are starkly divided:

1. **`MouseRegion` (Hover Logic)**
   This is a widget dedicated exclusively to tracking the mouse cursor entering, exiting, or hovering over an area.
   - It fires `onEnter`, `onExit`, and `onHover` callbacks.
   - If you wrap a `Container` in a `MouseRegion` and perform a `setState()` on hover, you are manually rebuilding the UI just to change the container's color.

2. **`Focus` and `FocusNode` (Focus Logic)**
   A widget to participate in the focus tree (keyboard navigation, tab order).
   - Fires `onFocusChange`.

3. **`InkWell` / `GestureDetector` (Tap / Splash Logic)**
   - `GestureDetector` parses raw pointers into semantic taps, drags, scales.
   - `InkWell` specifically handles the physical "splash" (ripple radius growing over time) and binds mouse regions to trigger focus/hover overlays.

4. **`WidgetStateProperty` / `MaterialStateProperty` (Styling System)**
   Because buttons need to react visually to 5+ states (hovered, focused, pressed, disabled, dragged), flutter introduced `WidgetStateProperty.resolveWith((states) => ...)` so the button can ask its style: "I am hovered and focused—what color should I be?"

**The Problem**: In Flutter, a user moving their mouse rapidly over 10 buttons causes 10 internal UI rebuilds on the Dart thread just to paint highlight overlays!

---

## 2. PyThra’s "Unfair Advantage": The DOM & CSS

PyThra builds on QtWebEngine (Chromium). The DOM + CSS is arguably the most highly optimized engine on earth for managing interactive hover states.

If PyThra adopted the exact same literal architecture as Flutter, here is what would happen:
1. User hovers over a deeply nested button.
2. JS fires a `mouseenter` event.
3. IPC Bridge marshalls JSON payload to Python API.
4. Python `onEnter` callback fires, modifying a python `is_hovered` variable.
5. Python triggers `setState()`.
6. PyThra Reconciler computes diffs and rebuilds identical HTML.
7. Python generates CSS rule with new background color.
8. Bridge sends thousands of bytes of JSON patch to JS over IPC.
9. JS evaluates string.
...All for a simple hover effect. **This would crush the app's responsiveness and create noticeable latency.**

### The Correct PyThra Architecture

We must bisect interactive states into two completely separate paradigms: **Declarative Styling** vs. **Imperative Logic**.

#### Paradigm A: Declarative Styling (Pure CSS)
For 90% of use cases, developers only want to *change the look* of a widget when it is hovered, focused, or disabled.

PyThra should expose a system akin to `WidgetStateProperty` (or simply direct style kwargs like `hoverStyle`), but instead of checking it at python runtime, **PyThra’s Engine compiles it directly into CSS pseudo-classes during the initial render.**

```python
# The Developer writes:
Container(
    color=Colors.blue,
    hoverStyle=BoxDecoration(color=Colors.red)
)

# PyThra compiles to pure CSS:
.container_hash { background-color: blue; }
.container_hash:hover { background-color: red; }
```
**Benefits:**
- **Zero Python Overhead**: Hover changes instantly at 120fps via native Chromium CSS.
- **Zero Bridge Traffic**: No `setState()` required!

#### Paradigm B: Imperative Logic (Python Callbacks)
For the 10% of use cases where the *logic* of the app must know the user is hovering (e.g. fetching autocomplete suggestions or showing a custom tooltip overlay that requires python logic), PyThra should provide dedicated logic wrappers exactly like Flutter.

1. **`MouseRegion` Widget**
   ```python
   MouseRegion(
       onEnter=lambda e: self.fetch_suggestions(),
       child=TextField()
   )
   ```
   *Implementation*: Emits raw `mouseenter`/`mouseleave` from JS back to Python.

2. **`Focus` Widget**
   ```python
   Focus(
       onFocusChange=lambda has_focus: self.handle_focus(has_focus),
       child=TextField()
   )
   ```
   *Implementation*: Emits `focus`/`blur` events from JS back to Python.

---

## 3. How to Implement This in PyThra

### Step 1: Upgrading `TextStyle` / `BoxDecoration`
Modify your style dictionaries and classes in `pythra` to accept interactive state variants. For example, `WidgetStateProperty` would be incredibly powerful:
```python
ButtonStyle(
    backgroundColor=WidgetStateProperty.all(Colors.blue),
    overlayColor=WidgetStateProperty.resolveWith(lambda states: Colors.white if WidgetState.HOVERED in states else None)
)
```
In `core.py`, when calling `generate_css_rule()`, evaluate this property for all known CSS pseudo-states (`:hover`, `:focus`, `:active`, `:disabled`), and generate a compound CSS rule for each one.

### Step 2: Interactive Wrappers (`HoverBuilder`, `FocusBuilder`)
If developers want their entire Python DOM tree structure to fundamentally morph based on hover (e.g. adding children to the DOM only on hover), create a Stateful widget that intercepts `MouseRegion`:
```python
HoverBuilder(
    builder=lambda is_hovered: Text("Hovered!" if is_hovered else "Resting")
)
```

### Step 3: Upgrading Core Widgets
The core `Widget` base class or `Container` should optionally accept `hoverStyle`, `focusStyle`, and `activeStyle` parameters mapping directly to CSS pseudo-classes. Ensure `reconciler.py` diffs these appropriately.

## 4. Conclusion

- Do **NOT** use `GestureDetector` or a python callback loop to manage purely visual hover/focus effects. The IPC latency overhead makes it unviable.
- **DO** embrace CSS pseudo-classes. Compile interactive python style properties into `:hover` and `:focus` selectors in `generate_css_rule()`.
- **DO** introduce `MouseRegion` and `FocusNode` wrappers exclusively for triggering Python/backend **logic** on hover and focus events, rather than driving core visuals.
