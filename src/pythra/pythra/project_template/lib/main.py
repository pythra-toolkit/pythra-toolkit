# main.py
import os
import sys
from typing import Union
from pythra.base import Key
from pythra.styles import BorderRadius, ButtonStyle, CrossAxisAlignment, EdgeInsets, TextStyle
from pythra.widgets import SizedBox

from pythra import (
    Framework,
    StatefulWidget,
    StatelessWidget,
    State,
    Column,
    Colors,
    Row,
    Text,
    Center,
    IconButton,
    Icon,
    Icons,
    Container,
    MainAxisAlignment,
)


# ---------------------------------------------------------------------------
# App Initialization Wrapper
# ---------------------------------------------------------------------------
def runApp(rootWidget: Union[StatefulWidget, StatelessWidget]):
    """
    A convenient class decorator that automatically initializes the PyThra
    framework, sets the decorated widget as the root of your application tree,
    and runs the application loop.
    
    Usage:
        @runApp
        class MyApp(StatefulWidget):
            ...
    """
    app = Framework.instance()
    app.set_root(rootWidget())  # Instantiates your root widget
    app.run()
    return rootWidget


# ---------------------------------------------------------------------------
# State (Your Logic and Variables)
# ---------------------------------------------------------------------------
class CounterState(State):
    """
    The State class holds mutable data for a StatefulWidget. It persists across
    UI rebuilds. When data here changes, calling self.setState() tells PyThra
    that the UI needs to be re-rendered to reflect the new state.
    """
    def __init__(self):
        super().__init__()
        self.count = 0  # This variable controls what displays on the counter

    def increment(self):
        self.count += 1
        self.setState()  # Signals PyThra to call build() and update the DOM

    def decrement(self):
        self.count -= 1
        self.setState()  # Signals PyThra to call build() and update the DOM

    # -----------------------------------------------------------------------
    # UI Layout (Your Declarative UI Tree)
    # -----------------------------------------------------------------------
    def build(self):
        """
        The build method returns the widget tree for this state.
        
        It is called automatically during initialization and every time 
        self.setState() is invoked. Only the parts of the tree that have 
        changed will be updated on the screen, thanks to PyThra's Virtual DOM.
        
        Important: Always assign a unique 'key' to widgets to ensure optimal
        re-rendering and state preservation.
        """
        return Container(
            key=Key("root_container"),
            height="100vh",
            width="100vw",
            color=Colors.background,
            padding=EdgeInsets.all(20),
            child=Center(
                key=Key("counter_app"),
                child=Column(
                    key=Key("counter_column"),
                    mainAxisAlignment=MainAxisAlignment.SPACE_BETWEEN,
                    crossAxisAlignment=CrossAxisAlignment.CENTER,
                    children=[
                        # --- App Title ---
                        Text(
                            "Simple Counter App",
                            key=Key("title_text"),
                            style=TextStyle(fontSize=24, fontWeight="bold"),
                        ),
                        SizedBox(height=20, key=Key("spacer_1")),
                        
                        # --- State Display ---
                        Text(
                            f"Count: {self.count}",
                            key=Key("count_text"),
                            style=TextStyle(fontSize=20, fontFamily="monospace"),
                        ),
                        SizedBox(height=20, key=Key("spacer_2")),
                        
                        # --- Interactive Buttons ---
                        Row(
                            key=Key("counter_row"),
                            mainAxisAlignment=MainAxisAlignment.CENTER,
                            children=[
                                # Decrease button
                                IconButton(
                                    key=Key("decrease_button"),
                                    icon=Icon(Icons.stat_minus_1_rounded),
                                    onPressed=self.decrement,
                                    style=ButtonStyle(
                                        backgroundColor=Colors.primary,
                                        foregroundColor=Colors.onPrimary,
                                        hoverColor=Colors.primaryContainer,
                                        padding=EdgeInsets.symmetric(
                                            horizontal=15, vertical=10
                                        ),
                                        shape=BorderRadius.circular(5),
                                    ),
                                ),
                                SizedBox(width=20, key=Key("spacer_3")),
                                
                                # Increase button
                                IconButton(
                                    key=Key("increase_button"),
                                    icon=Icon(Icons.stat_1_rounded),
                                    onPressed=self.increment,
                                    style=ButtonStyle(
                                        backgroundColor=Colors.primary,
                                        foregroundColor=Colors.onPrimary,
                                        hoverColor=Colors.primaryContainer,
                                        padding=EdgeInsets.symmetric(
                                            horizontal=15, vertical=10
                                        ),
                                        shape=BorderRadius.circular(5),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )


# ---------------------------------------------------------------------------
# Root Widget Wrapper
# ---------------------------------------------------------------------------
@runApp
class CounterApp(StatefulWidget):
    """
    The root widget of the application. 
    StatefulWidgets delegate their rendering and logic to a paired State class.
    The @runApp decorator mounts this widget to the DOM automatically.
    """
    def __init__(self, key=Key("counter_app_root_widget")):
        super().__init__(key=key)
    
    def createState(self):
        """Creates the mutable state for this widget at a given location in the tree."""
        return CounterState()
