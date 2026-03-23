from pythra import StatefulWidget, Key, Widget
from .renderer_state import MarkdownRendererState
from .style import RendererStyle
from .controller import MarkdownRendererController

class MarkdownRender(StatefulWidget):
    """
    High-performance Markdown Render widget for Pythra
    Uses marked.js and highlight.js to render Markdown efficiently in the frontend.
    """
    def __init__(
        self,
        key: Key,
        markdown_text: str = "",
        controller: MarkdownRendererController = None,
        width: str = "100%",
        height: str = "auto",
        style: RendererStyle = None
    ):
        self.markdown_text = markdown_text
        self.controller = controller
        self.width = width
        self.height = height
        self.style = style if style else RendererStyle()
        super().__init__(key=key)

    def createState(self):
        return MarkdownRendererState()
