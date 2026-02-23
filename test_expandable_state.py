import os
import sys

# Define a mock window to avoid starting QtWebEngine and hanging
class MockWindow:
    def evaluate_js(self, js: str):
        pass
    def evaluate_js_with_callback(self, js: str, callback):
        pass

from pythra.core import Framework
from pythra.widgets import Widget, Container, Text, Column
from pythra.base import Key
from pythra.state import StatefulWidget, State
from pythra.widgets_more import Expandable

class MockHomePageState(State):
    def __init__(self):
        super().__init__()
        self.slider_val = 0
        
    def trigger_rebuild(self):
        print("\n--- TRIGGERING HOMEPAGE REBUILD ---")
        self.slider_val += 1
        self.setState()

    def build(self) -> Widget:
        return Column(
            key=Key("col"),
            children=[
                Text(f"Val: {self.slider_val}", key=Key("txt")),
                Expandable(
                    key=Key("expandable"),
                    initiallyExpanded=True,
                    header=Text("Header", key=Key("header")),
                    child=Text("Body", key=Key("body"))
                )
            ]
        )

class MockHomePage(StatefulWidget):
    def createState(self):
        return MockHomePageState()

def run_test():
    app = Framework.instance()
    app.window = MockWindow()
    app.set_root(MockHomePage(key=Key("home")))
    
    print("Initial render...")
    app._perform_initial_render()
    
    main_map = app.reconciler.get_map_for_context('main')
    expandable_state = main_map[Key("expandable")]['widget_instance'].get_state()
    print(f"After initial render, Expandable is_expanded = {expandable_state.is_expanded}")
    
    # Toggle it to False
    print("\n--- APP USER TOGGLES EXPANDABLE CAUSING SETSTATE ---")
    expandable_state.toggle()
    
    # Process reconciliation synchronously
    app._process_reconciliation()
    print(f"After toggle rebuild, Expandable is_expanded = {expandable_state.is_expanded}")
    
    # Trigger parent rebuild
    st = app.root_widget._state
    st.trigger_rebuild()
    
    # Process reconciliation synchronously
    app._process_reconciliation()
    
    # Fetch Expandable state again (might be a new instance if bug isn't fixed, but should be the same instance natively)
    expandable_state_2 = app.reconciler.get_map_for_context('main')[Key("expandable")]['widget_instance'].get_state()
    print(f"After parent rebuild, Expandable is_expanded = {expandable_state_2.is_expanded}")
    
    # Check if they are the exact same instance in memory
    print(f"Is same State instance? {expandable_state is expandable_state_2}")
    
    sys.exit(0)

if __name__ == "__main__":
    run_test()
