from pythra.styles import *

# ==============================================================================
# 1. THEME (The Data and Style Models)
# ==============================================================================



class DerivedDropdownTheme:
    """Encapsulates the styling properties for the DerivedDropdown widget menu and specific attributes not covered by InputDecoration."""

    def __init__(
        self,
        width=100,
        dropdownColor=Colors.hex("#FFFFFF"),
        dropdownTextColor=Colors.hex("#000000"),
        selectedItemColor=Colors.hex("#E0E0E0"),
        selectedItemShape= BorderRadius.all(4),
        dropdownMargin=EdgeInsets.only(top=45),
        dropdownHeight=500,
        itemPadding = EdgeInsets.symmetric(horizontal=12, vertical=8),
    ):
        self.width = width
        self.dropdownColor = dropdownColor
        self.dropdownTextColor = dropdownTextColor
        self.selectedItemColor = selectedItemColor
        self.selectedItemShape = selectedItemShape
        self.dropdownMargin = dropdownMargin
        self.dropdownHeight = dropdownHeight
        self.itemPadding = itemPadding