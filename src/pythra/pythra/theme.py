from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ThemeData:
    """
    Defines the color palette and other theme attributes.
    Follows Material Design 3 naming conventions.
    """
    # Primary Palette
    primary: str = '#6750A4'
    onPrimary: str = '#FFFFFF'
    primaryContainer: str = '#EADDFF'
    onPrimaryContainer: str = '#21005D'
    
    # Secondary Palette
    secondary: str = '#625B71'
    onSecondary: str = '#FFFFFF'
    secondaryContainer: str = '#E8DEF8'
    onSecondaryContainer: str = '#1D192B'
    
    # Tertiary Palette
    tertiary: str = '#7D5260'
    onTertiary: str = '#FFFFFF'
    tertiaryContainer: str = '#FFD8E4'
    onTertiaryContainer: str = '#31111D'
    
    # Error Palette
    error: str = '#B3261E'
    onError: str = '#FFFFFF'
    errorContainer: str = '#F9DEDC'
    onErrorContainer: str = '#410E0B'
    
    # Neutral Palette (Surface Tones)
    background: str = '#FFFBFE' 
    onBackground: str = '#1C1B1F'
    surface: str = '#FFFBFE'
    onSurface: str = '#1C1B1F'
    surfaceVariant: str = '#E7E0EC'
    onSurfaceVariant: str = '#49454F'
    outline: str = '#79747E'
    outlineVariant: str = '#CAC4D0' 
    
    shadow: str = '#000000'
    scrim: str = '#000000' 
    
    # Inverse Tones
    inverseSurface: str = '#313033'
    inverseOnSurface: str = '#F4EFF4'
    inversePrimary: str = '#D0BCFF'
    
    # Additional customizations
    activeTrackColor: Optional[str] = None
    activeColor: Optional[str] = None
    thumbColor: Optional[str] = None
    fillColor: Optional[str] = None

    # Meta
    brightness: str = "light"

    def to_css_vars(self) -> str:
        """Generates the CSS variable definitions for this theme."""
        lines = []
        for field_name, value in self.__dict__.items():
            if field_name == 'brightness': continue
            if value and isinstance(value, str):
                 # Convert camelCase to kebab-case
                css_name = "".join(["-" + c.lower() if c.isupper() else c for c in field_name])
                lines.append(f"    --md-sys-color-{css_name}: {value};")
        
        # Add basic aliases and usage
        # This maps the generic variable to the specific MD3 role
        lines.append(f"    --primary: var(--md-sys-color-primary);")
        lines.append(f"    --background: var(--md-sys-color-background);")
        lines.append(f"    --surface: var(--md-sys-color-surface);")
        
        # Add Dynamic Colors from Registry
        dynamic_colors = ThemeManager.instance().get_dynamic_colors()
        for dc in dynamic_colors:
            val = dc['light'] if self.brightness == 'light' else dc['dark']
            lines.append(f"    --{dc['name']}: {val};")

        return ":root {\n" + "\n".join(lines) + "\n}"

    @staticmethod
    def light():
        return ThemeData(brightness="light")

    @staticmethod
    def dark():
        return ThemeData(
            primary = '#D0BCFF',
            onPrimary = '#381E72',
            primaryContainer = '#4F378B',
            onPrimaryContainer = '#EADDFF',
            secondary = '#CCC2DC',
            onSecondary = '#332D41',
            secondaryContainer = '#4A4458',
            onSecondaryContainer = '#E8DEF8',
            tertiary = '#EFB8C8',
            onTertiary = '#492532',
            tertiaryContainer = '#633B48',
            onTertiaryContainer = '#FFD8E4',
            error = '#F2B8B5',
            onError = '#601410',
            errorContainer = '#8C1D18',
            onErrorContainer = '#F9DEDC',
            background = '#1C1B1F',
            onBackground = '#E6E1E5',
            surface = '#1C1B1F',
            onSurface = '#E6E1E5',
            surfaceVariant = '#49454F',
            onSurfaceVariant = '#CAC4D0',
            outline = '#938F99',
            outlineVariant = '#49454F',
            inverseSurface = '#E6E1E5',
            inverseOnSurface = '#313033',
            inversePrimary = '#6750A4',
            brightness="dark"
        )

# Global theme manager
class ThemeManager:
    _instance = None
    
    def __init__(self):
        self._current_theme = ThemeData.light()
        self._dynamic_colors = [] # List of dicts {name, light, dark}
        
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    @property
    def current_theme(self):
        return self._current_theme
    
    def set_theme(self, theme: ThemeData):
        self._current_theme = theme
        from .core import Framework
        if Framework._instance:
            Framework._instance.set_theme(theme)

    def register_dynamic_color(self, light_val: str, dark_val: str) -> str:
        """
        Registers a new dynamic color and returns a stable CSS variable name.
        Uses hashing to ensure the same color values produce the same variable name.
        """
        import hashlib
        
        # Generate a stable ID based on the values
        unique_str = f"{light_val}-{dark_val}"
        hash_id = hashlib.md5(unique_str.encode()).hexdigest()[:8]
        name = f"dynamic-{hash_id}"
        
        # Check if already registered to avoid duplicates in the list
        for dc in self._dynamic_colors:
            if dc['name'] == name:
                return f"var(--{name})"
                
        self._dynamic_colors.append({
            'name': name,
            'light': light_val,
            'dark': dark_val
        })
        
        # Trigger an update of the CSS to include the new variable
        # This ensures that the variable is defined before the browser tries to render it
        # We only do this if it's a NEW color
        from .core import Framework
        # Use set_theme to refresh the CSS logic
        # Optimize: Only do this if we are running (Framework initialized)
        if Framework._instance:
             # Defer or throttle could be better, but for now instant update is safer for correctness
             Framework._instance.set_theme(self.current_theme)
             
        return f"var(--{name})"
        
    def get_dynamic_colors(self):
        return self._dynamic_colors

