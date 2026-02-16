import sys
import os

# Ensure we can import pythra
sys.path.insert(0, os.path.join(os.getcwd(), "src/pythra"))

# Explicit imports to avoid wildcard issues
from pythra.base import Key, Widget
from pythra.core import Framework
from pythra.state import State, StatefulWidget
from pythra.widgets import (
    Text, Container, Column, Expanded, Center, Scaffold, VirtualGridView
)
from pythra.styles import TextStyle, BoxDecoration, BorderRadius, Colors
from pythra.controllers import VirtualGridController

class MyVirtualGridApp(StatefulWidget):
    def __init__(self, key=None):
        super().__init__(key=key)

    def createState(self):
        return _MyVirtualGridAppState()

class _MyVirtualGridAppState(State):
    def __init__(self):
        super().__init__()
        self.controller = VirtualGridController()

    def build(self):
        return Scaffold(
            body=Column(
                children=[
                    Container(height=50, child=Text("Virtual Grid View Demo", style=TextStyle(fontSize=24, fontWeight="bold"))),
                    Expanded(
                        child=VirtualGridView(
                            key=Key("my_virtual_grid"),
                            controller=self.controller,
                            itemCount=1000,
                            crossAxisCount=3,
                            mainAxisSpacing=10,
                            crossAxisSpacing=10,
                            childAspectRatio=1.0,
                            itemBuilder=self.item_builder
                        )
                    )
                ]
            )
        )

    def item_builder(self, index):
        return Container(
            key=Key(f"grid_item_{index}"),
            decoration=BoxDecoration(
                color=Colors.blue if index % 2 == 0 else Colors.red,
                borderRadius=BorderRadius.all(8)
            ),
            child=Center(
                child=Text(f"Item {index}", style=TextStyle(color="white"))
            )
        )

def main():
    app = Framework.instance()
    if hasattr(app, 'set_root'):
        app.set_root(MyVirtualGridApp(key=Key("root_app")))
    else:
        app.root_widget = MyVirtualGridApp(key=Key("root_app"))

    app.run(
        title="Virtual Grid Verification",
        width=1200,
        height=800
    )

if __name__ == "__main__":
    main()
