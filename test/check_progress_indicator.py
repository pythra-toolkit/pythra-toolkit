import os
import sys

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src/pythra')))

from pythra.styles import Loader, LoaderStyle
from pythra.widgets_more import ProgressIndicator
from pythra.controllers import ProgressIndicatorController

def test_progress_indicator():
    print("Testing ProgressIndicator...")
    
    # 1. Test Controller
    controller = ProgressIndicatorController()
    assert controller.visible == True
    controller.hide()
    assert controller.visible == False
    controller.show()
    assert controller.visible == True
    print("Controller tests passed.")

    # 2. Test Widget & CSS Generation
    # Use a knwon loader type
    loader = Loader.ARCADE
    style = LoaderStyle.LOADER_ARCADE_1
    
    widget = ProgressIndicator(loader=loader, style=style, controller=controller)
    
    props = widget.render_props()
    print("Props:", props)
    # The injection marker class (css_class) is no longer used for file loading
    # We now verify _js_init
    
    # assert props['class'] == style.value
    # assert props['css_class'] == "injected-" + loader.value
    
    print("Props keys:", props.keys())
    assert props['class'] == style.value
    assert '_js_init' in props
    js_init = props['_js_init']
    assert js_init['engine'] == 'PythraProgressIndicator'
    assert js_init['loader'] == loader.value
    assert js_init['visible'] == True
    
    print("JS Init check passed.")
    
    # We no longer test generate_css_rule as it is removed

    print("ProgressIndicator tests finished.")

if __name__ == "__main__":
    test_progress_indicator()
