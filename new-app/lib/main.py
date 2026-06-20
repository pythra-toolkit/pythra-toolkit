import os
from pathlib import Path
import sys
import json
from typing import Optional, Union

from pythra.widgets import TextButton
from pythra.widgets_more import Align

from pythra import (
    Framework,
    StatefulWidget,
    StatelessWidget,
    State,
    Column,
    Row,
    Key,
    Widget,
    Container,
    Text,
    Alignment,
    Colors,
    Center,
    ElevatedButton,
    SizedBox,
    MainAxisAlignment,
    CrossAxisAlignment,
    ClipPath,
    EdgeInsets,
    Icon,
    IconButton,
    Icons,
    ButtonStyle,
    TextStyle,
    Stack,
    Positioned,
    GradientTheme,
    BoxConstraints,
    BoxDecoration,
    BorderRadius,
    BorderSide,
    Switch,
    VirtualGridView,
    VirtualGridController,
    VirtualListView,
    VirtualListController,
    Slider,
    SliderController,
    TextField,
    TextEditingController,
    InputDecoration,
    GestureDetector,
    PanUpdateDetails,
    Dropdown,
    DropdownMenuItem,
    DropdownTheme,
    VirtualDropdownController,
    VirtualDropdownTheme,
    VirtualDropdown,
    FutureBuilder,
    ConnectionState,
    Scrollbar,
    ResponsiveBuilder,
    GradientBorderContainer,
)
from pythra.controllers import DropdownController
from pythra.styles import (
    BorderSide,
    BorderRadius,
    Colors,
    EdgeInsets,
    GradientBorderTheme,
    ScrollbarTheme,
    TextStyle,
    VerticalDirection,
    Offset,
)


def runApp(rootWidget):
    app = Framework.instance()
    app.set_root(rootWidget())
    app.run()
    return rootWidget


class HomePageState(State):
    def __init__(self):
        super().__init__()
        self.vlist_ctrl = VirtualListController()
        self.vgrid_ctrl = VirtualGridController()

    def build_list_item(self, index: int) -> Widget:
        return Container(
            key=Key(f"vlist_item_{index}"),
            height=50,
            padding=EdgeInsets.symmetric(horizontal=16, vertical=8),
            decoration=BoxDecoration(
                color=Colors.hex("#363636") if index % 2 == 0 else Colors.transparent,
                borderRadius=BorderRadius.all(8),
            ),
            child=Center(
                key=Key(f"vlist_item_center_{index}"),
                child=Text(
                    f"List Item {index + 1}",
                    style=TextStyle(fontSize=16, color=Colors.hex("#D9D9D9")),
                    key=Key(f"vlist_item_text_{index}"),
                ),
            ),
        )

    def build_grid_item(self, index: int) -> Widget:
        return Container(
            key=Key(f"vgrid_item_{index}"),
            decoration=BoxDecoration(
                color=Colors.hex("#4A4A4A"),
                borderRadius=BorderRadius.all(8),
            ),
            child=Center(
                child=Text(
                    str(index + 1),
                    style=TextStyle(fontSize=20, color=Colors.hex("#FFFFFF")),
                    key=Key(f"vgrid_item_text_{index}"),
                ),
            ),
        )

    def build(self) -> Widget:
        return Container(
            key=Key("test_root"),
            height="100vh",
            width="100vw",
            color=Colors.hex("#1E1E1E"),
            padding=EdgeInsets.all(16),
            child=Row(
                key=Key("test_row"),
                mainAxisAlignment=MainAxisAlignment.SPACE_EVENLY,
                crossAxisAlignment=CrossAxisAlignment.START,
                children=[
                    Container(
                        key=Key("vlist_section"),
                        width="45%",
                        height="90vh",
                        decoration=BoxDecoration(
                            color=Colors.hex("#2D2D2D"),
                            borderRadius=BorderRadius.all(12),
                        ),
                        padding=EdgeInsets.all(8),
                        child=Column(
                            key=Key("vlist_col"),
                            children=[
                                Text(
                                    "VirtualListView",
                                    style=TextStyle(
                                        fontSize=18,
                                        color=Colors.hex("#FFFFFF"),
                                        fontWeight="bold",
                                    ),
                                    key=Key("vlist_title"),
                                ),
                                SizedBox(height=8),
                                Container(
                                    key=Key("vlist_wrapper"),
                                    height="calc(90vh - 60px)",
                                    width="100%",
                                    child=VirtualListView(
                                        key=Key("test_vlist"),
                                        controller=self.vlist_ctrl,
                                        itemCount=1000,
                                        itemBuilder=self.build_list_item,
                                        itemExtent=50,
                                        height="inherit",
                                        width="100%",
                                        initialItemCount=20,
                                    ),
                                ),
                            ],
                        ),
                    ),
                    Container(
                        key=Key("vgrid_section"),
                        width="45%",
                        height="90vh",
                        decoration=BoxDecoration(
                            color=Colors.hex("#2D2D2D"),
                            borderRadius=BorderRadius.all(12),
                        ),
                        padding=EdgeInsets.all(8),
                        child=Column(
                            key=Key("vgrid_col"),
                            children=[
                                Text(
                                    "VirtualGridView",
                                    style=TextStyle(
                                        fontSize=18,
                                        color=Colors.hex("#FFFFFF"),
                                        fontWeight="bold",
                                    ),
                                    key=Key("vgrid_title"),
                                ),
                                SizedBox(height=8),
                                Container(
                                    key=Key("vgrid_wrapper"),
                                    height="calc(90vh - 60px)",
                                    width="100%",
                                    child=VirtualGridView(
                                        key=Key("test_vgrid"),
                                        controller=self.vgrid_ctrl,
                                        itemCount=500,
                                        itemBuilder=self.build_grid_item,
                                        crossAxisCount=3,
                                        childAspectRatio=1.0,
                                        mainAxisSpacing=8,
                                        crossAxisSpacing=8,
                                        initialItemCount=30,
                                        height="inherit",
                                        width="100%",
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )


class HomePage(StatefulWidget):
    def createState(self) -> HomePageState:
        return HomePageState()


class MainState(State):
    def __init__(self):
        self.home_page = HomePage(key=Key("home_page"))

    def build(self):
        return self.home_page


@runApp
class Main(StatefulWidget):
    def __init__(self, key=Key("home_page_wrapper")):
        super().__init__(key=key)

    def createState(self) -> MainState:
        return MainState()


if __name__ == "__main__":
    app = Framework.instance()
    app.set_root(HomePage(key=Key("home_page_wrapper")))
    app.run()
