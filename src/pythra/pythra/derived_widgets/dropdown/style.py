from pythra.styles import *

# ==============================================================================
# 1. THEME (The Data and Style Models)
# ==============================================================================


class VirtualDropdownTheme:
    """Encapsulates the styling properties for the VirtualDropdown widget.

    The trigger button appearance is controlled by `inputDecoration`, which
    mirrors the same InputDecoration object used by TextField.  All other
    properties govern the drop-down menu panel itself.
    """

    def __init__(
        self,
        # ── Trigger button appearance (InputDecoration) ──────────────────────
        inputDecoration: Optional[InputDecoration] = None,
        # ── Legacy flat overrides (kept for back-compat; ignored when
        #    inputDecoration is provided) ──────────────────────────────────────
        backgroundColor=Colors.hex("#dedede"),
        borderColor=Colors.hex("#AAAAAA"),
        width=300,
        borderWidth=1.0,
        borderRadius=8.0,
        textColor=Colors.hex("#000000"),
        fontSize=14.0,
        padding=EdgeInsets.symmetric(vertical=8, horizontal=12),
        # ── Drop-down menu panel ─────────────────────────────────────────────
        dropdownColor=Colors.hex("#dedede"),
        dropdownTextColor=Colors.hex("#000000"),
        selectedItemColor=Colors.hex("#a0a0c3"),
        selectedItemShape=BorderRadius.all(4),
        dropdownMargin=EdgeInsets.only(top=12),
        dropdownHeight=200,
        itemPadding=EdgeInsets.symmetric(horizontal=12, vertical=8),
    ):
        # ── InputDecoration (primary trigger styling) ──────────────────────
        self.inputDecoration = inputDecoration  # may be None

        # ── Legacy flat props ───────────────────────────────────────────────
        self.backgroundColor = backgroundColor
        self.borderColor = borderColor
        self.width = width
        self.borderWidth = borderWidth
        self.borderRadius = borderRadius
        self.textColor = textColor
        self.fontSize = fontSize
        self.padding = padding

        # ── Menu panel props ────────────────────────────────────────────────
        self.dropdownColor = dropdownColor
        self.dropdownTextColor = dropdownTextColor
        self.selectedItemColor = selectedItemColor
        self.selectedItemShape = selectedItemShape
        self.dropdownMargin = dropdownMargin
        self.dropdownHeight = dropdownHeight
        self.itemPadding = itemPadding
