"""
PyThra Markdown Render Plugin
A high-performance Markdown render widget plugin for Pythra
"""

from .widget import MarkdownRender

__version__ = "1.0.0"
__all__ = ['MarkdownRender']

# Plugin definition for Pythra framework
plugin_definition = {
    'name': 'pythra-markdown-render',
    'version': __version__,
    'js_modules': {
        'PythraMarkdownRender': {
            'file': 'js/marked_engine.js',
            'global': 'pythraMarkdownRender',
            'initializer': 'initialize'
        }
    }
}
