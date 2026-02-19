#pythra/styles.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Union, Tuple, List, Dict, Any
import re # For hex validation
import math # For Matrix4 calculations

from .base import make_hashable

#Colors = Color()

# framework/styles.py

from typing import Union

class EdgeInsets:
    left_c=0
    top_c=0
    right_c=0 
    bottom_c=0
    """
    Represents padding or margin for a widget's edges.
    Compatible with reconciliation (hashable).
    """
    def __init__(self, left: float = 0.0, top: float = 0.0, right: float = 0.0, bottom: float = 0.0):
        """
        Initializes EdgeInsets. Values assumed to be pixels.

        Args:
            left (float): Padding/margin value for the left side. Defaults to 0.
            top (float): Padding/margin value for the top side. Defaults to 0.
            right (float): Padding/margin value for the right side. Defaults to 0.
            bottom (float): Padding/margin value for the bottom side. Defaults to 0.
        """
        self.left = max(-500.0, left)   # Ensure non-negative
        self.top = max(-500.0, top)
        self.right = max(-500.0, right)
        self.bottom = max(-500.0, bottom)

    # --- Static Constructors ---
    @staticmethod
    def all(value: float) -> 'EdgeInsets':
        """Creates EdgeInsets with the same value for all four sides."""
        val = max(-500.0, value)
        return EdgeInsets(left=val, top=val, right=val, bottom=val)

    @staticmethod
    def symmetric(horizontal: float = 0.0, vertical: float = 0.0) -> 'EdgeInsets':
        """Creates EdgeInsets with symmetric horizontal and vertical values."""
        h = max(-500.0, horizontal)
        v = max(-500.0, vertical)
        return EdgeInsets(left=h, right=h, top=v, bottom=v)

    @staticmethod
    def only(left: float = 0.0, top: float = 0.0, right: float = 0.0, bottom: float = 0.0) -> 'EdgeInsets':
         """Creates EdgeInsets with only the specified values set, others default to 0."""
         # Alias for the main constructor with clearer intent
         EdgeInsets.left_c=left
         EdgeInsets.top_c=top
         EdgeInsets.right_c=right
         EdgeInsets.bottom_c=bottom
         return EdgeInsets(left=left, top=top, right=right, bottom=bottom)

    @staticmethod
    def edit(operation: str='+',left: float = 0.0, top: float = 0.0, right: float = 0.0, bottom: float = 0.0) -> 'EdgeInsets':
        if operation == '+':
            left += EdgeInsets.left_c
            top += EdgeInsets.top_c
            right += EdgeInsets.right_c
            bottom += EdgeInsets.bottom_c
        elif operation == '-':
            left = EdgeInsets.left_c - left 
            top = EdgeInsets.top_c - top
            right = EdgeInsets.right_c - right
            bottom = EdgeInsets.bottom_c - bottom
        return EdgeInsets(left=left, top=top, right=right, bottom=bottom)

    

    # Deprecate or remove LRTB if 'only' is preferred for clarity
    # @staticmethod
    # def LRTB(...)

    # --- CSS Conversion ---
    def to_css_value(self) -> str:
        """
        Returns the CSS value string for padding/margin properties
        (e.g., '10px 5px 10px 5px'). Uses shorthand if possible.
        """
        # Check for simplifications
        if self.left == self.top == self.right == self.bottom:
            return f"{self.top}px" # All same: top
        if self.top == self.bottom and self.left == self.right:
            return f"{self.top}px {self.right}px" # Vertical Horizontal
        if self.left == self.right:
            return f"{self.top}px {self.right}px {self.bottom}px" # Top Horizontal Bottom
        # Full definition: Top Right Bottom Left
        return f"{self.top}px {self.right}px {self.bottom}px {self.left}px"

    def to_css(self) -> str:
        """
        Returns the full CSS padding or margin property string
        (e.g., 'padding: 10px 5px;').
        NOTE: Property name ('padding' or 'margin') must be added by caller.
        """
        # Return only the value part, property name decided by context
        return self.to_css_value() # Just return the value

    # --- Calculations ---
    def to_int_vertical(self) -> float: # Changed to float as inputs are float
        """Calculates the total vertical padding/margin (top + bottom)."""
        return self.top + self.bottom

    def to_int_horizontal(self) -> float: # Changed to float
        """Calculates the total horizontal padding/margin (left + right)."""
        return self.right + self.left

    # --- Compatibility Methods ---
    def __eq__(self, other):
        if not isinstance(other, EdgeInsets):
            return NotImplemented
        return (self.left == other.left and
                self.top == other.top and
                self.right == other.right and
                self.bottom == other.bottom)

    def __hash__(self):
        return hash((self.left, self.top, self.right, self.bottom))

    def __repr__(self):
         if self.left == self.top == self.right == self.bottom:
              return f"EdgeInsets.all({self.left})"
         if self.left == self.right and self.top == self.bottom:
              # Handle case where horizontal and vertical are also equal (covered by all)
              if self.left == self.top: return f"EdgeInsets.all({self.left})"
              return f"EdgeInsets.symmetric(horizontal={self.left}, vertical={self.top})"
         # Use 'only' for clarity if some values are 0
         args = []
         if self.left != 0.0: args.append(f"left={self.left}")
         if self.top != 0.0: args.append(f"top={self.top}")
         if self.right != 0.0: args.append(f"right={self.right}")
         if self.bottom != 0.0: args.append(f"bottom={self.bottom}")
         if not args: return "EdgeInsets()" # All zero
         return f"EdgeInsets.only({', '.join(args)})"


    def to_dict(self) -> Dict[str, float]:
         """Returns a simple dictionary representation."""
         return {'left': self.left, 'top': self.top, 'right': self.right, 'bottom': self.bottom}

    # --- ADDED to_tuple ---
    def to_tuple(self) -> Tuple[float, float, float, float]:
         """Returns a hashable tuple representation (left, top, right, bottom)."""
         return (self.left, self.top, self.right, self.bottom)


# print("Edge Insets", EdgeInsets.only(top=40, left=20).edit(operation='-',top=10))

class Alignment:
    """
    Represents alignment for widgets using flexbox concepts (justify-content, align-items).
    Ensures compatibility with reconciliation by being hashable.

    Attributes:
        justify_content (str): CSS value for justify-content (main axis alignment).
        align_items (str): CSS value for align-items (cross axis alignment).
    """
    def __init__(self, justify_content: str, align_items: str):
        """
        Initializes Alignment. It's recommended to use the static methods
        like Alignment.center(), Alignment.top_left(), etc.

        Args:
            justify_content (str): CSS value like 'flex-start', 'center', 'flex-end',
                                  'space-between', 'space-around', 'space-evenly'.
            align_items (str): CSS value like 'flex-start', 'center', 'flex-end',
                                'stretch', 'baseline'.
        """
        # Consider adding validation for allowed CSS values if needed
        self.justify_content = justify_content
        self.align_items = align_items

    # --- Static Constructors (Convenience Methods) ---
    @staticmethod
    def center():
        return Alignment('center', 'center')

    @staticmethod
    def top_left():
        return Alignment('flex-start', 'flex-start')

    @staticmethod
    def top_center():
        return Alignment('center', 'flex-start')

    @staticmethod
    def top_right():
        return Alignment('flex-end', 'flex-start')

    @staticmethod
    def center_left():
        return Alignment('flex-start', 'center')

    @staticmethod
    def center_right():
        return Alignment('flex-end', 'center')

    @staticmethod
    def bottom_left():
        return Alignment('flex-start', 'flex-end')

    @staticmethod
    def bottom_center():
        return Alignment('center', 'flex-end')

    @staticmethod
    def bottom_right():
        return Alignment('flex-end', 'flex-end')

    # Add others if needed, e.g., space_between variants
    @staticmethod
    def space_between_center(): # Example
        return Alignment('space-between', 'center')

    # --- Compatibility Methods ---

    def to_css_dict(self) -> dict:
        """
        Returns alignment properties as a dictionary suitable for CSS generation
        or applying as inline styles. Includes display:flex.
        """
        return {
            'display': 'flex',
            'justify-content': self.justify_content,
            'align-items': self.align_items
        }

    def to_css(self) -> str:
        """
        Converts the Alignment object to a CSS string snippet for flexbox layout.
        Includes display: flex.
        """
        return f"display: flex; justify-content: {self.justify_content}; align-items: {self.align_items};"

    # --- Add __eq__ and __hash__ for compatibility with style keys ---
    def __eq__(self, other):
        if not isinstance(other, Alignment):
            return NotImplemented
        return (self.justify_content == other.justify_content and
                self.align_items == other.align_items)

    def __hash__(self):
        # Hash a tuple of the relevant attributes
        return hash((self.justify_content, self.align_items))

    # --- Optional: Add representation for debugging ---
    def __repr__(self):
         # Try to find matching static method name for cleaner repr (optional)
         for name, method in Alignment.__dict__.items():
             if isinstance(method, staticmethod):
                 try:
                     instance = method.__func__() # Call the static method
                     if instance == self:
                          return f"Alignment.{name}()"
                 except Exception: # Catch potential errors during static method call
                     pass
         # Fallback representation
         return f"Alignment(justify_content='{self.justify_content}', align_items='{self.align_items}')"

    # --- Optional: Add method for reconciler prop representation ---
    def to_dict(self):
         """Returns a simple dictionary representation."""
         return {'justify_content': self.justify_content, 'align_items': self.align_items}

    # --- Optional: Add method for hashable tuple representation ---
    def to_tuple(self):
         """Returns a hashable tuple representation."""
         return (self.justify_content, self.align_items)

class TextAlign:
    """
    Represents horizontal text alignment options. Compatible with reconciliation.

    Attributes:
        value (str): The CSS text-align value (e.g., 'left', 'center', 'right', 'justify', 'start', 'end').
    """
    # Define constants for common values directly on the class
    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'
    JUSTIFY = 'justify'
    START = 'start' # Respects LTR/RTL directionality
    END = 'end'     # Respects LTR/RTL directionality

    def __init__(self, value: str):
        """
        Initializes TextAlign. Using class constants like TextAlign.CENTER is recommended.

        Args:
            value (str): A valid CSS text-align value.
        """
        # Optional: Add validation for allowed CSS values
        allowed_values = {self.LEFT, self.RIGHT, self.CENTER, self.JUSTIFY, self.START, self.END}
        if value not in allowed_values:
             # Or raise ValueError('Invalid TextAlign value')
             print(f"Warning: Using potentially invalid TextAlign value: '{value}'")
        self.value = value

    # --- Static Constructors (Optional, can use constants directly) ---
    @staticmethod
    def center(): return TextAlign(TextAlign.CENTER)
    @staticmethod
    def left(): return TextAlign(TextAlign.LEFT)
    @staticmethod
    def right(): return TextAlign(TextAlign.RIGHT)
    @staticmethod
    def justify(): return TextAlign(TextAlign.JUSTIFY)
    @staticmethod
    def start(): return TextAlign(TextAlign.START)
    @staticmethod
    def end(): return TextAlign(TextAlign.END)

    # --- Compatibility Methods ---

    def to_css_dict(self) -> dict:
        """Returns the CSS property as a dictionary."""
        return {'text-align': self.value}

    def to_css(self) -> str:
        """Returns the CSS property string (e.g., 'text-align: center;')."""
        return f"text-align: {self.value};"

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, TextAlign):
            return NotImplemented
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    # --- Representation ---
    def __repr__(self):
         # Try matching constants for cleaner representation
         for name, val in TextAlign.__dict__.items():
             if isinstance(val, str) and val == self.value: # Check class constants
                 return f"TextAlign.{name}"
         # Fallback
         return f"TextAlign('{self.value}')"

    # --- Reconciler Prop Representation ---
    def to_dict(self): return {'value': self.value}
    def to_tuple(self): return (self.value,) # Tuple for make_hashable

# --- BoxConstraints Refactored ---
class BoxConstraints:
    """
    Represents min/max width and height constraints for a widget.
    Compatible with reconciliation.
    """
    def __init__(self,
                 minWidth: Optional[float] = 0.0, # Default min width is 0
                 maxWidth: Optional[float] = float('inf'), # Default max width is infinity
                 minHeight: Optional[float] = 0.0, # Default min height is 0
                 maxHeight: Optional[float] = float('inf') # Default max height is infinity
                ):
        """
        Initializes BoxConstraints. Use float('inf') for unbounded max values.
        Units are assumed to be pixels for CSS conversion.

        Args:
            minWidth (float): Minimum width (default 0).
            maxWidth (float): Maximum width (default infinity).
            minHeight (float): Minimum height (default 0).
            maxHeight (float): Maximum height (default infinity).
        """
        # Validate inputs (ensure non-negative, min <= max)
        self.minWidth = max(0.0, minWidth) if minWidth is not None else 0.0
        self.maxWidth = max(self.minWidth, maxWidth) if maxWidth is not None else float('inf')
        self.minHeight = max(0.0, minHeight) if minHeight is not None else 0.0
        self.maxHeight = max(self.minHeight, maxHeight) if maxHeight is not None else float('inf')

    # --- Static Constructors (Optional) ---
    @staticmethod
    def tight(width: float, height: float):
        """Creates constraints forcing a specific size."""
        return BoxConstraints(minWidth=width, maxWidth=width, minHeight=height, maxHeight=height)

    @staticmethod
    def expand(width: Optional[float] = None, height: Optional[float] = None):
         """Creates constraints forcing maximum size (infinity)."""
         return BoxConstraints(minWidth=width or 0.0, maxWidth=float('inf'),
                               minHeight=height or 0.0, maxHeight=float('inf'))

    # --- Compatibility Methods ---

    def to_css_dict(self) -> dict:
        """Returns constraints as a dictionary of CSS properties."""
        styles = {}
        # Only include constraints that are not default (0 for min, inf for max)
        if self.minWidth > 0.0: styles['min-width'] = f"{self.minWidth}px"
        if self.maxWidth != float('inf'): styles['max-width'] = f"{self.maxWidth}px"
        if self.minHeight > 0.0: styles['min-height'] = f"{self.minHeight}px"
        if self.maxHeight != float('inf'): styles['max-height'] = f"{self.maxHeight}px"
        return styles

    def to_css(self) -> str:
        """Converts constraints to a CSS string snippet."""
        style_dict = self.to_css_dict()
        return " ".join(f"{prop}: {value};" for prop, value in style_dict.items())

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, BoxConstraints):
            return NotImplemented
        return (self.minWidth == other.minWidth and
                self.maxWidth == other.maxWidth and
                self.minHeight == other.minHeight and
                self.maxHeight == other.maxHeight)

    def __hash__(self):
        # Hash a tuple of the defining attributes
        return hash((self.minWidth, self.maxWidth, self.minHeight, self.maxHeight))

    # --- Representation ---
    def __repr__(self):
        props = []
        if self.minWidth != 0.0: props.append(f"minWidth={self.minWidth}")
        if self.maxWidth != float('inf'): props.append(f"maxWidth={self.maxWidth}")
        if self.minHeight != 0.0: props.append(f"minHeight={self.minHeight}")
        if self.maxHeight != float('inf'): props.append(f"maxHeight={self.maxHeight}")
        return f"BoxConstraints({', '.join(props)})"

    # --- Reconciler Prop Representation ---
    def to_dict(self):
         return {'minWidth': self.minWidth, 'maxWidth': self.maxWidth,
                 'minHeight': self.minHeight, 'maxHeight': self.maxHeight}

    def to_tuple(self):
         """Returns a hashable tuple representation."""
         return (self.minWidth, self.maxWidth, self.minHeight, self.maxHeight)

class Color:
    """
    Provides utility methods for defining CSS colors (hex, rgba)
    and defines common Material Design 3 color role constants (approximations).

    Usage:
        color = Colors.primary
        custom_hex = Colors.hex("#FF5733")
        transparent_red = Colors.rgba(255, 0, 0, 0.5)
    """   

    # --- Material Design 3 Color Role Constants ---
    # Primary Palette
    primary = 'var(--md-sys-color-primary)'
    onPrimary = 'var(--md-sys-color-on-primary)'
    primaryContainer = 'var(--md-sys-color-primary-container)'
    onPrimaryContainer = 'var(--md-sys-color-on-primary-container)'
    # Secondary Palette
    secondary = 'var(--md-sys-color-secondary)'
    onSecondary = 'var(--md-sys-color-on-secondary)'
    secondaryContainer = 'var(--md-sys-color-secondary-container)'
    onSecondaryContainer = 'var(--md-sys-color-on-secondary-container)'
    # Tertiary Palette
    tertiary = 'var(--md-sys-color-tertiary)'
    onTertiary = 'var(--md-sys-color-on-tertiary)'
    tertiaryContainer = 'var(--md-sys-color-tertiary-container)'
    onTertiaryContainer = 'var(--md-sys-color-on-tertiary-container)'
    # Error Palette
    error = 'var(--md-sys-color-error)'
    onError = 'var(--md-sys-color-on-error)'
    errorContainer = 'var(--md-sys-color-error-container)'
    onErrorContainer = 'var(--md-sys-color-on-error-container)'
    # Neutral Palette (Surface Tones)
    background = 'var(--md-sys-color-background)'
    onBackground = 'var(--md-sys-color-on-background)'
    surface = 'var(--md-sys-color-surface)'
    onSurface = 'var(--md-sys-color-on-surface)'
    surfaceVariant = 'var(--md-sys-color-surface-variant)'
    onSurfaceVariant = 'var(--md-sys-color-on-surface-variant)'
    outline = 'var(--md-sys-color-outline)'
    outlineVariant = 'var(--md-sys-color-outline-variant)'
    shadow = 'var(--md-sys-color-shadow)'
    scrim = 'var(--md-sys-color-scrim)'
    # Inverse Tones
    inverseSurface = 'var(--md-sys-color-inverse-surface)'
    inverseOnSurface = 'var(--md-sys-color-inverse-on-surface)'
    inversePrimary = 'var(--md-sys-color-inverse-primary)'
    # Fixed Tones (Less common in M3 theming but sometimes useful)
    # surfaceBright = '#FFFBFE'
    # surfaceDim = '#DED8E1'
    # surfaceContainerLowest = '#FFFFFF'
    # surfaceContainerLow = '#F7F2FA'
    # surfaceContainer = '#F3EDF7'
    # surfaceContainerHigh = '#ECE6F0'
    # surfaceContainerHighest = '#E6E0E9'

    # --- Common CSS Named Colors ---
    # Can be added if needed, but M3 roles are preferred
    red = 'red'
    blue = 'blue'
    green = 'green'
    white = 'white'
    black = 'black'
    grey = 'grey' # Or gray
    lightgrey = 'lightgrey' # Or lightgray
    darkgrey = 'darkgrey' # Or darkgray
    transparent = 'transparent'


    def __getattr__(self, name):
        """
        Retrieves the color name as an attribute of the class.
        
        Args:
            name (str): The name of the color attribute.

        Returns:
            str: The color name.
        """
        return name


    # --- Utility Methods ---
    @staticmethod
    def hex(hex_code: str) -> str:
        """
        Validates and returns a hexadecimal color code string (e.g., "#RRGGBB" or "#RGB").

        Args:
            hex_code (str): A hexadecimal color code string.

        Raises:
            ValueError: If the hex code is not in a valid format.

        Returns:
            str: The validated hex color code.
        """
        hex_code = hex_code.strip()
        # Basic validation for # followed by 3, 4, 6, or 8 hex digits
        if not re.match(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", hex_code):
            raise ValueError(f"Invalid hex code format: '{hex_code}'. Should be #RGB, #RGBA, #RRGGBB, or #RRGGBBAA.")
        return hex_code

    @staticmethod
    def gradient(direction: str, color, color2, color3=None, color4=None, color5=None) -> str:
        """
        Validates and returns a hexadecimal color code string (e.g., "#RRGGBB" or "#RGB").

        Args:
            hex_code (str): A hexadecimal color code string.

        Raises:
            ValueError: If the hex code is not in a valid format.

        Returns:
            str: The validated hex color code.
        """
        # hex_code = hex_code.strip()
        # # Basic validation for # followed by 3, 4, 6, or 8 hex digits
        # if not re.match(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", hex_code):
        #     raise ValueError(f"Invalid hex code format: '{hex_code}'. Should be #RGB, #RGBA, #RRGGBB, or #RRGGBBAA.")
        comma=", "
        return f"linear-gradient({direction}, {color}, {color2+comma if color3 else color2}{color3+comma if color3 else ""}{color4+comma if color4 else ""}{color5+comma if color5 else ""})"

    @staticmethod
    def rgba(red: int, green: int, blue: int, alpha: float) -> str:
        """
        Creates an rgba() CSS color string.

        Args:
            red (int): Red component (0-255).
            green (int): Green component (0-255).
            blue (int): Blue component (0-255).
            alpha (float): Alpha/opacity component (0.0 to 1.0).

        Raises:
            ValueError: If color components or alpha are out of range.

        Returns:
            str: The rgba(R, G, B, A) color string.
        """
        if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
            raise ValueError("RGB values must be between 0 and 255.")
        if not (0.0 <= alpha <= 1.0):
             raise ValueError("Alpha value must be between 0.0 and 1.0.")
        # Corrected order: R, G, B, A
        return f"rgba({red}, {green}, {blue}, {alpha})"

    @staticmethod
    def adaptive(light: str, dark: str) -> str:
        """
        Creates a custom color that adapts to the theme mode.
        Registers the values with ThemeManager and returns a CSS variable.
        """
        from .theme import ThemeManager
        return ThemeManager.instance().register_dynamic_color(light, dark)

    # --- Removed __getattr__ ---
    # def __getattr__(self, name): ...
Colors = Color()

# Assume Offset helper exists or define it here/import
# Example definition if needed:
class Offset:
     def __init__(self, dx: float, dy: float):
         self.dx = dx
         self.dy = dy
     def to_css(self):
         return f"{self.dx}px {self.dy}px"
     def __eq__(self, other):
         return isinstance(other, Offset) and self.dx == other.dx and self.dy == other.dy
     def __hash__(self):
         return hash((self.dx, self.dy))
     def __repr__(self):
         return f"Offset({self.dx}, {self.dy})"
# End Example Offset definition

class BoxShadow:
    """
    Represents a CSS box-shadow effect. Compatible with reconciliation.
    """
    def __init__(self,
                 color: str = 'rgba(0,0,0,0.2)', # Default shadow color
                 offset: Offset = Offset(0, 2), # Default offset (dx, dy)
                 blurRadius: float = 4.0, # Default blur
                 spreadRadius: float = 0.0, # Default spread
                 # Add inset keyword if needed later
                 ):
        """
        Initializes the box shadow.

        Args:
            color (str): The color of the shadow (CSS color string).
            offset (Offset): An Offset object specifying dx and dy.
            blurRadius (float): The blur radius in pixels. Must be non-negative.
            spreadRadius (float): The spread radius in pixels.
        """
        self.color = color
        if not isinstance(offset, Offset):
             raise TypeError("offset must be an Offset instance.")
        self.offset = offset
        self.blurRadius = max(0.0, blurRadius) # Ensure non-negative
        self.spreadRadius = spreadRadius

    # --- Compatibility Methods ---

    def to_css(self) -> str:
        """
        Converts the box shadow to a CSS box-shadow value string.
        Format: offset-x offset-y blur-radius spread-radius color
        """
        # Format: h-offset v-offset blur spread color
        return f'{self.offset.dx}px {self.offset.dy}px {self.blurRadius}px {self.spreadRadius}px {self.color}'

    def to_css_dict(self) -> dict:
         """Returns the CSS property as a dictionary."""
         return {'box-shadow': self.to_css()}

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, BoxShadow):
            return NotImplemented
        return (self.color == other.color and
                self.offset == other.offset and
                self.blurRadius == other.blurRadius and
                self.spreadRadius == other.spreadRadius)

    def __hash__(self):
        # Hash a tuple of the relevant attributes
        # Ensure offset is hashable (Offset class needs __hash__)
        return hash((self.color, self.offset, self.blurRadius, self.spreadRadius))

    # --- Representation ---
    def __repr__(self):
        return f"BoxShadow(color='{self.color}', offset={self.offset!r}, blurRadius={self.blurRadius}, spreadRadius={self.spreadRadius})"

    # --- Reconciler Prop Representation ---
    def to_dict(self):
         return {'color': self.color, 'offset': {'dx': self.offset.dx, 'dy': self.offset.dy},
                 'blurRadius': self.blurRadius, 'spreadRadius': self.spreadRadius}

    def to_tuple(self):
         """Returns a hashable tuple representation."""
         # Hash offset's tuple representation if Offset is complex
         return (self.color, self.offset, self.blurRadius, self.spreadRadius)



# --- ClipBehavior Refactored (Using Enum) ---
class ClipBehavior:
    """Specifies how content should be clipped."""
    NONE = 'none' # CSS overflow: visible (effectively)
    HARD_EDGE = 'hardEdge' # CSS overflow: hidden
    ANTI_ALIAS = 'antiAlias' # CSS overflow: hidden (visual effect not guaranteed)
    ANTI_ALIAS_WITH_SAVE_LAYER = 'antiAliasWithSaveLayer' # CSS overflow: hidden (effect not CSS)

    def to_css_overflow(self) -> Optional[str]:
         """Maps enum value to CSS overflow property value."""
         if self == ClipBehavior.NONE:
              return 'visible' # Or None if default is desired
         elif self in [ClipBehavior.HARD_EDGE, ClipBehavior.ANTI_ALIAS, ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER]:
              return 'hidden'
         return None # Default or unmapped

# --- ImageFit (Keep as String Constants) ---
class ImageFit:
    """CSS object-fit values."""
    CONTAIN = 'contain'
    COVER = 'cover'
    FILL = 'fill'
    NONE = 'none'
    SCALE_DOWN = 'scale-down'

# --- MainAxisSize (Keep as conceptual values) ---
class MainAxisSize:
    """Conceptual sizing behavior for main axis in Flex/Row/Column."""
    MIN = 'min' # Wrap content size
    MAX = 'max' # Fill available space

# --- Axis Constants ---
class Axis:
    """Specifies the primary direction for layout widgets like Flex, ListView."""
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'

# --- MainAxisAlignment Constants (for Flexbox justify-content) ---
class MainAxisAlignment:
    """How children should be placed along the main axis in a flex layout."""
    START = 'flex-start'
    END = 'flex-end'
    CENTER = 'center'
    SPACE_BETWEEN = 'space-between'
    SPACE_AROUND = 'space-around'
    SPACE_EVENLY = 'space-evenly'

# --- CrossAxisAlignment Constants (for Flexbox align-items) ---
class CrossAxisAlignment:
    """How children should be placed along the cross axis in a flex layout."""
    START = 'flex-start'
    END = 'flex-end'
    CENTER = 'center'
    STRETCH = 'stretch' # Make children fill the cross axis.
    BASELINE = 'baseline' # Align children along their text baseline.

class Double:
    INFINITY = '-webkit-fill-available'
    INHERIT = 'inherit'
    INITIAL = 'initial'

class TextStyle:
    """
    Holds styling information for text (font, color, decoration, etc.).
    Compatible with reconciliation.
    """
    def __init__(self,
                 color: Optional[str] = None,
                 # Font properties
                 fontFamily: Optional[str] = None, # e.g., 'Roboto', 'Arial', sans-serif
                 fontSize: Optional[Union[int, float]] = None, # Assumed px
                 fontWeight: Optional[Union[str, int]] = None, # e.g., 'bold', 'normal', 400, 700
                 fontStyle: Optional[str] = None, # e.g., 'italic', 'normal'
                 # Spacing
                 letterSpacing: Optional[Union[int, float, str]] = None, # number (px) or string ('normal')
                 wordSpacing: Optional[Union[int, float, str]] = None, # number (px) or string ('normal')
                 lineHeight: Optional[Union[int, float, str]] = None, # number (multiplier), px, or 'normal'
                 # Decoration
                 textDecoration: Optional[str] = None, # e.g., 'underline', 'line-through', 'none'
                 decorationColor: Optional[str] = None, # Color of the decoration line
                 decorationStyle: Optional[str] = None, # e.g., 'solid', 'wavy', 'dotted'
                 decorationThickness: Optional[Union[int, float, str]] = None, # number (px) or string ('auto')
                 # Add other properties like textShadow, fontFeatures, etc. if needed
                 ):
        """
        Initializes the TextStyle object.

        Args:
            color: Text color (CSS color string).
            fontFamily: CSS font-family value.
            fontSize: Font size in pixels.
            fontWeight: CSS font-weight value.
            fontStyle: CSS font-style value.
            letterSpacing: CSS letter-spacing value (number assumes px).
            wordSpacing: CSS word-spacing value (number assumes px).
            lineHeight: CSS line-height value (number is multiplier, or include units).
            textDecoration: CSS text-decoration-line value.
            decorationColor: CSS text-decoration-color value.
            decorationStyle: CSS text-decoration-style value.
            decorationThickness: CSS text-decoration-thickness value.
        """
        self.color = color
        self.fontFamily = fontFamily
        self.fontSize = fontSize
        self.fontWeight = fontWeight
        self.fontStyle = fontStyle
        self.letterSpacing = letterSpacing
        self.wordSpacing = wordSpacing
        self.lineHeight = lineHeight
        self.textDecoration = textDecoration
        self.decorationColor = decorationColor
        self.decorationStyle = decorationStyle
        self.decorationThickness = decorationThickness

    # --- Compatibility Methods ---

    def _format_css_value(self, value: Any, default_unit: str = 'px') -> Optional[str]:
        """Helper to format values for CSS, adding units if needed."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return f"{value}{default_unit}"
        return str(value) # Assume string values are already correct CSS values

    def to_css_dict(self) -> Dict[str, str]:
        """Converts text style properties to a dictionary of CSS styles."""
        styles = {}
        if self.color: styles['color'] = self.color
        if self.fontFamily: styles['font-family'] = self.fontFamily
        if self.fontSize: styles['font-size'] = self._format_css_value(self.fontSize)
        if self.fontWeight: styles['font-weight'] = str(self.fontWeight)
        if self.fontStyle: styles['font-style'] = self.fontStyle
        if self.letterSpacing: styles['letter-spacing'] = self._format_css_value(self.letterSpacing)
        if self.wordSpacing: styles['word-spacing'] = self._format_css_value(self.wordSpacing)
        if self.lineHeight: styles['line-height'] = self._format_css_value(self.lineHeight, default_unit='') # Unitless multiplier is common
        # Combine text-decoration properties if possible
        if self.textDecoration: styles['text-decoration-line'] = self.textDecoration
        if self.decorationColor: styles['text-decoration-color'] = self.decorationColor
        if self.decorationStyle: styles['text-decoration-style'] = self.decorationStyle
        if self.decorationThickness: styles['text-decoration-thickness'] = self._format_css_value(self.decorationThickness)
        # Could try to combine into shorthand `text-decoration` but it's complex
        return styles

    def to_css(self) -> str:
        """Converts text style attributes to a CSS string snippet."""
        style_dict = self.to_css_dict()
        return " ".join(f"{prop}: {value};" for prop, value in style_dict.items())

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, TextStyle):
            return NotImplemented
        # Compare all attributes
        return (self.color == other.color and
                self.fontFamily == other.fontFamily and
                self.fontSize == other.fontSize and
                self.fontWeight == other.fontWeight and
                self.fontStyle == other.fontStyle and
                self.letterSpacing == other.letterSpacing and
                self.wordSpacing == other.wordSpacing and
                self.lineHeight == other.lineHeight and
                self.textDecoration == other.textDecoration and
                self.decorationColor == other.decorationColor and
                self.decorationStyle == other.decorationStyle and
                self.decorationThickness == other.decorationThickness)

    def __hash__(self):
        # Hash a tuple of all attributes
        return hash((
            self.color, self.fontFamily, self.fontSize, self.fontWeight,
            self.fontStyle, self.letterSpacing, self.wordSpacing, self.lineHeight,
            self.textDecoration, self.decorationColor, self.decorationStyle,
            self.decorationThickness
        ))

    # --- Representation ---
    def __repr__(self):
        props = []
        for attr in ['color', 'fontFamily', 'fontSize', 'fontWeight', 'fontStyle',
                     'letterSpacing', 'wordSpacing', 'lineHeight', 'textDecoration',
                     'decorationColor', 'decorationStyle', 'decorationThickness']:
            value = getattr(self, attr)
            if value is not None:
                props.append(f"{attr}={value!r}")
        return f"TextStyle({', '.join(props)})"

    # --- Reconciler Prop Representation ---
    def to_dict(self):
        """Returns a simple dictionary representation."""
        return {attr: getattr(self, attr) for attr in [
            'color', 'fontFamily', 'fontSize', 'fontWeight', 'fontStyle',
            'letterSpacing', 'wordSpacing', 'lineHeight', 'textDecoration',
            'decorationColor', 'decorationStyle', 'decorationThickness'
        ] if getattr(self, attr) is not None}

    def to_tuple(self):
         """Returns a hashable tuple representation."""
         return tuple(getattr(self, attr) for attr in [
            'color', 'fontFamily', 'fontSize', 'fontWeight', 'fontStyle',
            'letterSpacing', 'wordSpacing', 'lineHeight', 'textDecoration',
            'decorationColor', 'decorationStyle', 'decorationThickness'
        ])

# --- BorderStyle Constants ---
class BorderStyle:
    """
    A class representing various border styles.
    
    This class defines the different types of border styles that can be applied to widgets.

    Attributes:
        NONE (str): No border.
        DOTTED (str): Dotted border.
        DASHED (str): Dashed border.
        SOLID (str): Solid border.
        DOUBLE (str): Double border.
        GROOVE (str): Groove border.
        RIDGE (str): Ridge border.
        INSET (str): Inset border.
        OUTSET (str): Outset border.
        HIDDEN (str): Hidden border.
    """
    NONE = 'none'
    DOTTED = 'dotted'
    DASHED = 'dashed'
    SOLID = 'solid'
    DOUBLE ='double'
    GROOVE = 'groove'
    RIDGE = 'ridge'
    INSET = 'inset'
    OUTSET = 'outset'
    HIDDEN = 'hidden'



# --- BorderRadius Refactored ---
class BorderRadius:
    """
    Represents the radius for the corners of a box. Compatible with reconciliation.
    """
    def __init__(self,
                 topLeft: float = 0.0,
                 topRight: float = 0.0,
                 bottomRight: float = 0.0,
                 bottomLeft: float = 0.0):
        """
        Initializes BorderRadius. Values are typically in pixels.

        Args:
            topLeft (float): Radius for the top-left corner.
            topRight (float): Radius for the top-right corner.
            bottomRight (float): Radius for the bottom-right corner.
            bottomLeft (float): Radius for the bottom-left corner.
        """
        self.topLeft = max(0.0, topLeft) # Ensure non-negative
        self.topRight = max(0.0, topRight)
        self.bottomRight = max(0.0, bottomRight)
        self.bottomLeft = max(0.0, bottomLeft)

    # --- Static Constructors ---
    @staticmethod
    def all(value: float) -> 'BorderRadius':
        """Creates a BorderRadius with the same radius for all corners."""
        radius = max(0.0, value)
        return BorderRadius(radius, radius, radius, radius)

    @staticmethod
    def circular(radius: float) -> 'BorderRadius':
         """Creates a BorderRadius with the same radius for all corners (alias for all)."""
         return BorderRadius.all(radius)

    @staticmethod
    def vertical(top: float = 0.0, bottom: float = 0.0) -> 'BorderRadius':
         """Creates a BorderRadius with the same radius for top-left/top-right and bottom-left/bottom-right."""
         top_r = max(0.0, top)
         bottom_r = max(0.0, bottom)
         return BorderRadius(topLeft=top_r, topRight=top_r, bottomRight=bottom_r, bottomLeft=bottom_r)

    @staticmethod
    def horizontal(left: float = 0.0, right: float = 0.0) -> 'BorderRadius':
         """Creates a BorderRadius with the same radius for top-left/bottom-left and top-right/bottom-right."""
         left_r = max(0.0, left)
         right_r = max(0.0, right)
         return BorderRadius(topLeft=left_r, topRight=right_r, bottomRight=right_r, bottomLeft=left_r)

    # --- Compatibility Methods ---

    def to_css_value(self) -> str:
        """
        Returns the CSS value string for the border-radius property
        (e.g., '10px 5px 10px 5px'). Uses shorthand if possible.
        """
        # Check for simplifications
        if self.topLeft == self.topRight == self.bottomRight == self.bottomLeft:
            return f"{self.topLeft}px" # All same
        if self.topLeft == self.bottomRight and self.topRight == self.bottomLeft:
            return f"{self.topLeft}px {self.topRight}px" # Top-left/bottom-right, Top-right/bottom-left
        if self.topRight == self.bottomLeft:
             return f"{self.topLeft}px {self.topRight}px {self.bottomRight}px" # Top-left, Top-right/bottom-left, Bottom-right
        # Full definition
        return f"{self.topLeft}px {self.topRight}px {self.bottomRight}px {self.bottomLeft}px"

    def to_css_dict(self) -> dict:
         """Returns the CSS property as a dictionary."""
         return {'border-radius': self.to_css_value()}

    def to_css(self) -> str:
        """Returns the full CSS property string (e.g., 'border-radius: 10px;')."""
        return f"border-radius: {self.to_css_value()};"

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, BorderRadius):
            return NotImplemented
        return (self.topLeft == other.topLeft and
                self.topRight == other.topRight and
                self.bottomRight == other.bottomRight and
                self.bottomLeft == other.bottomLeft)

    def __hash__(self):
        return hash((self.topLeft, self.topRight, self.bottomRight, self.bottomLeft))

    # --- Representation ---
    def __repr__(self):
         if self.topLeft == self.topRight == self.bottomRight == self.bottomLeft:
              return f"BorderRadius.all({self.topLeft})"
         # Add checks for vertical/horizontal if desired
         return f"BorderRadius(topLeft={self.topLeft}, topRight={self.topRight}, bottomRight={self.bottomRight}, bottomLeft={self.bottomLeft})"

    # --- Reconciler Prop Representation ---
    def to_dict(self):
         return {'topLeft': self.topLeft, 'topRight': self.topRight,
                 'bottomRight': self.bottomRight, 'bottomLeft': self.bottomLeft}

    def to_tuple(self):
         """Returns a hashable tuple representation."""
         return (self.topLeft, self.topRight, self.bottomRight, self.bottomLeft)

class BorderSide:
    """
    Represents the style of a single side of a border.
    Used by BoxDecoration or for individual border properties (border-top, etc.).
    Compatible with reconciliation.
    """
    # Define a constant for no border
    NONE = None # Or potentially an instance: BorderSide(width=0, style=BorderStyle.NONE)

    def __init__(self,
                 width: float = 1.0, # Default width
                 style: str = BorderStyle.SOLID, # Default style
                 color: str = Colors.black # Default color
                 # Removed borderRadius - Radius applies to the box (BorderRadius), not a single side's style
                 # borderRadius=None
                 ):
        """
        Initializes the BorderSide.

        Args:
            width (float): The width of the border line in pixels. Defaults to 1.0.
                           Use 0 for no border width.
            style (str): The border style (e.g., BorderStyle.SOLID, BorderStyle.DASHED).
                         Defaults to BorderStyle.SOLID. Use BorderStyle.NONE for no visible border.
            color (str): The color of the border line (CSS color string). Defaults to Colors.black.
        """
        self.width = max(0.0, width) # Ensure non-negative
        # Add validation for style if desired
        self.style = style if style else BorderStyle.NONE # Default to NONE if None/empty provided
        self.color = color if color else Colors.black # Default color if None/empty

    # --- Compatibility Methods ---

    def to_css_shorthand_value(self) -> str:
        """
        Returns the CSS shorthand value string for the 'border' property
        (e.g., '1px solid black'). Returns 'none' if style is NONE or width is 0.
        """
        if self.style == BorderStyle.NONE or self.width <= 0:
            return 'none'
        # Format: width style color
        return f"{self.width}px {self.style} {self.color}"

    def to_css_dict(self) -> Dict[str, str]:
        """
        Returns border properties as a dictionary of individual CSS properties.
        Useful if applying to specific sides (e.g., border-top-width).
        """
        styles = {}
        if self.style == BorderStyle.NONE or self.width <= 0:
             # Set style to none, implicitly hiding width/color
             styles['border-style'] = BorderStyle.NONE
             styles['border-width'] = '0px' # Explicitly set width to 0
        else:
            styles['border-width'] = f"{self.width}px"
            styles['border-style'] = self.style
            styles['border-color'] = self.color
        return styles

    def to_css(self) -> str:
        """
        DEPRECATED? Returns individual CSS properties as a string snippet.
        Using the shorthand value or dictionary is generally better.
        """
        style_dict = self.to_css_dict()
        return " ".join(f"{prop}: {value};" for prop, value in style_dict.items())

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, BorderSide):
            return NotImplemented
        # Treat width=0 or style=NONE as equivalent to no border for comparison? Optional.
        # Simple comparison for now:
        return (self.width == other.width and
                self.style == other.style and
                self.color == other.color)

    def __hash__(self):
        # Hash based on the defining attributes
        return hash((self.width, self.style, self.color))

    # --- Representation ---
    def __repr__(self):
        # Show defaults only if non-standard
        props = []
        if self.width != 1.0: props.append(f"width={self.width}")
        if self.style != BorderStyle.SOLID: props.append(f"style='{self.style}'")
        if self.color != Colors.black: props.append(f"color='{self.color}'")
        if not props: return "BorderSide()" # All defaults
        return f"BorderSide({', '.join(props)})"

    # --- Reconciler Prop Representation ---
    def to_dict(self):
         """Returns a simple dictionary representation."""
         return {'width': self.width, 'style': self.style, 'color': self.color}

    def to_tuple(self):
         """Returns a hashable tuple representation."""
         return (self.width, self.style, self.color)

    # Removed to_int() - unclear purpose, width is directly accessible.
    # Removed borderRadius - Belongs on BoxDecoration/BorderRadius.
    # Removed border_to_css() - Replaced by to_css_shorthand_value().

class Border:
    """
    A border of a box, comprised of four sides: top, right, bottom, left.
    """
    def __init__(self, top: BorderSide = None, right: BorderSide = None, bottom: BorderSide = None, left: BorderSide = None):
        """
        Creates a border with the given sides.
        If a side is None, it defaults to a border with no style (no width).
        """
        self.top = top if top else BorderSide(width=0, style=BorderStyle.NONE)
        self.right = right if right else BorderSide(width=0, style=BorderStyle.NONE)
        self.bottom = bottom if bottom else BorderSide(width=0, style=BorderStyle.NONE)
        self.left = left if left else BorderSide(width=0, style=BorderStyle.NONE)

    @classmethod
    def all(cls, color=Colors.black, width=1.0, style=BorderStyle.SOLID):
        """Creates a uniform border with the same style on all sides."""
        side = BorderSide(color=color, width=width, style=style)
        return cls(top=side, right=side, bottom=side, left=side)

    @classmethod
    def symmetric(cls, vertical: BorderSide = None, horizontal: BorderSide = None):
        """Creates a border with symmetrical vertical and horizontal sides."""
        return cls(
            top=vertical, 
            right=horizontal, 
            bottom=vertical, 
            left=horizontal
        )
    
    @classmethod
    def fromBorderSide(cls, side: BorderSide):
        """Creates a border with the same side on all four edges."""
        return cls(top=side, right=side, bottom=side, left=side)

    def to_css_dict(self) -> Dict[str, str]:
        """Returns the CSS properties for the individual border sides."""
        styles = {}
        # Optimization: check if all sides are identical
        if self.top == self.right == self.bottom == self.left:
             # Use shorthand 'border' property
             shorthand = self.top.to_css_shorthand_value()
             if shorthand != 'none':
                 styles['border'] = shorthand
             return styles

        # Otherwise, apply individual sides
        # Helper to apply side rules
        def apply_side(side, prefix):
            side_dict = side.to_css_dict()
            for k, v in side_dict.items():
                # k is like 'border-width', 'border-color'
                # we need 'border-top-width', etc.
                suffix = k.split('-')[1] # width, style, color
                styles[f"{prefix}-{suffix}"] = v

        apply_side(self.top, 'border-top')
        apply_side(self.right, 'border-right')
        apply_side(self.bottom, 'border-bottom')
        apply_side(self.left, 'border-left')
        
        return styles

    def __eq__(self, other):
        if not isinstance(other, Border):
            return NotImplemented
        return (self.top == other.top and 
                self.right == other.right and 
                self.bottom == other.bottom and 
                self.left == other.left)

    def __hash__(self):
        return hash((self.top, self.right, self.bottom, self.left))

    def __repr__(self):
        return f"Border(top={self.top}, right={self.right}, bottom={self.bottom}, left={self.left})"

    def to_dict(self):
         return {
             'top': self.top.to_dict(),
             'right': self.right.to_dict(),
             'bottom': self.bottom.to_dict(),
             'left': self.left.to_dict()
         }

    def to_tuple(self):
         return (self.top.to_tuple(), self.right.to_tuple(), self.bottom.to_tuple(), self.left.to_tuple())

from typing import Optional, Union, Tuple, Dict, Any

# Assuming other style classes are defined/imported and compatible:
# from .styles import Colors, EdgeInsets, BorderSide, BorderRadius, TextStyle, Alignment, BoxShadow, Offset

class ButtonStyle:
    """
    Defines the visual properties of buttons (TextButton, ElevatedButton, etc.).
    Compatible with reconciliation. Aggregates other style objects.

    Args:
            backgroundColor: Background color.
            foregroundColor: Text and icon color.
            disabledBackgroundColor: Background when disabled.
            disabledForegroundColor: Text/icon color when disabled.
            shadowColor: Color used for the elevation shadow.
            elevation: Elevation level (used for box-shadow).
            padding: Internal padding.
            minimumSize: Minimum width/height tuple (pixels).
            maximumSize: Maximum width/height tuple (pixels).
            side: Border definition (BorderSide object).
            shape: Corner radius (number for all corners or BorderRadius object).
            textStyle: TextStyle object for button label.
            alignment: Alignment object if button uses flex/grid for content.
    """
    def __init__(self,
                 # --- Colors ---
                 backgroundColor: Optional[str] = None, # Button background
                 foregroundColor: Optional[str] = None, # Text/Icon color
                 disabledBackgroundColor: Optional[str] = None, # Background when disabled
                 disabledForegroundColor: Optional[str] = None, # Text/Icon when disabled
                 shadowColor: Optional[str] = None, # Color of elevation shadow
                 hoverColor: Optional[str] = None,
                 activeColor: Optional[str] = None,
                 # overlayColor: Optional[str] = None, # TODO: Handle hover/focus/pressed overlay (CSS :hover/:active or JS)
                 # --- Shape & Border ---
                 elevation: Optional[float] = None, # Shadow depth (used to generate BoxShadow)
                 padding: Optional[EdgeInsets] = None, # Padding inside the button
                 margin: Optional[EdgeInsets] = None, # margin outside the button
                 minimumSize: Optional[Tuple[Optional[float], Optional[float]]] = None, # (minWidth, minHeight) in px
                 maximumSize: Optional[Tuple[Optional[float], Optional[float]]] = None, # (maxWidth, maxHeight) in px
                 side: Optional[BorderSide] = None, # Border properties
                 shape: Optional[Union[float, BorderRadius]] = None, # Corner radius (number or BorderRadius object)
                 # --- Content Style ---
                 textStyle: Optional[TextStyle] = None, # Style for text content
                 alignment: Optional[Alignment] = None, # How content (icon+label) is aligned if button is flex container
                 # iconColor: Optional[str] = None, # Specific icon color override? (or use foregroundColor)
                 # iconSize: Optional[float] = None, # Icon size? (Usually handled by Icon widget itself)
                 ):
        """
        Initializes the ButtonStyle.

        Args:
            backgroundColor: Background color.
            foregroundColor: Text and icon color.
            disabledBackgroundColor: Background when disabled.
            disabledForegroundColor: Text/icon color when disabled.
            shadowColor: Color used for the elevation shadow.
            elevation: Elevation level (used for box-shadow).
            padding: Internal padding.
            minimumSize: Minimum width/height tuple (pixels).
            maximumSize: Maximum width/height tuple (pixels).
            side: Border definition (BorderSide object).
            shape: Corner radius (number for all corners or BorderRadius object).
            textStyle: TextStyle object for button label.
            alignment: Alignment object if button uses flex/grid for content.
        """
        self.backgroundColor = backgroundColor
        self.foregroundColor = foregroundColor
        self.disabledBackgroundColor = disabledBackgroundColor
        self.disabledForegroundColor = disabledForegroundColor
        self.shadowColor = shadowColor
        self.hoverColor = hoverColor
        self.activeColor = activeColor
        self.elevation = elevation
        self.padding = padding
        self.margin = margin
        self.minimumSize = minimumSize
        self.maximumSize = maximumSize
        self.side = side
        self.shape = shape
        self.textStyle = textStyle
        self.alignment = alignment
        # Removed icon - Icon should be passed as child widget

    # --- Compatibility Methods ---

    def to_css_dict(self) -> Dict[str, str]:
        """Converts button style properties to a dictionary of CSS styles."""
        styles = {}
        if self.backgroundColor: styles['background-color'] = self.backgroundColor
        if self.foregroundColor: styles['color'] = self.foregroundColor # Applies to text/icon color usually
        if self.hoverColor: styles['hover-color'] = self.hoverColor
        if self.activeColor: styles['active-color'] = self.activeColor
        # Disabled colors handled by specific .disabled class rules, not here directly

        # --- Shadow ---
        # Generate box-shadow based on elevation
        if self.elevation is not None and self.elevation > 0:
            # Basic elevation mapping (improve as needed)
            offset_y = min(max(1, self.elevation * 0.8), 6)
            blur = max(4, self.elevation * 1.5)
            spread = max(0, self.elevation * 0.2 - 1)
            color = self.shadowColor or Colors.rgba(0,0,0,0.2)
            styles['box-shadow'] = f"0px {offset_y}px {blur}px {spread}px {color}"

        if self.padding and isinstance(self.padding, EdgeInsets): styles['padding'] = self.padding.to_css() # Use EdgeInsets method
        if self.margin and isinstance(self.margin, EdgeInsets): styles['margin'] = self.margin.to_css() # Use EdgeInsets method
        if self.minimumSize:
            min_w, min_h = self.minimumSize
            if min_w is not None: styles['min-width'] = f"{min_w}px"
            if min_h is not None: styles['min-height'] = f"{min_h}px"
        if self.maximumSize:
            max_w, max_h = self.maximumSize
            if max_w is not None: styles['max-width'] = f"{max_w}px"
            if max_h is not None: styles['max-height'] = f"{max_h}px"

        # --- Border & Shape ---
        if self.side and isinstance(self.side, BorderSide):
            # Use shorthand if available and not NONE
            shorthand = self.side.to_css_shorthand_value()
            if shorthand != 'none':
                 styles['border'] = shorthand
            else:
                 styles['border'] = 'none' # Explicitly set to none
        else:
            # Default: buttons often have no border unless specified
            styles['border'] = 'none'

        if self.shape:
            print("Shape value in btnStyle: ", self.shape.to_css_value())
            if isinstance(self.shape, BorderRadius):
                styles['border-radius'] = self.shape.to_css_value()
            elif isinstance(self.shape, (int, float)):
                 styles['border-radius'] = f"{max(0.0, self.shape)}px"

        # --- Text Style ---
        # Note: Text styles apply to text *within* the button.
        # Best applied via CSS descendant selector (e.g., .button-class > .text-class)
        # or if the button directly renders text. Including here might override wrongly.
        # if self.textStyle and isinstance(self.textStyle, TextStyle):
        #     styles.update(self.textStyle.to_css_dict()) # Merge text styles

        # --- Alignment ---
        # Applies if the button itself uses flex/grid to lay out an icon and label
        if self.alignment and isinstance(self.alignment, Alignment):
             # Usually buttons use flex to align icon+label
             styles['display'] = 'inline-flex' # Use inline-flex for button
             styles['justify-content'] = self.alignment.justify_content
             styles['align-items'] = self.alignment.align_items
             styles['gap'] = '8px' # Default gap between icon/label?

        return styles

    def to_css(self) -> str:
        """Converts button style properties to a CSS string snippet."""
        style_dict = self.to_css_dict()
        return " ".join(f"{prop}: {value};" for prop, value in style_dict.items())

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, ButtonStyle):
            return NotImplemented
        # Compare all relevant attributes
        # Ensure nested objects are comparable (__eq__ implemented)
        return (self.backgroundColor == other.backgroundColor and
                self.foregroundColor == other.foregroundColor and
                self.disabledBackgroundColor == other.disabledBackgroundColor and
                self.disabledForegroundColor == other.disabledForegroundColor and
                self.shadowColor == other.shadowColor and
                self.hoverColor == other.hoverColor and
                self.activeColor == other.activeColor and
                self.elevation == other.elevation and
                self.padding == other.padding and
                self.margin == other.margin and
                self.minimumSize == other.minimumSize and
                self.maximumSize == other.maximumSize and
                self.side == other.side and
                self.shape == other.shape and
                self.textStyle == other.textStyle and
                self.alignment == other.alignment)

    def __hash__(self):
        # Hash a tuple of hashable representations of attributes
        # Ensure nested objects (EdgeInsets, BorderSide, BorderRadius, TextStyle, Alignment) are hashable
        return hash((
            self.backgroundColor, self.foregroundColor,
            self.disabledBackgroundColor, self.disabledForegroundColor,
            self.shadowColor, self.hoverColor, self.activeColor, self.elevation, self.padding, self.margin,
            self.minimumSize, self.maximumSize, # Tuples are hashable
            self.side, self.shape, self.textStyle, self.alignment
        ))

    # --- Representation ---
    def __repr__(self):
        props = []
        # Add checks to show only non-default/non-None values
        attrs = ['backgroundColor', 'foregroundColor', 'disabledBackgroundColor', 'disabledForegroundColor',
                 'shadowColor', 'hoverColor', 'activeColor', 'elevation', 'padding', 'margin','minimumSize', 'maximumSize',
                 'side', 'shape', 'textStyle', 'alignment']
        for attr in attrs:
            value = getattr(self, attr)
            if value is not None: # Simple check for None
                # Add more sophisticated default checks if needed
                 props.append(f"{attr}={value!r}")
        return f"ButtonStyle({', '.join(props)})"

    # --- Reconciler Prop Representation ---
    def to_dict(self):
        """Returns a simple dictionary representation."""
        # Convert nested objects to dicts too
        return {attr: getattr(self, attr).to_dict() if hasattr(getattr(self, attr), 'to_dict') else getattr(self, attr)
                for attr in [
                    'backgroundColor', 'foregroundColor', 'disabledBackgroundColor', 'disabledForegroundColor',
                    'shadowColor', 'hoverColor', 'activeColor', 'elevation', 'padding', 'margin', 'minimumSize', 'maximumSize',
                    'side', 'shape', 'textStyle', 'alignment'
                ] if getattr(self, attr) is not None}

    def to_tuple(self):
         """Returns a hashable tuple representation."""
         # Convert nested objects to tuples too
         return tuple(getattr(self, attr).to_tuple() if hasattr(getattr(self, attr), 'to_tuple') else getattr(self, attr)
                      for attr in [
                          'backgroundColor', 'foregroundColor', 'disabledBackgroundColor', 'disabledForegroundColor',
                          'shadowColor', 'hoverColor', 'activeColor', 'elevation', 'padding', 'margin', 'minimumSize', 'maximumSize',
                          'side', 'shape', 'textStyle', 'alignment'
                      ])

class ScrollPhysics:
    """
    Specifies the scrolling behavior of a widget.

    Attributes:
        BOUNCING: Allows scrolling beyond content bounds with a spring-like effect.
        CLAMPING: Prevents scrolling beyond content bounds.
        ALWAYS_SCROLLABLE: Enables scrolling even if content does not overflow.
        NEVER_SCROLLABLE: Disables scrolling regardless of content size.
    """
    BOUNCING = 'bouncing'
    CLAMPING = 'clamping'
    ALWAYS_SCROLLABLE = 'alwaysScrollable'
    NEVER_SCROLLABLE = 'neverScrollable'
    
class Overflow:
    """
    Defines how content overflow is handled in a widget.

    Attributes:
        VISIBLE: Content is visible beyond the bounds of the widget.
        HIDDEN: Content is clipped to the bounds of the widget.
        SCROLL: Adds scrolling to manage content overflow.
        AUTO: Automatically decides based on the content size.
    """
    VISIBLE = 'visible'
    HIDDEN = 'hidden'
    SCROLL = 'scroll'
    AUTO = 'auto'    

class StackFit:
    """
    Determines how children are sized within a Stack widget.

    Attributes:
        loose: Children take up as little space as possible.
        expand: Children expand to fill the Stack's available space.
        passthrough: Children retain their original size.
    """
    loose = 'loose'
    expand = 'expand'
    passthrough = 'passthrough'

class TextDirection:
    """
    Specifies the direction in which text flows.

    Attributes:
        LTR: Text flows from left to right.
        RTL: Text flows from right to left.
    """
    LTR = 'ltr'
    RTL = 'rtl'

class TextBaseline():
    """
    Specifies the alignment of text baselines.

    Attributes:
        alphabetic: Aligns the baseline to the bottom of alphabetic characters.
        ideographic: Aligns the baseline to the middle of ideographic characters.
    """
    alphabetic = 'text-bottom'
    ideographic = 'middle'

class VerticalDirection:
    """
    Determines the vertical arrangement of children.

    Attributes:
        DOWN: Children are arranged from top to bottom.
        UP: Children are arranged from bottom to top.
    """
    DOWN = 'down'
    UP = 'up'


class BoxFit:
    """
    Defines how an image or box is fitted into its allocated space.

    Attributes:
        CONTAIN: Scales to fit within the bounds while maintaining aspect ratio.
        COVER: Scales to fill the bounds while maintaining aspect ratio, possibly cropping.
        FILL: Stretches to fill the bounds, disregarding aspect ratio.
        NONE: Does not scale; the content's original size is used.
    """
    CONTAIN = 'contain'
    COVER = 'cover'
    FILL = 'fill'
    NONE = 'none'
    
# --- BoxDecoration Refactored ---
class BoxDecoration:
    """
    Describes how to paint a box (background, border, shadow, shape).
    Compatible with reconciliation.
    """
    def __init__(self,
                 color: Optional[str] = None,
                 # image: Optional[DecorationImage] = None, # TODO: If image backgrounds needed
                 border: Optional[Union[str, BorderSide]] = None, # Allow BorderSide object or CSS string? Prefer object.
                 borderRadius: Optional[Union[int, float, BorderRadius]] = None, # Allow number or BorderRadius obj
                 boxShadow: Optional[Union[BoxShadow, List[BoxShadow]]] = None, # Allow single or list
                 # gradient: Optional[Gradient] = None, # TODO: If gradients needed
                 # shape: BoxShape = BoxShape.rectangle, # TODO: If specific shapes like circle needed
                 # For simplicity, sticking to properties easily mappable to CSS:
                 transform: Optional[str] = None, # Raw CSS transform string
                 # Padding is usually handled by Padding widget, not BoxDecoration
                 # padding: Optional[EdgeInsets] = None,
                 visible: bool = True,
                 ):
        """
        Initializes the BoxDecoration.

        Args:
            color: Background color.
            border: Border definition (BorderSide object preferred).
            borderRadius: Corner radius (number for all corners or BorderRadius object).
            boxShadow: BoxShadow object or list of BoxShadow objects.
            transform: CSS transform string (e.g., 'rotate(45deg)').
        """
        self.color = color
        self.border = border
        self.borderRadius = borderRadius
        self.visible = visible
        # Ensure boxShadow is always a list for consistent handling
        if isinstance(boxShadow, BoxShadow):
            self.boxShadow = [boxShadow]
        elif isinstance(boxShadow, list):
            self.boxShadow = boxShadow
        else:
            self.boxShadow = None
        self.transform = transform
        # self.padding = padding # Removed padding, use Padding widget

    # --- Compatibility Methods ---

    def to_css_dict(self) -> Dict[str, str]:
        """Converts decoration properties to a dictionary of CSS styles."""
        styles = {}
        if self.color:
            styles['background'] = self.color
        if self.border:
            if isinstance(self.border, BorderSide):
                 # Assumes BorderSide has a way to generate full border property
                 if hasattr(self.border, 'border_to_css_shorthand'):
                      styles['border'] = self.border.border_to_css_shorthand() # Example method name
                 else: # Fallback using individual properties if needed
                      border_dict = self.border.to_css_dict() # Assume BorderSide returns dict
                      styles.update(border_dict)
            elif isinstance(self.border, str): # Allow raw CSS string (less safe)
                 styles['border'] = self.border
        if self.borderRadius:
            if isinstance(self.borderRadius, BorderRadius):
                # Assumes BorderRadius has a way to generate border-radius property
                 styles['border-radius'] = self.borderRadius.to_css_value() # Example method name
            elif isinstance(self.borderRadius, (int, float)):
                 styles['border-radius'] = f"{self.borderRadius}px"
            # Else handle string? For now, require object or number
        if self.boxShadow:
            # Combine multiple shadows with comma
            shadow_strings = [shadow.to_css() for shadow in self.boxShadow if isinstance(shadow, BoxShadow)]
            if shadow_strings:
                 styles['box-shadow'] = ", ".join(shadow_strings)
        if self.transform:
            styles['transform'] = self.transform
        # if self.padding and isinstance(self.padding, EdgeInsets): # Padding removed
        #     styles['padding'] = self.padding.to_css()
        return styles

    def to_css(self) -> str:
        """Converts decoration properties to a CSS string snippet."""
        style_dict = self.to_css_dict()
        return " ".join(f"{prop}: {value};" for prop, value in style_dict.items())

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, BoxDecoration):
            return NotImplemented
        # Compare all relevant attributes
        # Note: Comparing lists requires order to be the same for equality
        return (self.color == other.color and
                self.border == other.border and
                self.borderRadius == other.borderRadius and
                self.boxShadow == other.boxShadow and # Relies on BoxShadow __eq__ and list order
                self.transform == other.transform)

    def __hash__(self):
        # Hash a tuple of hashable representations of attributes
        # Ensure nested objects (BorderSide, BorderRadius, BoxShadow) are hashable
        # Convert list of shadows to tuple for hashing
        shadow_tuple = tuple(self.boxShadow) if self.boxShadow else None
        return hash((
            self.color,
            self.border, # Relies on BorderSide/str hash
            self.borderRadius, # Relies on BorderRadius/number hash
            shadow_tuple, # Relies on BoxShadow hash
            self.transform
        ))

    # --- Representation ---
    def __repr__(self):
        props = []
        if self.color: props.append(f"color='{self.color}'")
        if self.border: props.append(f"border={self.border!r}")
        if self.borderRadius: props.append(f"borderRadius={self.borderRadius!r}")
        if self.boxShadow: props.append(f"boxShadow={self.boxShadow!r}")
        if self.transform: props.append(f"transform='{self.transform}'")
        return f"BoxDecoration({', '.join(props)})"

    # --- Reconciler Prop Representation ---
    def to_dict(self):
         # Convert nested objects to dicts too if needed for serialization
         border_repr = self.border.to_dict() if hasattr(self.border, 'to_dict') else self.border
         radius_repr = self.borderRadius.to_dict() if hasattr(self.borderRadius, 'to_dict') else self.borderRadius
         shadow_repr = [s.to_dict() for s in self.boxShadow if hasattr(s, 'to_dict')] if self.boxShadow else None

         return {'color': self.color, 'border': border_repr,
                 'borderRadius': radius_repr, 'boxShadow': shadow_repr,
                 'transform': self.transform}

    def to_tuple(self):
         """Returns a hashable tuple representation."""
         shadow_tuple = tuple(self.boxShadow) if self.boxShadow else None
         return (self.color, self.border, self.borderRadius, shadow_tuple, self.transform)

# --- BoxDecoration Refactored ---
class BoxDecoration:
    """
    Describes how to paint a box (background, border, shadow, shape).
    Compatible with reconciliation.
    """
    def __init__(self,
                 color: Optional[str] = None,
                 # image: Optional[DecorationImage] = None, # TODO: If image backgrounds needed
                 border: Optional[Union[str, BorderSide, Border]] = None, # Allow BorderSide, Border object or CSS string.
                 borderRadius: Optional[Union[int, float, BorderRadius]] = None, # Allow number or BorderRadius obj
                 boxShadow: Optional[Union[BoxShadow, List[BoxShadow]]] = None, # Allow single or list
                 # gradient: Optional[Gradient] = None, # TODO: If gradients needed
                 # shape: BoxShape = BoxShape.rectangle, # TODO: If specific shapes like circle needed
                 # For simplicity, sticking to properties easily mappable to CSS:
                 transform: Optional[str] = None, # Raw CSS transform string
                 # Padding is usually handled by Padding widget, not BoxDecoration
                 # padding: Optional[EdgeInsets] = None,
                 ):
        """
        Initializes the BoxDecoration.

        Args:
            color: Background color.
            border: Border definition (BorderSide or Border object preferred).
            borderRadius: Corner radius (number for all corners or BorderRadius object).
            boxShadow: BoxShadow object or list of BoxShadow objects.
            transform: CSS transform string (e.g., 'rotate(45deg)').
        """
        self.color = color
        self.border = border
        self.borderRadius = borderRadius
        # Ensure boxShadow is always a list for consistent handling
        if isinstance(boxShadow, BoxShadow):
            self.boxShadow = [boxShadow]
        elif isinstance(boxShadow, list):
            self.boxShadow = boxShadow
        else:
            self.boxShadow = None
        self.transform = transform
        # self.padding = padding # Removed padding, use Padding widget

    # --- Compatibility Methods ---

    def to_css_dict(self) -> Dict[str, str]:
        """Converts decoration properties to a dictionary of CSS styles."""
        styles = {}
        if self.color:
            styles['background'] = self.color
        if self.border:
            if isinstance(self.border, Border):
                 styles.update(self.border.to_css_dict())
            elif isinstance(self.border, BorderSide):
                 # Assumes BorderSide has a way to generate full border property
                 if hasattr(self.border, 'to_css_shorthand_value'):
                      styles['border'] = self.border.to_css_shorthand_value()
                 else: # Fallback using individual properties if needed
                      border_dict = self.border.to_css_dict() # Assume BorderSide returns dict
                      styles.update(border_dict)
            elif isinstance(self.border, str): # Allow raw CSS string (less safe)
                 styles['border'] = self.border
        if self.borderRadius:
            if isinstance(self.borderRadius, BorderRadius):
                # Assumes BorderRadius has a way to generate border-radius property
                 styles['border-radius'] = self.borderRadius.to_css_value() # Example method name
            elif isinstance(self.borderRadius, (int, float)):
                 styles['border-radius'] = f"{self.borderRadius}px"
            # Else handle string? For now, require object or number
        if self.boxShadow:
            # Combine multiple shadows with comma
            shadow_strings = [shadow.to_css() for shadow in self.boxShadow if isinstance(shadow, BoxShadow)]
            if shadow_strings:
                 styles['box-shadow'] = ", ".join(shadow_strings)
        if self.transform:
            styles['transform'] = self.transform
        # if self.padding and isinstance(self.padding, EdgeInsets): # Padding removed
        #     styles['padding'] = self.padding.to_css()
        return styles

    def to_css(self) -> str:
        """Converts decoration properties to a CSS string snippet."""
        style_dict = self.to_css_dict()
        return " ".join(f"{prop}: {value};" for prop, value in style_dict.items())

    # --- Hashability & Equality ---
    def __eq__(self, other):
        if not isinstance(other, BoxDecoration):
            return NotImplemented
        # Compare all relevant attributes
        # Note: Comparing lists requires order to be the same for equality
        return (self.color == other.color and
                self.border == other.border and
                self.borderRadius == other.borderRadius and
                self.boxShadow == other.boxShadow and # Relies on BoxShadow __eq__ and list order
                self.transform == other.transform)

    def __hash__(self):
        # Hash a tuple of hashable representations of attributes
        # Ensure nested objects (BorderSide, BorderRadius, BoxShadow) are hashable
        # Convert list of shadows to tuple for hashing
        shadow_tuple = tuple(self.boxShadow) if self.boxShadow else None
        return hash((
            self.color,
            self.border, # Relies on BorderSide/str hash
            self.borderRadius, # Relies on BorderRadius/number hash
            shadow_tuple, # Relies on BoxShadow hash
            self.transform
        ))

    # --- Representation ---
    def __repr__(self):
        props = []
        if self.color: props.append(f"color='{self.color}'")
        if self.border: props.append(f"border={self.border!r}")
        if self.borderRadius: props.append(f"borderRadius={self.borderRadius!r}")
        if self.boxShadow: props.append(f"boxShadow={self.boxShadow!r}")
        if self.transform: props.append(f"transform='{self.transform}'")
        return f"BoxDecoration({', '.join(props)})"

    # --- Reconciler Prop Representation ---
    def to_dict(self):
         # Convert nested objects to dicts too if needed for serialization
         border_repr = self.border.to_dict() if hasattr(self.border, 'to_dict') else self.border
         radius_repr = self.borderRadius.to_dict() if hasattr(self.borderRadius, 'to_dict') else self.borderRadius
         shadow_repr = [s.to_dict() for s in self.boxShadow if hasattr(s, 'to_dict')] if self.boxShadow else None

         return {'color': self.color, 'border': border_repr,
                 'borderRadius': radius_repr, 'boxShadow': shadow_repr,
                 'transform': self.transform}

    def to_tuple(self):
         """Returns a hashable tuple representation."""
         shadow_tuple = tuple(self.boxShadow) if self.boxShadow else None
         return (self.color, self.border, self.borderRadius, shadow_tuple, self.transform)





# class InputDecoration:
#     """
#     Defines the visual decoration for a TextField.

#     This class encapsulates properties like labels, icons, hints, error text,
#     and border styles, allowing for consistent and reusable text field styling
#     that mimics Material Design's filled or outlined text fields.
#     """
#     def __init__(self,
#                  label: Optional[str] = None,
#                  hintText: Optional[str] = None,
#                  errorText: Optional[str] = None,
#                  # You can add prefixIcon and suffixIcon as Widget later
                 
#                  # --- Colors ---
#                  fillColor: Optional[str] = None, # Background of the input
#                  focusColor: Optional[str] = None, # Color of the border/label when focused
                 
#                  # --- Borders ---
#                  # For simplicity, we can use a single border style and change its color based on state
#                  border: Optional[BorderSide] = None,
#                  focusedBorder: Optional[BorderSide] = None,
#                  errorBorder: Optional[BorderSide] = None,
                 
#                  # --- Flags ---
#                  filled: bool = True, # Determines if fillColor is used
#                  ):
#         self.label = label
#         self.hintText = hintText
#         self.errorText = errorText
        
#         self.fillColor = fillColor
#         self.focusColor = focusColor
        
#         self.border = border
#         self.focusedBorder = focusedBorder
#         self.errorBorder = errorBorder
        
#         self.filled = filled

#     def to_tuple(self) -> Tuple:
#         """
#         Creates a hashable tuple representation for use in style keys.
#         This is crucial for the shared styling system.
#         """
#         # make_hashable will handle converting BorderSide to a tuple
#         return (
#             self.label, self.hintText, self.errorText, self.fillColor,
#             self.focusColor, make_hashable(self.border),
#             make_hashable(self.focusedBorder), make_hashable(self.errorBorder),
#             self.filled
#         )

#     def __eq__(self, other):
#         if not isinstance(other, InputDecoration):
#             return NotImplemented
#         return self.to_tuple() == other.to_tuple()

#     def __hash__(self):
#         return hash(self.to_tuple())



# in pythra/styles.py

# ... (other imports) ...
# Make sure BorderSide is defined before this class or imported
# from .styles import BorderSide, Colors

class InputDecoration:
    """
    Defines the visual decoration for a TextField.

    This class encapsulates properties like labels, icons, hints, error text,
    and border styles, allowing for consistent and reusable text field styling
    that mimics Material Design's filled or outlined text fields.
    """
    def __init__(self,
                 label: Optional[str] = None,
                 hintText: Optional[str] = None,
                 errorText: Optional[str] = None,
                 
                 # --- Colors ---
                 fillColor: Optional[str] = None,
                 focusColor: Optional[str] = None,
                 labelColor: Optional[str] = None, # NEW: Color for the label
                 errorColor: Optional[str] = None, # NEW: Color for border/label/text in error state
                 
                 # --- Borders ---
                 borderRadius: Optional[BorderRadius] = None,
                 border: Optional[BorderSide] = None,
                 focusedBorder: Optional[BorderSide] = None,
                 errorBorder: Optional[BorderSide] = None,
                 
                 # --- Flags ---
                 filled: bool = True
                 ):
        
        # --- Store user-provided values ---
        self.label = label
        self.hintText = hintText
        self.errorText = errorText
        
        self.filled = filled

        # --- Set smart, M3-style defaults if values are not provided ---
        self.fillColor = fillColor if fillColor is not None else (fillColor if self.filled else 'transparent')
        # print("FILL FROM STYLE.PY: ", self.fillColor, self.label)
        self.focusColor = focusColor if focusColor is not None else Colors.primary
        self.labelColor = labelColor if labelColor is not None else Colors.onSurfaceVariant
        self.errorColor = errorColor if errorColor is not None else Colors.error

        self.borderRadius = borderRadius if borderRadius is not None else BorderRadius.all(4)

        self.border = border if border is not None else BorderSide(
            width=1.0, 
            style=BorderStyle.SOLID, 
            color=Colors.outline
        )
        self.focusedBorder = focusedBorder if focusedBorder is not None else BorderSide(
            width=2.0, 
            style=BorderStyle.SOLID, 
            color=self.focusColor # Use the focus color for the focused border
        )
        self.errorBorder = errorBorder if errorBorder is not None else BorderSide(
            width=2.0, 
            style=BorderStyle.SOLID, 
            color=self.errorColor # Use the error color for the error border
        )

    def to_tuple(self) -> Tuple:
        """Creates a hashable tuple representation for use in style keys."""
        # Note: We now hash the final, resolved values, not the initial ones.
        return (
            self.label, self.hintText, self.errorText, self.fillColor,
            self.focusColor, self.labelColor, self.errorColor,
            self.borderRadius.to_css(),
            make_hashable(self.border),
            make_hashable(self.focusedBorder),
            make_hashable(self.errorBorder),
            self.filled
        )

    def __eq__(self, other):
        if not isinstance(other, InputDecoration):
            return NotImplemented
        return self.to_tuple() == other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())


# In pythra/styles.py



# ... (keep all your other style classes)

@dataclass
class ScrollbarTheme:
    """
    Holds the styling information for a custom scrollbar.
    Maps directly to CSS scrollbar pseudo-element properties.
    """
    width: int = 12  # The width of the vertical scrollbar in pixels.
    height: int = 12 # The height of the horizontal scrollbar in pixels.
    
    thumbColor: Optional[str] = "#888" # Color of the draggable thumb.
    thumbHoverColor: Optional[str] = "#555" # Color of the thumb on hover.
    
    trackColor: Optional[str] = "transparent" # Color of the track (the groove).
    
    # The radius of the corners on the thumb.
    radius: int = 6 
    trackRadius: int = 8 
    
    # Creates a "padding" effect around the thumb by using a transparent border.
    thumbPadding: int = 0 
    trackMargin: Optional[EdgeInsets] = 0 

    def to_tuple(self) -> Tuple:
        """Returns a hashable tuple representation for use as a style key."""
        return (
            self.width, self.height, self.thumbColor, self.thumbHoverColor,
            self.trackColor, self.radius, self.trackRadius, self.thumbPadding, self.trackMargin
        )

# In pythra/styles.py

# ... (keep all your other style classes like EdgeInsets, Colors, etc.)

@dataclass
class SliderTheme:
    """
    Defines the visual properties of a Slider widget.

    This data class holds customizable properties for colors and dimensions,
    allowing for consistent theming of sliders across an application.
    """
    # Colors
    activeTrackColor: Optional[str] = None
    inactiveTrackColor: Optional[str] = None
    thumbColor: Optional[str] = None
    overlayColor: Optional[str] = None # Color of the halo effect when dragging

    # Dimensions
    trackHeight: float = 4.0
    thumbSize: float = 14.0
    thumbBorderWidth: float = 2.0
    thumbBorderColor: Optional[str] = None
    overlaySize: float = 8.0 # The 'spread' of the overlay halo in pixels


    def to_tuple(self) -> Tuple:
        """Creates a hashable tuple for use in style keys."""
        print("thumbBorderColor: ", self.thumbBorderColor)
        return (
            self.activeTrackColor, self.inactiveTrackColor, self.thumbColor,
            self.overlayColor, self.trackHeight, self.thumbSize,
            self.thumbBorderWidth, self.thumbBorderColor, self.overlaySize
        )

# In pythra/styles.py

# ... (keep all your other style classes like EdgeInsets, SliderTheme, etc.)

@dataclass
class CheckboxTheme:
    """
    Defines the visual properties for a Checkbox widget.
    """
    # Colors
    activeColor: Optional[str] = None      # The background color of the box when checked.
    checkColor: Optional[str] = None       # The color of the checkmark icon.
    inactiveColor: Optional[str] = None    # The color of the border when unchecked.
    splashColor: Optional[str] = None      # The color of the ripple/splash effect on press.

    # Dimensions
    size: float = 18.0                     # The width and height of the checkbox square.
    strokeWidth: float = 2.0               # The thickness of the border and checkmark.
    splashRadius: float = 20.0             # The radius of the splash effect.

    def to_tuple(self) -> Tuple:
        """Creates a hashable tuple for use in style keys."""
        return (
            self.activeColor, self.checkColor, self.inactiveColor,
            self.splashColor, self.size, self.strokeWidth, self.splashRadius
        )


# In pythra/styles.py

# ... (keep all your other style classes)

@dataclass
class SwitchTheme:
    """
    Defines the visual properties for a Switch widget.
    """
    # Color of the sliding circle (thumb).
    thumbColor: Optional[str] = None
    # Color of the track when the switch is ON.
    activeTrackColor: Optional[str] = None
    # Color of the track when the switch is OFF.
    inactiveTrackColor: Optional[str] = None
    # Optional color for the thumb when the switch is ON.
    activeThumbColor: Optional[str] = None

    def to_tuple(self) -> Tuple:
        """Creates a hashable tuple for use in style keys."""
        return (
            self.thumbColor,
            self.activeTrackColor,
            self.inactiveTrackColor,
            self.activeThumbColor,
        )


# In pythra/styles.py

# ... (keep all your other style classes)

@dataclass
class RadioTheme:
    """
    Defines the visual properties for a Radio button widget.
    """
    # The color of the radio button's fill and border when selected.
    fillColor: Optional[str] = None
    # The color of the splash/ripple effect on press.
    splashColor: Optional[str] = None

    def to_tuple(self) -> Tuple:
        """Creates a hashable tuple for use in style keys."""
        return (self.fillColor, self.splashColor)



class DropdownTheme:
    """Encapsulates the styling properties for the Dropdown widget."""

    def __init__(
        self,
        backgroundColor=Colors.hex("#FFFFFF"),
        borderColor=Colors.hex("#AAAAAA"),
        hoverColor=Colors.rgba(0, 0, 0, 0.1),
        dropdownHoverColor=Colors.rgba(0, 0, 0, 0.08),
        itemHoverColor=Colors.rgba(103, 80, 164, 0.1),
        width = "100%",
        height = "auto",
        dropDownHeight = "auto",
        borderWidth=1.0,
        borderRadius=8.0,
        textColor=Colors.hex("#000000"),
        fontSize=14.0,
        padding=EdgeInsets.symmetric(vertical=8, horizontal=12),
        dropdownColor=Colors.hex("#FFFFFF"),
        dropdownTextColor=Colors.hex("#000000"),
        selectedItemColor=Colors.hex("#E0E0E0"),
        selectedItemShape= BorderRadius.all(4),
        dropdownMargin=EdgeInsets.only(top=45),
        itemPadding = EdgeInsets.symmetric(horizontal=12, vertical=8),
    ):
        self.backgroundColor = backgroundColor
        self.borderColor = borderColor
        self.hoverColor = hoverColor
        self.dropdownHoverColor = dropdownHoverColor
        self.itemHoverColor = itemHoverColor
        self.width = width
        self.height = height
        self.dropDownHeight = dropDownHeight
        self.borderWidth = borderWidth
        self.borderRadius = borderRadius
        self.textColor = textColor
        self.fontSize = fontSize
        self.padding = padding
        self.dropdownColor = dropdownColor
        self.dropdownTextColor = dropdownTextColor
        self.selectedItemColor = selectedItemColor
        self.selectedItemShape = selectedItemShape
        self.dropdownMargin = dropdownMargin
        self.itemPadding = itemPadding



@dataclass
class GradientBorderTheme:
    """
    Defines the visual properties for a GradientBorderContainer.
    """
    # A list of CSS colors for the gradient.
    gradientColors: List[str] = field(default_factory=lambda: [
        '#ff4d4d', '#ffb86b', '#ffd166', '#7bed9f',
        '#6ad3ff', '#a78bfa', '#ff4d4d'
    ])
    
    # The CSS angle or direction for the linear gradient (e.g., '270deg', 'to right').
    gradientDirection: str = '270deg'
    
    # The speed of the animation (e.g., '5s', '10s').
    animationSpeed: str = '5s'
    
    # The animation timing function (e.g., 'linear', 'ease-in-out').
    animationTiming: str = 'linear'

    def to_tuple(self) -> Tuple:
        """Creates a hashable tuple for use in style keys."""
        return (
            tuple(self.gradientColors), # Convert list to tuple for hashing
            self.gradientDirection,
            self.animationSpeed,
            self.animationTiming
        )


# In pythra/styles.py

# Rename GradientBorderTheme to GradientTheme
@dataclass
class GradientTheme: # <-- RENAMED
    """
    Defines the visual properties for an animated gradient effect.
    """
    # A list of CSS colors for the gradient.
    gradientColors: List[str] = field(default_factory=lambda: [
        '#ff4d4d', '#ffb86b', '#ffd166', '#7bed9f',
        '#6ad3ff', '#a78bfa', '#ff4d4d'
    ])
    
    # The CSS angle or direction for the linear gradient.
    gradientDirection: str = '270deg'
    
    # The speed of the animation.
    animationSpeed: str = '5s'
    
    # The animation timing function.
    animationTiming: str = 'linear'

    # --- NEW: Rotation Animation ---
    # Set to a time (e.g., '10s') to enable rotation. Set to None to disable.
    rotationSpeed: Optional[str] = None 

    def to_tuple(self) -> Tuple:
        """Creates a hashable tuple for use in style keys."""
        return (
            tuple(self.gradientColors),
            self.gradientDirection,
            self.animationSpeed,
            self.animationTiming,
            self.rotationSpeed # <-- ADD TO TUPLE
        )


class Loader(Enum):
    """Enum for all available loader styles."""
    
    ARCADE = "arcade"
    ARROW = "arrow"
    BARS = "bars"
    BLOB = "blob"
    BOUNCING = "bouncing"
    CIRCLE = "circle"
    CLASSIC = "classic"
    CLONES = "clones"
    COLORFUL = "colorful"
    CONTINUOUS = "continuous"
    CUT = "cut"
    DANCERS = "dancers"
    DOTS = "dots"
    DOTS_BARS = "dots-bars"
    EYES = "eyes"
    FACTORY = "factory"
    FILLING = "filling"
    FLIPPING = "flipping"
    GLOWING = "glowing"
    GROWING = "growing"
    HUNGRY = "hungry"
    HYPNOTIC = "hypnotic"
    INFINITY = "infinity"
    LINE = "line"
    MAZE = "maze"
    MECHANIC = "mechanic"
    MOVING = "moving"
    NATURE = "nature"
    POLYGONS = "polygons"
    PROGRESS = "progress"
    PULSING = "pulsing"
    ROLLING = "rolling"
    SHAPES = "shapes"
    SHURIKEN = "shuriken"
    SPINNER = "spinner"
    SQUARE = "square"
    SQUARE_CIRCLE = "square-circle"
    THIN = "thin"
    TIME = "time"
    WAVY = "wavy"
    WOBBLING = "wobbling"
    ZIG_ZAG = "zig-zag"
    
    def __str__(self) -> str:
        """Return the lowercase string value of the enum."""
        return self.value



class LoaderStyle(Enum):
    """Enum for loader-styles CSS classes."""
    LOADER_3D_1 = "loader-3d-1"
    LOADER_3D_10 = "loader-3d-10"
    LOADER_3D_11 = "loader-3d-11"
    LOADER_3D_12 = "loader-3d-12"
    LOADER_3D_2 = "loader-3d-2"
    LOADER_3D_3 = "loader-3d-3"
    LOADER_3D_4 = "loader-3d-4"
    LOADER_3D_5 = "loader-3d-5"
    LOADER_3D_6 = "loader-3d-6"
    LOADER_3D_7 = "loader-3d-7"
    LOADER_3D_8 = "loader-3d-8"
    LOADER_3D_9 = "loader-3d-9"
    LOADER_ARCADE_1 = "loader-arcade-1"
    LOADER_ARCADE_10 = "loader-arcade-10"
    LOADER_ARCADE_2 = "loader-arcade-2"
    LOADER_ARCADE_3 = "loader-arcade-3"
    LOADER_ARCADE_4 = "loader-arcade-4"
    LOADER_ARCADE_5 = "loader-arcade-5"
    LOADER_ARCADE_6 = "loader-arcade-6"
    LOADER_ARCADE_7 = "loader-arcade-7"
    LOADER_ARCADE_8 = "loader-arcade-8"
    LOADER_ARCADE_9 = "loader-arcade-9"
    LOADER_ARROW_1 = "loader-arrow-1"
    LOADER_ARROW_10 = "loader-arrow-10"
    LOADER_ARROW_2 = "loader-arrow-2"
    LOADER_ARROW_3 = "loader-arrow-3"
    LOADER_ARROW_4 = "loader-arrow-4"
    LOADER_ARROW_5 = "loader-arrow-5"
    LOADER_ARROW_6 = "loader-arrow-6"
    LOADER_ARROW_7 = "loader-arrow-7"
    LOADER_ARROW_8 = "loader-arrow-8"
    LOADER_ARROW_9 = "loader-arrow-9"
    LOADER_BARS_1 = "loader-bars-1"
    LOADER_BARS_10 = "loader-bars-10"
    LOADER_BARS_11 = "loader-bars-11"
    LOADER_BARS_12 = "loader-bars-12"
    LOADER_BARS_13 = "loader-bars-13"
    LOADER_BARS_14 = "loader-bars-14"
    LOADER_BARS_15 = "loader-bars-15"
    LOADER_BARS_16 = "loader-bars-16"
    LOADER_BARS_17 = "loader-bars-17"
    LOADER_BARS_18 = "loader-bars-18"
    LOADER_BARS_19 = "loader-bars-19"
    LOADER_BARS_2 = "loader-bars-2"
    LOADER_BARS_20 = "loader-bars-20"
    LOADER_BARS_21 = "loader-bars-21"
    LOADER_BARS_22 = "loader-bars-22"
    LOADER_BARS_23 = "loader-bars-23"
    LOADER_BARS_24 = "loader-bars-24"
    LOADER_BARS_25 = "loader-bars-25"
    LOADER_BARS_26 = "loader-bars-26"
    LOADER_BARS_27 = "loader-bars-27"
    LOADER_BARS_28 = "loader-bars-28"
    LOADER_BARS_29 = "loader-bars-29"
    LOADER_BARS_3 = "loader-bars-3"
    LOADER_BARS_30 = "loader-bars-30"
    LOADER_BARS_4 = "loader-bars-4"
    LOADER_BARS_5 = "loader-bars-5"
    LOADER_BARS_6 = "loader-bars-6"
    LOADER_BARS_7 = "loader-bars-7"
    LOADER_BARS_8 = "loader-bars-8"
    LOADER_BARS_9 = "loader-bars-9"
    LOADER_BLOB_1 = "loader-blob-1"
    LOADER_BLOB_10 = "loader-blob-10"
    LOADER_BLOB_11 = "loader-blob-11"
    LOADER_BLOB_12 = "loader-blob-12"
    LOADER_BLOB_13 = "loader-blob-13"
    LOADER_BLOB_14 = "loader-blob-14"
    LOADER_BLOB_15 = "loader-blob-15"
    LOADER_BLOB_16 = "loader-blob-16"
    LOADER_BLOB_17 = "loader-blob-17"
    LOADER_BLOB_18 = "loader-blob-18"
    LOADER_BLOB_19 = "loader-blob-19"
    LOADER_BLOB_2 = "loader-blob-2"
    LOADER_BLOB_20 = "loader-blob-20"
    LOADER_BLOB_3 = "loader-blob-3"
    LOADER_BLOB_4 = "loader-blob-4"
    LOADER_BLOB_5 = "loader-blob-5"
    LOADER_BLOB_6 = "loader-blob-6"
    LOADER_BLOB_7 = "loader-blob-7"
    LOADER_BLOB_8 = "loader-blob-8"
    LOADER_BLOB_9 = "loader-blob-9"
    LOADER_BOUNCING_1 = "loader-bouncing-1"
    LOADER_BOUNCING_10 = "loader-bouncing-10"
    LOADER_BOUNCING_11 = "loader-bouncing-11"
    LOADER_BOUNCING_12 = "loader-bouncing-12"
    LOADER_BOUNCING_2 = "loader-bouncing-2"
    LOADER_BOUNCING_3 = "loader-bouncing-3"
    LOADER_BOUNCING_4 = "loader-bouncing-4"
    LOADER_BOUNCING_5 = "loader-bouncing-5"
    LOADER_BOUNCING_6 = "loader-bouncing-6"
    LOADER_BOUNCING_7 = "loader-bouncing-7"
    LOADER_BOUNCING_8 = "loader-bouncing-8"
    LOADER_BOUNCING_9 = "loader-bouncing-9"
    LOADER_CIRCLE_1 = "loader-circle-1"
    LOADER_CIRCLE_10 = "loader-circle-10"
    LOADER_CIRCLE_11 = "loader-circle-11"
    LOADER_CIRCLE_2 = "loader-circle-2"
    LOADER_CIRCLE_3 = "loader-circle-3"
    LOADER_CIRCLE_4 = "loader-circle-4"
    LOADER_CIRCLE_5 = "loader-circle-5"
    LOADER_CIRCLE_6 = "loader-circle-6"
    LOADER_CIRCLE_7 = "loader-circle-7"
    LOADER_CIRCLE_8 = "loader-circle-8"
    LOADER_CIRCLE_9 = "loader-circle-9"
    LOADER_CLASSIC_1 = "loader-classic-1"
    LOADER_CLASSIC_10 = "loader-classic-10"
    LOADER_CLASSIC_11 = "loader-classic-11"
    LOADER_CLASSIC_12 = "loader-classic-12"
    LOADER_CLASSIC_13 = "loader-classic-13"
    LOADER_CLASSIC_14 = "loader-classic-14"
    LOADER_CLASSIC_15 = "loader-classic-15"
    LOADER_CLASSIC_16 = "loader-classic-16"
    LOADER_CLASSIC_17 = "loader-classic-17"
    LOADER_CLASSIC_18 = "loader-classic-18"
    LOADER_CLASSIC_19 = "loader-classic-19"
    LOADER_CLASSIC_2 = "loader-classic-2"
    LOADER_CLASSIC_20 = "loader-classic-20"
    LOADER_CLASSIC_21 = "loader-classic-21"
    LOADER_CLASSIC_22 = "loader-classic-22"
    LOADER_CLASSIC_23 = "loader-classic-23"
    LOADER_CLASSIC_24 = "loader-classic-24"
    LOADER_CLASSIC_25 = "loader-classic-25"
    LOADER_CLASSIC_26 = "loader-classic-26"
    LOADER_CLASSIC_27 = "loader-classic-27"
    LOADER_CLASSIC_28 = "loader-classic-28"
    LOADER_CLASSIC_29 = "loader-classic-29"
    LOADER_CLASSIC_3 = "loader-classic-3"
    LOADER_CLASSIC_30 = "loader-classic-30"
    LOADER_CLASSIC_31 = "loader-classic-31"
    LOADER_CLASSIC_32 = "loader-classic-32"
    LOADER_CLASSIC_33 = "loader-classic-33"
    LOADER_CLASSIC_34 = "loader-classic-34"
    LOADER_CLASSIC_35 = "loader-classic-35"
    LOADER_CLASSIC_36 = "loader-classic-36"
    LOADER_CLASSIC_37 = "loader-classic-37"
    LOADER_CLASSIC_38 = "loader-classic-38"
    LOADER_CLASSIC_39 = "loader-classic-39"
    LOADER_CLASSIC_4 = "loader-classic-4"
    LOADER_CLASSIC_40 = "loader-classic-40"
    LOADER_CLASSIC_5 = "loader-classic-5"
    LOADER_CLASSIC_6 = "loader-classic-6"
    LOADER_CLASSIC_7 = "loader-classic-7"
    LOADER_CLASSIC_8 = "loader-classic-8"
    LOADER_CLASSIC_9 = "loader-classic-9"
    LOADER_CLONES_1 = "loader-clones-1"
    LOADER_CLONES_10 = "loader-clones-10"
    LOADER_CLONES_11 = "loader-clones-11"
    LOADER_CLONES_12 = "loader-clones-12"
    LOADER_CLONES_13 = "loader-clones-13"
    LOADER_CLONES_14 = "loader-clones-14"
    LOADER_CLONES_15 = "loader-clones-15"
    LOADER_CLONES_16 = "loader-clones-16"
    LOADER_CLONES_17 = "loader-clones-17"
    LOADER_CLONES_18 = "loader-clones-18"
    LOADER_CLONES_19 = "loader-clones-19"
    LOADER_CLONES_2 = "loader-clones-2"
    LOADER_CLONES_20 = "loader-clones-20"
    LOADER_CLONES_3 = "loader-clones-3"
    LOADER_CLONES_4 = "loader-clones-4"
    LOADER_CLONES_5 = "loader-clones-5"
    LOADER_CLONES_6 = "loader-clones-6"
    LOADER_CLONES_7 = "loader-clones-7"
    LOADER_CLONES_8 = "loader-clones-8"
    LOADER_CLONES_9 = "loader-clones-9"
    LOADER_COLORFUL_1 = "loader-colorful-1"
    LOADER_COLORFUL_10 = "loader-colorful-10"
    LOADER_COLORFUL_11 = "loader-colorful-11"
    LOADER_COLORFUL_12 = "loader-colorful-12"
    LOADER_COLORFUL_13 = "loader-colorful-13"
    LOADER_COLORFUL_14 = "loader-colorful-14"
    LOADER_COLORFUL_15 = "loader-colorful-15"
    LOADER_COLORFUL_16 = "loader-colorful-16"
    LOADER_COLORFUL_17 = "loader-colorful-17"
    LOADER_COLORFUL_18 = "loader-colorful-18"
    LOADER_COLORFUL_19 = "loader-colorful-19"
    LOADER_COLORFUL_2 = "loader-colorful-2"
    LOADER_COLORFUL_20 = "loader-colorful-20"
    LOADER_COLORFUL_3 = "loader-colorful-3"
    LOADER_COLORFUL_4 = "loader-colorful-4"
    LOADER_COLORFUL_5 = "loader-colorful-5"
    LOADER_COLORFUL_6 = "loader-colorful-6"
    LOADER_COLORFUL_7 = "loader-colorful-7"
    LOADER_COLORFUL_8 = "loader-colorful-8"
    LOADER_COLORFUL_9 = "loader-colorful-9"
    LOADER_CONTINUOUS_1 = "loader-continuous-1"
    LOADER_CONTINUOUS_10 = "loader-continuous-10"
    LOADER_CONTINUOUS_2 = "loader-continuous-2"
    LOADER_CONTINUOUS_3 = "loader-continuous-3"
    LOADER_CONTINUOUS_4 = "loader-continuous-4"
    LOADER_CONTINUOUS_5 = "loader-continuous-5"
    LOADER_CONTINUOUS_6 = "loader-continuous-6"
    LOADER_CONTINUOUS_7 = "loader-continuous-7"
    LOADER_CONTINUOUS_8 = "loader-continuous-8"
    LOADER_CONTINUOUS_9 = "loader-continuous-9"
    LOADER_CUT_1 = "loader-cut-1"
    LOADER_CUT_10 = "loader-cut-10"
    LOADER_CUT_2 = "loader-cut-2"
    LOADER_CUT_3 = "loader-cut-3"
    LOADER_CUT_4 = "loader-cut-4"
    LOADER_CUT_5 = "loader-cut-5"
    LOADER_CUT_6 = "loader-cut-6"
    LOADER_CUT_7 = "loader-cut-7"
    LOADER_CUT_8 = "loader-cut-8"
    LOADER_CUT_9 = "loader-cut-9"
    LOADER_DANCERS_1 = "loader-dancers-1"
    LOADER_DANCERS_10 = "loader-dancers-10"
    LOADER_DANCERS_2 = "loader-dancers-2"
    LOADER_DANCERS_3 = "loader-dancers-3"
    LOADER_DANCERS_4 = "loader-dancers-4"
    LOADER_DANCERS_5 = "loader-dancers-5"
    LOADER_DANCERS_6 = "loader-dancers-6"
    LOADER_DANCERS_7 = "loader-dancers-7"
    LOADER_DANCERS_8 = "loader-dancers-8"
    LOADER_DANCERS_9 = "loader-dancers-9"
    LOADER_DOTS_BARS_1 = "loader-dots-bars-1"
    LOADER_DOTS_BARS_10 = "loader-dots-bars-10"
    LOADER_DOTS_BARS_11 = "loader-dots-bars-11"
    LOADER_DOTS_BARS_12 = "loader-dots-bars-12"
    LOADER_DOTS_BARS_13 = "loader-dots-bars-13"
    LOADER_DOTS_BARS_14 = "loader-dots-bars-14"
    LOADER_DOTS_BARS_15 = "loader-dots-bars-15"
    LOADER_DOTS_BARS_16 = "loader-dots-bars-16"
    LOADER_DOTS_BARS_17 = "loader-dots-bars-17"
    LOADER_DOTS_BARS_18 = "loader-dots-bars-18"
    LOADER_DOTS_BARS_19 = "loader-dots-bars-19"
    LOADER_DOTS_BARS_2 = "loader-dots-bars-2"
    LOADER_DOTS_BARS_20 = "loader-dots-bars-20"
    LOADER_DOTS_BARS_3 = "loader-dots-bars-3"
    LOADER_DOTS_BARS_4 = "loader-dots-bars-4"
    LOADER_DOTS_BARS_5 = "loader-dots-bars-5"
    LOADER_DOTS_BARS_6 = "loader-dots-bars-6"
    LOADER_DOTS_BARS_7 = "loader-dots-bars-7"
    LOADER_DOTS_BARS_8 = "loader-dots-bars-8"
    LOADER_DOTS_BARS_9 = "loader-dots-bars-9"
    LOADER_DOTS_1 = "loader-dots-1"
    LOADER_DOTS_10 = "loader-dots-10"
    LOADER_DOTS_11 = "loader-dots-11"
    LOADER_DOTS_12 = "loader-dots-12"
    LOADER_DOTS_13 = "loader-dots-13"
    LOADER_DOTS_14 = "loader-dots-14"
    LOADER_DOTS_15 = "loader-dots-15"
    LOADER_DOTS_16 = "loader-dots-16"
    LOADER_DOTS_17 = "loader-dots-17"
    LOADER_DOTS_18 = "loader-dots-18"
    LOADER_DOTS_19 = "loader-dots-19"
    LOADER_DOTS_2 = "loader-dots-2"
    LOADER_DOTS_20 = "loader-dots-20"
    LOADER_DOTS_21 = "loader-dots-21"
    LOADER_DOTS_22 = "loader-dots-22"
    LOADER_DOTS_23 = "loader-dots-23"
    LOADER_DOTS_24 = "loader-dots-24"
    LOADER_DOTS_25 = "loader-dots-25"
    LOADER_DOTS_26 = "loader-dots-26"
    LOADER_DOTS_27 = "loader-dots-27"
    LOADER_DOTS_28 = "loader-dots-28"
    LOADER_DOTS_29 = "loader-dots-29"
    LOADER_DOTS_3 = "loader-dots-3"
    LOADER_DOTS_30 = "loader-dots-30"
    LOADER_DOTS_31 = "loader-dots-31"
    LOADER_DOTS_32 = "loader-dots-32"
    LOADER_DOTS_33 = "loader-dots-33"
    LOADER_DOTS_34 = "loader-dots-34"
    LOADER_DOTS_35 = "loader-dots-35"
    LOADER_DOTS_36 = "loader-dots-36"
    LOADER_DOTS_37 = "loader-dots-37"
    LOADER_DOTS_38 = "loader-dots-38"
    LOADER_DOTS_39 = "loader-dots-39"
    LOADER_DOTS_4 = "loader-dots-4"
    LOADER_DOTS_40 = "loader-dots-40"
    LOADER_DOTS_41 = "loader-dots-41"
    LOADER_DOTS_42 = "loader-dots-42"
    LOADER_DOTS_43 = "loader-dots-43"
    LOADER_DOTS_44 = "loader-dots-44"
    LOADER_DOTS_45 = "loader-dots-45"
    LOADER_DOTS_46 = "loader-dots-46"
    LOADER_DOTS_47 = "loader-dots-47"
    LOADER_DOTS_48 = "loader-dots-48"
    LOADER_DOTS_49 = "loader-dots-49"
    LOADER_DOTS_5 = "loader-dots-5"
    LOADER_DOTS_50 = "loader-dots-50"
    LOADER_DOTS_6 = "loader-dots-6"
    LOADER_DOTS_7 = "loader-dots-7"
    LOADER_DOTS_8 = "loader-dots-8"
    LOADER_DOTS_9 = "loader-dots-9"
    LOADER_EYES_1 = "loader-eyes-1"
    LOADER_EYES_10 = "loader-eyes-10"
    LOADER_EYES_2 = "loader-eyes-2"
    LOADER_EYES_3 = "loader-eyes-3"
    LOADER_EYES_4 = "loader-eyes-4"
    LOADER_EYES_5 = "loader-eyes-5"
    LOADER_EYES_6 = "loader-eyes-6"
    LOADER_EYES_7 = "loader-eyes-7"
    LOADER_EYES_8 = "loader-eyes-8"
    LOADER_EYES_9 = "loader-eyes-9"
    LOADER_FACTORY_1 = "loader-factory-1"
    LOADER_FACTORY_2 = "loader-factory-2"
    LOADER_FACTORY_3 = "loader-factory-3"
    LOADER_FACTORY_4 = "loader-factory-4"
    LOADER_FACTORY_5 = "loader-factory-5"
    LOADER_FACTORY_6 = "loader-factory-6"
    LOADER_FACTORY_7 = "loader-factory-7"
    LOADER_FACTORY_8 = "loader-factory-8"
    LOADER_FILLING_1 = "loader-filling-1"
    LOADER_FILLING_10 = "loader-filling-10"
    LOADER_FILLING_11 = "loader-filling-11"
    LOADER_FILLING_12 = "loader-filling-12"
    LOADER_FILLING_13 = "loader-filling-13"
    LOADER_FILLING_14 = "loader-filling-14"
    LOADER_FILLING_15 = "loader-filling-15"
    LOADER_FILLING_16 = "loader-filling-16"
    LOADER_FILLING_17 = "loader-filling-17"
    LOADER_FILLING_18 = "loader-filling-18"
    LOADER_FILLING_19 = "loader-filling-19"
    LOADER_FILLING_2 = "loader-filling-2"
    LOADER_FILLING_20 = "loader-filling-20"
    LOADER_FILLING_3 = "loader-filling-3"
    LOADER_FILLING_4 = "loader-filling-4"
    LOADER_FILLING_5 = "loader-filling-5"
    LOADER_FILLING_6 = "loader-filling-6"
    LOADER_FILLING_7 = "loader-filling-7"
    LOADER_FILLING_8 = "loader-filling-8"
    LOADER_FILLING_9 = "loader-filling-9"
    LOADER_FLIPPING_1 = "loader-flipping-1"
    LOADER_FLIPPING_10 = "loader-flipping-10"
    LOADER_FLIPPING_11 = "loader-flipping-11"
    LOADER_FLIPPING_12 = "loader-flipping-12"
    LOADER_FLIPPING_13 = "loader-flipping-13"
    LOADER_FLIPPING_14 = "loader-flipping-14"
    LOADER_FLIPPING_15 = "loader-flipping-15"
    LOADER_FLIPPING_16 = "loader-flipping-16"
    LOADER_FLIPPING_17 = "loader-flipping-17"
    LOADER_FLIPPING_18 = "loader-flipping-18"
    LOADER_FLIPPING_19 = "loader-flipping-19"
    LOADER_FLIPPING_2 = "loader-flipping-2"
    LOADER_FLIPPING_20 = "loader-flipping-20"
    LOADER_FLIPPING_3 = "loader-flipping-3"
    LOADER_FLIPPING_4 = "loader-flipping-4"
    LOADER_FLIPPING_5 = "loader-flipping-5"
    LOADER_FLIPPING_6 = "loader-flipping-6"
    LOADER_FLIPPING_7 = "loader-flipping-7"
    LOADER_FLIPPING_8 = "loader-flipping-8"
    LOADER_FLIPPING_9 = "loader-flipping-9"
    LOADER_GLOWING_1 = "loader-glowing-1"
    LOADER_GLOWING_10 = "loader-glowing-10"
    LOADER_GLOWING_11 = "loader-glowing-11"
    LOADER_GLOWING_12 = "loader-glowing-12"
    LOADER_GLOWING_2 = "loader-glowing-2"
    LOADER_GLOWING_3 = "loader-glowing-3"
    LOADER_GLOWING_4 = "loader-glowing-4"
    LOADER_GLOWING_5 = "loader-glowing-5"
    LOADER_GLOWING_6 = "loader-glowing-6"
    LOADER_GLOWING_7 = "loader-glowing-7"
    LOADER_GLOWING_8 = "loader-glowing-8"
    LOADER_GLOWING_9 = "loader-glowing-9"
    LOADER_GROWING_1 = "loader-growing-1"
    LOADER_GROWING_10 = "loader-growing-10"
    LOADER_GROWING_2 = "loader-growing-2"
    LOADER_GROWING_3 = "loader-growing-3"
    LOADER_GROWING_4 = "loader-growing-4"
    LOADER_GROWING_5 = "loader-growing-5"
    LOADER_GROWING_6 = "loader-growing-6"
    LOADER_GROWING_7 = "loader-growing-7"
    LOADER_GROWING_8 = "loader-growing-8"
    LOADER_GROWING_9 = "loader-growing-9"
    LOADER_HUNGRY_1 = "loader-hungry-1"
    LOADER_HUNGRY_2 = "loader-hungry-2"
    LOADER_HUNGRY_3 = "loader-hungry-3"
    LOADER_HUNGRY_4 = "loader-hungry-4"
    LOADER_HUNGRY_5 = "loader-hungry-5"
    LOADER_HUNGRY_6 = "loader-hungry-6"
    LOADER_HUNGRY_7 = "loader-hungry-7"
    LOADER_HUNGRY_8 = "loader-hungry-8"
    LOADER_HYPNOTIC_1 = "loader-hypnotic-1"
    LOADER_HYPNOTIC_10 = "loader-hypnotic-10"
    LOADER_HYPNOTIC_11 = "loader-hypnotic-11"
    LOADER_HYPNOTIC_12 = "loader-hypnotic-12"
    LOADER_HYPNOTIC_13 = "loader-hypnotic-13"
    LOADER_HYPNOTIC_14 = "loader-hypnotic-14"
    LOADER_HYPNOTIC_15 = "loader-hypnotic-15"
    LOADER_HYPNOTIC_16 = "loader-hypnotic-16"
    LOADER_HYPNOTIC_17 = "loader-hypnotic-17"
    LOADER_HYPNOTIC_18 = "loader-hypnotic-18"
    LOADER_HYPNOTIC_19 = "loader-hypnotic-19"
    LOADER_HYPNOTIC_2 = "loader-hypnotic-2"
    LOADER_HYPNOTIC_20 = "loader-hypnotic-20"
    LOADER_HYPNOTIC_3 = "loader-hypnotic-3"
    LOADER_HYPNOTIC_4 = "loader-hypnotic-4"
    LOADER_HYPNOTIC_5 = "loader-hypnotic-5"
    LOADER_HYPNOTIC_6 = "loader-hypnotic-6"
    LOADER_HYPNOTIC_7 = "loader-hypnotic-7"
    LOADER_HYPNOTIC_8 = "loader-hypnotic-8"
    LOADER_HYPNOTIC_9 = "loader-hypnotic-9"
    LOADER_INFINITY_1 = "loader-infinity-1"
    LOADER_INFINITY_10 = "loader-infinity-10"
    LOADER_INFINITY_11 = "loader-infinity-11"
    LOADER_INFINITY_12 = "loader-infinity-12"
    LOADER_INFINITY_13 = "loader-infinity-13"
    LOADER_INFINITY_14 = "loader-infinity-14"
    LOADER_INFINITY_15 = "loader-infinity-15"
    LOADER_INFINITY_16 = "loader-infinity-16"
    LOADER_INFINITY_17 = "loader-infinity-17"
    LOADER_INFINITY_18 = "loader-infinity-18"
    LOADER_INFINITY_19 = "loader-infinity-19"
    LOADER_INFINITY_2 = "loader-infinity-2"
    LOADER_INFINITY_20 = "loader-infinity-20"
    LOADER_INFINITY_3 = "loader-infinity-3"
    LOADER_INFINITY_4 = "loader-infinity-4"
    LOADER_INFINITY_5 = "loader-infinity-5"
    LOADER_INFINITY_6 = "loader-infinity-6"
    LOADER_INFINITY_7 = "loader-infinity-7"
    LOADER_INFINITY_8 = "loader-infinity-8"
    LOADER_INFINITY_9 = "loader-infinity-9"
    LOADER_LINE_1 = "loader-line-1"
    LOADER_LINE_10 = "loader-line-10"
    LOADER_LINE_11 = "loader-line-11"
    LOADER_LINE_12 = "loader-line-12"
    LOADER_LINE_13 = "loader-line-13"
    LOADER_LINE_14 = "loader-line-14"
    LOADER_LINE_15 = "loader-line-15"
    LOADER_LINE_16 = "loader-line-16"
    LOADER_LINE_17 = "loader-line-17"
    LOADER_LINE_18 = "loader-line-18"
    LOADER_LINE_19 = "loader-line-19"
    LOADER_LINE_2 = "loader-line-2"
    LOADER_LINE_20 = "loader-line-20"
    LOADER_LINE_3 = "loader-line-3"
    LOADER_LINE_4 = "loader-line-4"
    LOADER_LINE_5 = "loader-line-5"
    LOADER_LINE_6 = "loader-line-6"
    LOADER_LINE_7 = "loader-line-7"
    LOADER_LINE_8 = "loader-line-8"
    LOADER_LINE_9 = "loader-line-9"
    LOADER_MAZE_1 = "loader-maze-1"
    LOADER_MAZE_10 = "loader-maze-10"
    LOADER_MAZE_2 = "loader-maze-2"
    LOADER_MAZE_3 = "loader-maze-3"
    LOADER_MAZE_4 = "loader-maze-4"
    LOADER_MAZE_5 = "loader-maze-5"
    LOADER_MAZE_6 = "loader-maze-6"
    LOADER_MAZE_7 = "loader-maze-7"
    LOADER_MAZE_8 = "loader-maze-8"
    LOADER_MAZE_9 = "loader-maze-9"
    LOADER_MECHANIC_1 = "loader-mechanic-1"
    LOADER_MECHANIC_10 = "loader-mechanic-10"
    LOADER_MECHANIC_11 = "loader-mechanic-11"
    LOADER_MECHANIC_12 = "loader-mechanic-12"
    LOADER_MECHANIC_2 = "loader-mechanic-2"
    LOADER_MECHANIC_3 = "loader-mechanic-3"
    LOADER_MECHANIC_4 = "loader-mechanic-4"
    LOADER_MECHANIC_5 = "loader-mechanic-5"
    LOADER_MECHANIC_6 = "loader-mechanic-6"
    LOADER_MECHANIC_7 = "loader-mechanic-7"
    LOADER_MECHANIC_8 = "loader-mechanic-8"
    LOADER_MECHANIC_9 = "loader-mechanic-9"
    LOADER_MOVING_1 = "loader-moving-1"
    LOADER_MOVING_10 = "loader-moving-10"
    LOADER_MOVING_2 = "loader-moving-2"
    LOADER_MOVING_3 = "loader-moving-3"
    LOADER_MOVING_4 = "loader-moving-4"
    LOADER_MOVING_5 = "loader-moving-5"
    LOADER_MOVING_6 = "loader-moving-6"
    LOADER_MOVING_7 = "loader-moving-7"
    LOADER_MOVING_8 = "loader-moving-8"
    LOADER_MOVING_9 = "loader-moving-9"
    LOADER_NATURE_1 = "loader-nature-1"
    LOADER_NATURE_10 = "loader-nature-10"
    LOADER_NATURE_11 = "loader-nature-11"
    LOADER_NATURE_12 = "loader-nature-12"
    LOADER_NATURE_13 = "loader-nature-13"
    LOADER_NATURE_14 = "loader-nature-14"
    LOADER_NATURE_15 = "loader-nature-15"
    LOADER_NATURE_16 = "loader-nature-16"
    LOADER_NATURE_2 = "loader-nature-2"
    LOADER_NATURE_3 = "loader-nature-3"
    LOADER_NATURE_4 = "loader-nature-4"
    LOADER_NATURE_5 = "loader-nature-5"
    LOADER_NATURE_6 = "loader-nature-6"
    LOADER_NATURE_7 = "loader-nature-7"
    LOADER_NATURE_8 = "loader-nature-8"
    LOADER_NATURE_9 = "loader-nature-9"
    LOADER_POLYGONS_1 = "loader-polygons-1"
    LOADER_POLYGONS_10 = "loader-polygons-10"
    LOADER_POLYGONS_11 = "loader-polygons-11"
    LOADER_POLYGONS_12 = "loader-polygons-12"
    LOADER_POLYGONS_2 = "loader-polygons-2"
    LOADER_POLYGONS_3 = "loader-polygons-3"
    LOADER_POLYGONS_4 = "loader-polygons-4"
    LOADER_POLYGONS_5 = "loader-polygons-5"
    LOADER_POLYGONS_6 = "loader-polygons-6"
    LOADER_POLYGONS_7 = "loader-polygons-7"
    LOADER_POLYGONS_8 = "loader-polygons-8"
    LOADER_POLYGONS_9 = "loader-polygons-9"
    LOADER_PROGRESS_1 = "loader-progress-1"
    LOADER_PROGRESS_10 = "loader-progress-10"
    LOADER_PROGRESS_11 = "loader-progress-11"
    LOADER_PROGRESS_12 = "loader-progress-12"
    LOADER_PROGRESS_13 = "loader-progress-13"
    LOADER_PROGRESS_14 = "loader-progress-14"
    LOADER_PROGRESS_15 = "loader-progress-15"
    LOADER_PROGRESS_16 = "loader-progress-16"
    LOADER_PROGRESS_17 = "loader-progress-17"
    LOADER_PROGRESS_18 = "loader-progress-18"
    LOADER_PROGRESS_19 = "loader-progress-19"
    LOADER_PROGRESS_2 = "loader-progress-2"
    LOADER_PROGRESS_20 = "loader-progress-20"
    LOADER_PROGRESS_3 = "loader-progress-3"
    LOADER_PROGRESS_4 = "loader-progress-4"
    LOADER_PROGRESS_5 = "loader-progress-5"
    LOADER_PROGRESS_6 = "loader-progress-6"
    LOADER_PROGRESS_7 = "loader-progress-7"
    LOADER_PROGRESS_8 = "loader-progress-8"
    LOADER_PROGRESS_9 = "loader-progress-9"
    LOADER_PULSING_1 = "loader-pulsing-1"
    LOADER_PULSING_10 = "loader-pulsing-10"
    LOADER_PULSING_2 = "loader-pulsing-2"
    LOADER_PULSING_3 = "loader-pulsing-3"
    LOADER_PULSING_4 = "loader-pulsing-4"
    LOADER_PULSING_5 = "loader-pulsing-5"
    LOADER_PULSING_6 = "loader-pulsing-6"
    LOADER_PULSING_7 = "loader-pulsing-7"
    LOADER_PULSING_8 = "loader-pulsing-8"
    LOADER_PULSING_9 = "loader-pulsing-9"
    LOADER_ROLLING_1 = "loader-rolling-1"
    LOADER_ROLLING_10 = "loader-rolling-10"
    LOADER_ROLLING_2 = "loader-rolling-2"
    LOADER_ROLLING_3 = "loader-rolling-3"
    LOADER_ROLLING_4 = "loader-rolling-4"
    LOADER_ROLLING_5 = "loader-rolling-5"
    LOADER_ROLLING_6 = "loader-rolling-6"
    LOADER_ROLLING_7 = "loader-rolling-7"
    LOADER_ROLLING_8 = "loader-rolling-8"
    LOADER_ROLLING_9 = "loader-rolling-9"
    LOADER_SHAPES_1 = "loader-shapes-1"
    LOADER_SHAPES_10 = "loader-shapes-10"
    LOADER_SHAPES_11 = "loader-shapes-11"
    LOADER_SHAPES_12 = "loader-shapes-12"
    LOADER_SHAPES_13 = "loader-shapes-13"
    LOADER_SHAPES_14 = "loader-shapes-14"
    LOADER_SHAPES_15 = "loader-shapes-15"
    LOADER_SHAPES_16 = "loader-shapes-16"
    LOADER_SHAPES_17 = "loader-shapes-17"
    LOADER_SHAPES_18 = "loader-shapes-18"
    LOADER_SHAPES_19 = "loader-shapes-19"
    LOADER_SHAPES_2 = "loader-shapes-2"
    LOADER_SHAPES_20 = "loader-shapes-20"
    LOADER_SHAPES_21 = "loader-shapes-21"
    LOADER_SHAPES_22 = "loader-shapes-22"
    LOADER_SHAPES_23 = "loader-shapes-23"
    LOADER_SHAPES_24 = "loader-shapes-24"
    LOADER_SHAPES_25 = "loader-shapes-25"
    LOADER_SHAPES_26 = "loader-shapes-26"
    LOADER_SHAPES_27 = "loader-shapes-27"
    LOADER_SHAPES_28 = "loader-shapes-28"
    LOADER_SHAPES_29 = "loader-shapes-29"
    LOADER_SHAPES_3 = "loader-shapes-3"
    LOADER_SHAPES_30 = "loader-shapes-30"
    LOADER_SHAPES_31 = "loader-shapes-31"
    LOADER_SHAPES_32 = "loader-shapes-32"
    LOADER_SHAPES_33 = "loader-shapes-33"
    LOADER_SHAPES_34 = "loader-shapes-34"
    LOADER_SHAPES_35 = "loader-shapes-35"
    LOADER_SHAPES_36 = "loader-shapes-36"
    LOADER_SHAPES_37 = "loader-shapes-37"
    LOADER_SHAPES_38 = "loader-shapes-38"
    LOADER_SHAPES_39 = "loader-shapes-39"
    LOADER_SHAPES_4 = "loader-shapes-4"
    LOADER_SHAPES_40 = "loader-shapes-40"
    LOADER_SHAPES_5 = "loader-shapes-5"
    LOADER_SHAPES_6 = "loader-shapes-6"
    LOADER_SHAPES_7 = "loader-shapes-7"
    LOADER_SHAPES_8 = "loader-shapes-8"
    LOADER_SHAPES_9 = "loader-shapes-9"
    LOADER_SHURIKEN_1 = "loader-shuriken-1"
    LOADER_SHURIKEN_10 = "loader-shuriken-10"
    LOADER_SHURIKEN_2 = "loader-shuriken-2"
    LOADER_SHURIKEN_3 = "loader-shuriken-3"
    LOADER_SHURIKEN_4 = "loader-shuriken-4"
    LOADER_SHURIKEN_5 = "loader-shuriken-5"
    LOADER_SHURIKEN_6 = "loader-shuriken-6"
    LOADER_SHURIKEN_7 = "loader-shuriken-7"
    LOADER_SHURIKEN_8 = "loader-shuriken-8"
    LOADER_SHURIKEN_9 = "loader-shuriken-9"
    LOADER_SPINNER_1 = "loader-spinner-1"
    LOADER_SPINNER_10 = "loader-spinner-10"
    LOADER_SPINNER_11 = "loader-spinner-11"
    LOADER_SPINNER_12 = "loader-spinner-12"
    LOADER_SPINNER_13 = "loader-spinner-13"
    LOADER_SPINNER_14 = "loader-spinner-14"
    LOADER_SPINNER_15 = "loader-spinner-15"
    LOADER_SPINNER_16 = "loader-spinner-16"
    LOADER_SPINNER_17 = "loader-spinner-17"
    LOADER_SPINNER_18 = "loader-spinner-18"
    LOADER_SPINNER_19 = "loader-spinner-19"
    LOADER_SPINNER_2 = "loader-spinner-2"
    LOADER_SPINNER_20 = "loader-spinner-20"
    LOADER_SPINNER_21 = "loader-spinner-21"
    LOADER_SPINNER_22 = "loader-spinner-22"
    LOADER_SPINNER_23 = "loader-spinner-23"
    LOADER_SPINNER_24 = "loader-spinner-24"
    LOADER_SPINNER_25 = "loader-spinner-25"
    LOADER_SPINNER_26 = "loader-spinner-26"
    LOADER_SPINNER_27 = "loader-spinner-27"
    LOADER_SPINNER_28 = "loader-spinner-28"
    LOADER_SPINNER_29 = "loader-spinner-29"
    LOADER_SPINNER_3 = "loader-spinner-3"
    LOADER_SPINNER_30 = "loader-spinner-30"
    LOADER_SPINNER_4 = "loader-spinner-4"
    LOADER_SPINNER_5 = "loader-spinner-5"
    LOADER_SPINNER_6 = "loader-spinner-6"
    LOADER_SPINNER_7 = "loader-spinner-7"
    LOADER_SPINNER_8 = "loader-spinner-8"
    LOADER_SPINNER_9 = "loader-spinner-9"
    LOADER_SQUARE_CIRCLE_1 = "loader-square-circle-1"
    LOADER_SQUARE_CIRCLE_10 = "loader-square-circle-10"
    LOADER_SQUARE_CIRCLE_2 = "loader-square-circle-2"
    LOADER_SQUARE_CIRCLE_3 = "loader-square-circle-3"
    LOADER_SQUARE_CIRCLE_4 = "loader-square-circle-4"
    LOADER_SQUARE_CIRCLE_5 = "loader-square-circle-5"
    LOADER_SQUARE_CIRCLE_6 = "loader-square-circle-6"
    LOADER_SQUARE_CIRCLE_7 = "loader-square-circle-7"
    LOADER_SQUARE_CIRCLE_8 = "loader-square-circle-8"
    LOADER_SQUARE_CIRCLE_9 = "loader-square-circle-9"
    LOADER_SQUARE_1 = "loader-square-1"
    LOADER_SQUARE_10 = "loader-square-10"
    LOADER_SQUARE_11 = "loader-square-11"
    LOADER_SQUARE_2 = "loader-square-2"
    LOADER_SQUARE_3 = "loader-square-3"
    LOADER_SQUARE_4 = "loader-square-4"
    LOADER_SQUARE_5 = "loader-square-5"
    LOADER_SQUARE_6 = "loader-square-6"
    LOADER_SQUARE_7 = "loader-square-7"
    LOADER_SQUARE_8 = "loader-square-8"
    LOADER_SQUARE_9 = "loader-square-9"
    LOADER_THIN_1 = "loader-thin-1"
    LOADER_THIN_10 = "loader-thin-10"
    LOADER_THIN_2 = "loader-thin-2"
    LOADER_THIN_3 = "loader-thin-3"
    LOADER_THIN_4 = "loader-thin-4"
    LOADER_THIN_5 = "loader-thin-5"
    LOADER_THIN_6 = "loader-thin-6"
    LOADER_THIN_7 = "loader-thin-7"
    LOADER_THIN_8 = "loader-thin-8"
    LOADER_THIN_9 = "loader-thin-9"
    LOADER_TIME_1 = "loader-time-1"
    LOADER_TIME_10 = "loader-time-10"
    LOADER_TIME_2 = "loader-time-2"
    LOADER_TIME_3 = "loader-time-3"
    LOADER_TIME_4 = "loader-time-4"
    LOADER_TIME_5 = "loader-time-5"
    LOADER_TIME_6 = "loader-time-6"
    LOADER_TIME_7 = "loader-time-7"
    LOADER_TIME_8 = "loader-time-8"
    LOADER_TIME_9 = "loader-time-9"
    LOADER_WAVY_1 = "loader-wavy-1"
    LOADER_WAVY_10 = "loader-wavy-10"
    LOADER_WAVY_11 = "loader-wavy-11"
    LOADER_WAVY_12 = "loader-wavy-12"
    LOADER_WAVY_13 = "loader-wavy-13"
    LOADER_WAVY_14 = "loader-wavy-14"
    LOADER_WAVY_15 = "loader-wavy-15"
    LOADER_WAVY_16 = "loader-wavy-16"
    LOADER_WAVY_2 = "loader-wavy-2"
    LOADER_WAVY_3 = "loader-wavy-3"
    LOADER_WAVY_4 = "loader-wavy-4"
    LOADER_WAVY_5 = "loader-wavy-5"
    LOADER_WAVY_6 = "loader-wavy-6"
    LOADER_WAVY_7 = "loader-wavy-7"
    LOADER_WAVY_8 = "loader-wavy-8"
    LOADER_WAVY_9 = "loader-wavy-9"
    LOADER_WOBBLING_1 = "loader-wobbling-1"
    LOADER_WOBBLING_10 = "loader-wobbling-10"
    LOADER_WOBBLING_11 = "loader-wobbling-11"
    LOADER_WOBBLING_12 = "loader-wobbling-12"
    LOADER_WOBBLING_13 = "loader-wobbling-13"
    LOADER_WOBBLING_14 = "loader-wobbling-14"
    LOADER_WOBBLING_15 = "loader-wobbling-15"
    LOADER_WOBBLING_16 = "loader-wobbling-16"
    LOADER_WOBBLING_17 = "loader-wobbling-17"
    LOADER_WOBBLING_18 = "loader-wobbling-18"
    LOADER_WOBBLING_19 = "loader-wobbling-19"
    LOADER_WOBBLING_2 = "loader-wobbling-2"
    LOADER_WOBBLING_20 = "loader-wobbling-20"
    LOADER_WOBBLING_3 = "loader-wobbling-3"
    LOADER_WOBBLING_4 = "loader-wobbling-4"
    LOADER_WOBBLING_5 = "loader-wobbling-5"
    LOADER_WOBBLING_6 = "loader-wobbling-6"
    LOADER_WOBBLING_7 = "loader-wobbling-7"
    LOADER_WOBBLING_8 = "loader-wobbling-8"
    LOADER_WOBBLING_9 = "loader-wobbling-9"
    LOADER_ZIG_ZAG_1 = "loader-zig-zag-1"
    LOADER_ZIG_ZAG_10 = "loader-zig-zag-10"
    LOADER_ZIG_ZAG_11 = "loader-zig-zag-11"
    LOADER_ZIG_ZAG_12 = "loader-zig-zag-12"
    LOADER_ZIG_ZAG_13 = "loader-zig-zag-13"
    LOADER_ZIG_ZAG_14 = "loader-zig-zag-14"
    LOADER_ZIG_ZAG_15 = "loader-zig-zag-15"
    LOADER_ZIG_ZAG_16 = "loader-zig-zag-16"
    LOADER_ZIG_ZAG_17 = "loader-zig-zag-17"
    LOADER_ZIG_ZAG_18 = "loader-zig-zag-18"
    LOADER_ZIG_ZAG_19 = "loader-zig-zag-19"
    LOADER_ZIG_ZAG_2 = "loader-zig-zag-2"
    LOADER_ZIG_ZAG_20 = "loader-zig-zag-20"
    LOADER_ZIG_ZAG_3 = "loader-zig-zag-3"
    LOADER_ZIG_ZAG_4 = "loader-zig-zag-4"
    LOADER_ZIG_ZAG_5 = "loader-zig-zag-5"
    LOADER_ZIG_ZAG_6 = "loader-zig-zag-6"
    LOADER_ZIG_ZAG_7 = "loader-zig-zag-7"
    LOADER_ZIG_ZAG_8 = "loader-zig-zag-8"
    LOADER_ZIG_ZAG_9 = "loader-zig-zag-9"

    def __str__(self) -> str:
        return self.value


# --- Matrix4 Implementation for Transform Widget ---
class Matrix4:
    """
    Represents a 4x4 matrix for 3D transformations.
    Compatible with reconciliation.
    Stored in column-major order (like OpenGL/Flutter/CSS matrix3d).
    """
    def __init__(self, storage: Optional[List[float]] = None):
        """
        Initializes Matrix4.
        Args:
            storage: List of 16 floats in column-major order. Defaults to identity.
        """
        if storage:
            if len(storage) != 16:
                raise ValueError("Matrix4 storage must have 16 values.")
            self.storage = list(storage)
        else:
            self.storage = [
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0
            ]

    @staticmethod
    def identity() -> 'Matrix4':
        return Matrix4()

    @staticmethod
    def rotationZ(radians: float) -> 'Matrix4':
        """Returns a rotation matrix around the Z axis."""
        c = math.cos(radians)
        s = math.sin(radians)
        # Column-major
        return Matrix4([
             c,  s, 0.0, 0.0,
            -s,  c, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        ])
    
    @staticmethod
    def rotationX(radians: float) -> 'Matrix4':
        """Returns a rotation matrix around the X axis."""
        c = math.cos(radians)
        s = math.sin(radians)
        return Matrix4([
            1.0, 0.0, 0.0, 0.0,
            0.0,  c,  s, 0.0,
            0.0, -s,  c, 0.0,
            0.0, 0.0, 0.0, 1.0
        ])

    @staticmethod
    def rotationY(radians: float) -> 'Matrix4':
        """Returns a rotation matrix around the Y axis."""
        c = math.cos(radians)
        s = math.sin(radians)
        return Matrix4([
             c, 0.0, -s, 0.0,
            0.0, 1.0, 0.0, 0.0,
             s, 0.0,  c, 0.0,
            0.0, 0.0, 0.0, 1.0
        ])

    @staticmethod
    def translationValues(x: float, y: float, z: float) -> 'Matrix4':
        """Returns a translation matrix."""
        return Matrix4([
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
              x,   y,   z, 1.0
        ])

    @staticmethod
    def diagonal3Values(x: float, y: float, z: float) -> 'Matrix4':
        """Returns a scaling matrix."""
        return Matrix4([
              x, 0.0, 0.0, 0.0,
            0.0,   y, 0.0, 0.0,
            0.0, 0.0,   z, 0.0,
            0.0, 0.0, 0.0, 1.0
        ])
    
    @staticmethod
    def skew(alpha: float, beta: float) -> 'Matrix4':
        """
        Returns a skew matrix.
        alpha: Skew along X axis (radians/tan value usually, but here simplifies to tan for standard CSS skew)
        beta: Skew along Y axis
        Note: CSS matrix3d uses tan(alpha) for skew.
        """
        tan_alpha = math.tan(alpha)
        tan_beta = math.tan(beta)
        return Matrix4([
               1.0, tan_beta, 0.0, 0.0,
            tan_alpha,      1.0, 0.0, 0.0,
               0.0,      0.0, 1.0, 0.0,
               0.0,      0.0, 0.0, 1.0
        ])

    @staticmethod
    def compose(translation: Tuple[float, float, float], 
                rotation: 'Matrix4', 
                scale: Tuple[float, float, float]) -> 'Matrix4':
        """
        Composes a matrix from translation, rotation, and scale.
        Order: Translation * Rotation * Scale (T * R * S)
        """
        t = Matrix4.translationValues(*translation)
        s = Matrix4.diagonal3Values(*scale)
        return t.multiply(rotation).multiply(s)

    def multiply(self, other: 'Matrix4') -> 'Matrix4':
        """Returns the result of satisfying this * other."""
        a = self.storage
        b = other.storage
        result = [0.0] * 16
        
        # 4x4 Matrix multiplication (Column-Major)
        # C = A * B
        # C_col_k = A * B_col_k
        
        for r in range(4): # Row
            for c in range(4): # Column
                sum_val = 0.0
                for k in range(4):
                    # A accesses: row r, col k -> index k*4 + r
                    # B accesses: row k, col c -> index c*4 + k
                    sum_val += a[k*4 + r] * b[c*4 + k]
                result[c*4 + r] = sum_val
        
        return Matrix4(result)
        
    def __mul__(self, other: 'Matrix4') -> 'Matrix4':
        return self.multiply(other)

    def scale(self, x: float, y: float = None, z: float = None) -> 'Matrix4':
        """Post-multiplies this matrix by a scale matrix."""
        if y is None: y = x
        if z is None: z = 1.0 # 2D scale usually ignores Z
        s = Matrix4.diagonal3Values(x, y, z)
        return self.multiply(s) # Post-multiply: this * s

    def translate(self, x: float, y: float, z: float = 0.0) -> 'Matrix4':
        """Post-multiplies this matrix by a translation matrix."""
        t = Matrix4.translationValues(x, y, z)
        return self.multiply(t) # Post-multiply: this * t
    
    def rotateZ(self, radians: float) -> 'Matrix4':
        """Post-multiplies this matrix by a Z-rotation matrix."""
        r = Matrix4.rotationZ(radians)
        return self.multiply(r)

    # --- CSS Conversion ---
    def to_css(self) -> str:
        """Returns the CSS matrix3d string."""
        # CSS matrix3d takes 16 values in column-major order, comma-separated.
        # Ensure values are floats
        vals = [f"{v:.6f}" for v in self.storage] # Limit precision
        return f"matrix3d({', '.join(vals)})"

    # --- Compatibility ---
    def __eq__(self, other):
        if not isinstance(other, Matrix4):
            return NotImplemented
        # Allow small epsilon for float comparison? Keeping it strict for now for styles
        return self.storage == other.storage

    def __hash__(self):
        return hash(tuple(self.storage))

    def __repr__(self):
        return f"Matrix4({self.storage})"

    def to_tuple(self):
        return tuple(self.storage)