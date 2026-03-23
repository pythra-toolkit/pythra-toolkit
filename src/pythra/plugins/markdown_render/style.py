class RendererStyle:
    """
    CSS Styling options for the Markdown Render widget.
    """
    def __init__(
        self,
        color: str = "inherit",
        font_family: str = "inherit",
        font_size: str = "16px",
        padding: str = "16px",
        background_color: str = "transparent",
        custom_css: dict = None
    ):
        self.color = color
        self.font_family = font_family
        self.font_size = font_size
        self.padding = padding
        self.background_color = background_color
        self.custom_css = custom_css or {}

    def to_dict(self):
        style_dict = {
            "color": self.color,
            "fontFamily": self.font_family,
            "fontSize": self.font_size,
            "padding": self.padding,
            "backgroundColor": self.background_color
        }
        style_dict.update(self.custom_css)
        return style_dict
