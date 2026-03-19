# PyThra Widget Polish Report

## 1. Functional Leading and Trailing Icons in `TextField`

### Current State
In `src/pythra/pythra/widgets.py`, the `TextField` widget's `__init__` accepts `leading: Optional[Icon]` and `trailing: Optional[Icon]`. However:
1.  **Bug:** `self.trailing = trailing` is missing from the `__init__` body.
2.  **Implementation:** The HTML stub generator (`_generate_html_stub`) currently ignores both properties entirely.
3.  **Reconciler limitation:** Because `TextField` uses a custom `_generate_html_stub`, the standard PyThra child-appending logic places any `children` at the very end of the root `<div>`, not perfectly aligned next to the `<input>` element where they belong.

### Implementation Plan
To fix this efficiently without breaking the reconciler:
1.  **Extract Data in `render_props`**: Instead of trying to mount `Icon` widgets as standard children (which would require complex DOM slotting), we can extract the raw icon names and font families directly in `TextField.render_props()`:
    ```python
    "leading_icon": self.leading.icon_name if self.leading else None,
    "leading_family": self.leading.font_family if self.leading else None,
    "trailing_icon": self.trailing.icon_name if self.trailing else None,
    "trailing_family": self.trailing.font_family if self.trailing else None,
    ```
2.  **Update `_generate_html_stub`**: Inject the standard FontAwesome HTML directly into the text field container layout:
    ```html
    <div class="textfield-container {base_class}">
        {f'<i class="{leading_family} fa-{leading_icon} textfield-icon leading"></i>' if leading_icon else ''}
        <input ... >
        {f'<i class="{trailing_family} fa-{trailing_icon} textfield-icon trailing"></i>' if trailing_icon else ''}
        <label ...>
    </div>
    ```
3.  **Update CSS**: Add styles for `.textfield-icon` to position them absolutely (or use flexbox on the `.textfield-container`) with appropriate padding adjustments on the `<input>` element itself depending on whether the icons are present (e.g., `padding-left: 48px` if leading exists).

---

## 2. Material-Style Outlined Labels (Sitting on the Top Border)

### Current State
When `filled=False` (outlined mode), the label currently translates upwards:
`transform: translateY(-24px) scale(0.75);`
However, it stays *inside* or floating above the box, and the top border line cuts straight through it because there is no visual cutout.

### Implementation Plan
Material Design achieves the "label on border" effect by either using a physical SVG cutout (complex) or a simple CSS masking trick (highly effective).

1.  **CSS Trick**: Apply a `background-color` to the floating label that matches the app's background color. This "erases" the top border line behind the text.
2.  **Positioning**: Adjust the `transform: translateY(...)` so the mathematical center of the label intersects exactly with the top border line.
3.  **Dynamic CSS Generation**: 
    ```css
    /* Resting state (inside the box) */
    .textfield-root-container.{css_class} .textfield-label {{
        position: absolute; 
        left: 16px; 
        top: 18px; 
        padding: 0 4px; /* Add padding for the cutout effect */
        background-color: transparent; /* Transparent when resting */
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.2s;
    }}

    /* Floating state (on the border) */
    .textfield-root-container.{css_class} .textfield-input:focus ~ .textfield-label,
    .textfield-root-container.{css_class} .textfield-input:not(:placeholder-shown) ~ .textfield-label {{
        /* Precise translation up to the border */
        transform: translateY(-28px) scale(0.75); 
        /* Match page background to hide the border line behind it */
        /* E.g. Colors.surface or a hardcoded fallback like #FFFFFF */
        background-color: {surface_color_from_theme_or_scaffold}; 
    }}
    ```
    *Note: To make the `background-color` match perfectly, we may need to add a `scaffoldBackgroundColor` fallback to `InputDecoration`, or inherit it via CSS variables.*

---

## 3. Investigation of Other Widgets

Here is a brief assessment of other input/interactive widgets in `widgets.py` and `widgets_more.py` that could use similar architectural polish:

### `Dropdown` / `VirtualDropdown`
*   **Current State:** Highly functional but relies on complex absolute positioning and Javascript bridges for menu toggling.
*   **Improvement:** Ensure the Dropdown button styling shares the exact same `InputDecoration` logic as `TextField` so forms look cohesive. Currently, Dropdown has its own `DropdownTheme` which scales differently than `InputDecoration`.

### `Switch` / `Checkbox` / `Radio`
*   **Current State:** Working well, but CSS animations are strictly hardcoded. The `Switch` had the `onChanged` vs `onPressed` bug (recently fixed).
*   **Improvement:** Native HTML input states (`:checked`) are utilized well, but we should add focus rings (`:focus-visible`) for keyboard navigation accessibility, tying into a global focus color theme.

### `Slider`
*   **Current State:** Relies on `slider.js` for interaction tracking.
*   **Improvement:** The "halo" or overlay effect when dragging is implemented via JS. This could be modernized to pure CSS using `::after` pseudo-elements transitioning on the `:active` pseudo-class for slightly better performance.

### `Button` (Elevated, Text, Icon)
*   **Current State:** Good Material 3 approximations.
*   **Improvement:** They currently lack the "Ink Ripple" effect (Material touch feedback). This can be achieved with a relatively simple lightweight JS module or clever CSS keyframes on active clicks. TextField could also use a slight hover-opacity transition on the unfilled borders to fully match M3 guidelines.
