import os
import sys
import json
from typing import Optional, Union

# Add the project root directory to Python path
# (No longer necessary, PyThra handles this automatically)

# removed local imports

# Welcome to your new Pythra App!
from pythra import (
    # app,
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
    ClipBehavior,
    GradientTheme,
    ProgressIndicator,
    ProgressIndicatorController,
    Loader,
    LoaderStyle,
    BarsProgressIndicator,
    ThreeDLoader,
    BoxConstraints,
    BoxDecoration,
    BorderRadius,
    BorderSide,
    Divider,
    Switch,
    Transform,
    Matrix4,
    VirtualGridView,
    VirtualGridController,
    VirtualListView,
    VirtualListController,
    ClipPath,
    Slider,
    SliderController,
    TextField,
    TextEditingController,
    InputDecoration,
    Expandable,
    ExpandableTheme,
    GestureDetector,
    PanUpdateDetails,
    Dropdown,
    DropdownMenuItem,
    DropdownTheme,
    VirtualDropdownController,
    VirtualDropdownTheme,
    VirtualDropdown,
    Switch,
    FutureBuilder,
    ConnectionState,
    background_task,
    ui_thread,
)

from pythra.controllers import DropdownController
from pythra.styles import (
    BorderSide,
    BorderRadius,
    Colors,
    EdgeInsets,
    TextStyle,
    VerticalDirection,
    Offset,
)


def runApp(rootWidget: Union[StatefulWidget, StatelessWidget]):
    """
    A decorator that instantiates the decorated widget class
    and runs the PyThra app with it.
    """
    app = Framework.instance()
    app.set_root(rootWidget())  # Instantiate the class before setting it as root
    app.run()
    return rootWidget


class FutureState(State):
    def __init__(self):
        super().__init__()

    def fetch_data(self):
        # Simulate a blocking IO-bound call
        import time

        time.sleep(0.1)  # Simulate delay
        print("fetch_data completed!")
        return "Hello from FutureBuilder!"

    def build(self) -> Widget:
        return FutureBuilder(
            key=Key("future_builder_demo"),
            future=self.fetch_data,
            initialData="Initial data before future completes",
            builder=lambda context, snapshot: (
                Text(
                    f"Result: {snapshot.data}",
                    key=Key(f"fb_result_{snapshot.data}"),
                )
            ),
        )


class Future(StatefulWidget):
    def createState(self) -> FutureState:
        return FutureState()


class HomePageState(State):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.async_status = "Standby"
        self.slider_controller = SliderController(value=50.0)
        self.text_controller = TextEditingController(text="")
        self.text_controller.add_listener(self.on_text_changed_internal)
        self.drag_offset = Offset(0, 0)
        self.vlist_controller = VirtualListController()
        self.is_expanded = True
        self.val = True
        self.dropdown_controller = DropdownController(selectedValue="Option 1")
        self.derived_dropdown_controller = VirtualDropdownController(
            value="Apple",
            items=[
                "Apple",
                "Banana",
                "Cherry",
                "Date",
                "d",
                "Applevv",
                "Bavnana",
                "Chevrry",
                "Dvate",
                "Applaae",
                "Banaana",
                "Cherrya",
                "Datae",
                "ad",
                "Apaplevv",
                "Baavnana",
                "Cheavrry",
                "Dvaate",
                "sBaavnana",
                "ssCheavrry",
                "Dsvaate",
            ],
        )
        self.derived_dropdown_controller_2 = VirtualDropdownController(
            value="Apple",
            items=[
                "Apple",
                "Banana",
                "Cherry",
                "Date",
                "d",
                "Applevv",
                "Bavnana",
                "Chevrry",
                "Dvate",
                "Applaae",
                "Banaana",
                "Cherrya",
                "Datae",
                "ad",
                "Apaplevv",
                "Baavnana",
                "Cheavrry",
                "Dvaate",
                "sBaavnana",
                "ssCheavrry",
                "Dsvaate",
            ],
        )
        # self.font_controller = DropdownController(selectedValue=SYSTEM_FONTS[0]["val"] if SYSTEM_FONTS else "Arial")

    def tog(self, t):
        self.val = not self.val
        self.setState()

    def on_pan_update(self, details: PanUpdateDetails):
        self.drag_offset = Offset(
            self.drag_offset.dx + details.dx, self.drag_offset.dy + details.dy
        )
        self.setState()

    def on_dropdown_changed(self, new_value):
        self.dropdown_controller.selectedValue = new_value
        self.setState()

    def on_font_changed(self, new_value):
        self.font_controller.selectedValue = new_value
        self.setState()

    def on_text_changed_internal(self):
        self.setState()

    def fetch_data(self):
        # Simulate a blocking IO-bound call
        import time

        time.sleep(5)  # Simulate delay
        print("fetch_data completed!")
        return "Hello from FutureBuilder!"

    def run_async_test(self):
        self.async_status = "Running async task..."
        self.setState()

        def slow_task():
            import time

            time.sleep(2)
            return "✅ Async Task Done!"

        def on_done(res):
            self.async_status = res
            self.setState()

        self.runAsync(slow_task, on_done)

    @background_task
    def decorator_test_fetch(self):
        print("Executing @background_task...")
        self._update_status_ui("Decorator running...")

        import time
        time.sleep(2)

        print("Finished @background_task wait, calling @ui_thread...")
        self.decorator_test_done("✅ Decorators connected!")

    @ui_thread
    def _update_status_ui(self, status):
        self.async_status = status
        self.setState()

    @ui_thread
    def decorator_test_done(self, result):
        self.async_status = result
        self.setState()

    async def qasync_test(self):
        self.async_status = "Running native async handler..."
        self.setState() # Safe: runs on main thread

        import asyncio
        await asyncio.sleep(2) # Yields control to Qt Event Loop without blocking UI!

        self.async_status = "✅ Native await finished!"
        self.setState() # Also safe!

    def vlist_item_builder(self, index: int) -> Widget:
        return Container(
            key=Key(f"vlist_item_{index}"),
            height=60,
            padding=EdgeInsets.symmetric(horizontal=16, vertical=8),
            decoration=BoxDecoration(
                color=Colors.surfaceVariant,
                borderRadius=BorderRadius.all(8),
            ),
            child=Center(
                key=Key(f"vlist_item_center_{index}"),
                child=Text(
                    f"List Item {index + 1}",
                    style=TextStyle(fontSize=16, color=Colors.onSurfaceVariant),
                    key=Key(f"vlist_item_text_{index}"),
                ),
            ),
        )

    def on_slider_changed(self, new_value: float):
        self.slider_controller.value = new_value
        self.setState()

    @property
    def is_dark(self):
        return Framework.instance().theme.brightness == "dark"

    def toggle_theme(self):
        new_theme = "light" if self.is_dark else "dark"
        Framework.instance().set_theme(new_theme)
        # Rebuild this row to update all icons (Sun/Moon, Sparkle, etc)
        self.setState()

    def toggle(self, *args, **kwargs):
        print("Toggling expandable state...")
        print(args, kwargs)
        self.is_expanded = not self.is_expanded
        print(f"is_expanded: {self.is_expanded}")
        self.setState()

    def build(self) -> Widget:
        return Container(
            key=Key("home_page_Pythra_wrapper_container"),
            height="100vh",
            width="100vw",
            color=Colors.background,
            child=Center(
                key=Key("home_page_Pythra_center"),
                child=Container(
                    constraints=BoxConstraints(
                        minWidth=500,
                    ),
                    width=800,
                    height="80vh",
                    padding=EdgeInsets.all(20),
                    decoration=BoxDecoration(
                        color=Colors.background,
                        borderRadius=BorderRadius.all(20),
                        border=BorderSide(
                            width=1,
                            color=Colors.adaptive(dark="#5a5a5a", light="#d3d3d3"),
                        ),
                    ),
                    key=Key("body_card"),
                    child=Column(
                        key=Key("body_column"),
                        crossAxisAlignment=CrossAxisAlignment.STRETCH,
                        children=[
                            Container(
                                key=Key("run_async_demo_box"),
                                padding=EdgeInsets.all(16),
                                decoration=BoxDecoration(
                                    color=Colors.surfaceVariant,
                                    borderRadius=BorderRadius.circular(8),
                                ),
                                child=Column(
                                    key=Key("run_async_demo_column"),
                                    children=[
                                        Text(
                                            f"run_async State: {self.async_status}",
                                            style=TextStyle(fontSize=16, color=Colors.onSurfaceVariant),
                                            key=Key("run_async_status_text"),
                                        ),
                                        SizedBox(height=10, key=Key("space_async_btn")),
                                        Row(
                                            key=Key("async_buttons_row"),
                                            mainAxisAlignment=MainAxisAlignment.CENTER,
                                            children=[
                                                ElevatedButton(
                                                    key=Key("btn_run_async"),
                                            child=Text(
                                                "Test State.run_async()",
                                                key=Key("btn_txt_run_async"),
                                            ),
                                                    onPressed=self.run_async_test,
                                                ),
                                                SizedBox(width=10, key=Key("space_between_async_btns")),
                                                ElevatedButton(
                                                    key=Key("btn_test_decorators"),
                                                    child=Text("Test @background_task",key=Key("btn_txt_test_decorators"),),
                                                    onPressed=self.decorator_test_fetch,
                                                ),
                                                SizedBox(width=10, key=Key("space_between_qasync_btns")),
                                                ElevatedButton(
                                                    key=Key("btn_test_qasync"),
                                                    child=Text("Test async/await",key=Key("btn_txt_test_qasync"),),
                                                    onPressed=self.qasync_test,
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                            ),
                            SizedBox(height=20, key=Key("space_after_async")),
                            Text(
                                f"Slider Value: {self.slider_controller.value:.2f} | Text: {self.text_controller.text}",
                                style=TextStyle(fontSize=24, color=Colors.onBackground),
                                key=Key("slider_text"),
                            ),
                            SizedBox(height=40, key=Key("slider_space")),
                            TextField(
                                key=Key("my_textfield"),
                                controller=self.text_controller,
                                # enabled=False,
                                # obscureText=True,
                                leading=Icon(
                                    Icons.person,
                                    key=Key("tf_icon_lead"),
                                    color=Colors.onSurfaceVariant,
                                ),
                                trailing=IconButton(
                                    key=Key("tf_icon_trail"),
                                    icon=Icon(Icons.search, key=Key("sh_ic")),
                                    onPressed=lambda: (
                                        print(f"Search! {self.text_controller.text}"),
                                        self.setState(),
                                    ),
                                ),
                                decoration=InputDecoration(
                                    label="Username",
                                    hintText="Enter your chosen name...",
                                    fillColor=Colors.surfaceVariant,
                                    labelColor=Colors.onSurfaceVariant,
                                    focusColor=Colors.primary,
                                    borderRadius=BorderRadius.only(
                                        topLeft=12, topRight=12
                                    ),
                                    border=BorderSide(width=2, color=Colors.outline),
                                    focusedBorder=BorderSide(
                                        width=2, color=Colors.primary
                                    ),
                                    # contentPadding=EdgeInsets.symmetric(
                                    #     horizontal=24, vertical=16
                                    # ),
                                    labelStyle=TextStyle(
                                        fontSize=18, fontFamily="Arial"
                                    ),
                                    hintStyle=TextStyle(fontSize=14),
                                    filled=False,
                                ),
                            ),
                            SizedBox(height=20, key=Key("future_builder_demo_space")),
                            Future(key="not_past"),
                            SizedBox(height=20, key=Key("textfield_space")),
                            Slider(
                                key=Key("my_slider"),
                                controller=self.slider_controller,
                                onChanged=self.on_slider_changed,
                                min=0,
                                max=100,
                                divisions=10000,
                            ),
                            # Expandable(
                            #     initiallyExpanded=True,#self.is_expanded,
                            #     key=Key("my_expandable_test"),
                            #     header=Text(
                            #         "Tap to Expand/Collapse Me",
                            #         style=TextStyle(
                            #             fontWeight="bold", color=Colors.onSurfaceVariant
                            #         ),
                            #         key=Key("expandable_header_text"),
                            #     ),
                            #     verticalDirection=VerticalDirection.DOWN,
                            #     # onToggle=self.toggle,
                            #     theme=ExpandableTheme(
                            #         headerPadding=EdgeInsets.all(16),
                            #         headerDecoration=BoxDecoration(
                            #             color=Colors.surfaceVariant,
                            #             borderRadius=BorderRadius.circular(8),
                            #         ),
                            #         bodyPadding=EdgeInsets.all(16),
                            #         bodyDecoration=BoxDecoration(
                            #             color=Colors.background,
                            #         ),
                            #         iconColor=Colors.blue,
                            #     ),
                            #     child=Text(
                            #         "This is the hidden content! It animated smoothly via CSS grid.",
                            #         style=TextStyle(color=Colors.onBackground),
                            #         key=Key("expandable_child_text"),
                            #     ),
                            # ),
                            # SizedBox(height=20, key=Key("space_before_drag")),
                            # Switch(
                            #     key=Key("my_switch"),
                            #     value=self.val,
                            #     onChanged=self.tog
                            # ),
                            # SizedBox(height=20, key=Key("space_before_dropdowns")),
                            # Dropdown(
                            #     key=Key("test_dropdown"),
                            #     controller=self.dropdown_controller,
                            #     onChanged=self.on_dropdown_changed,
                            #     items=[
                            #         DropdownMenuItem(
                            #             key=Key("ddi_1"),
                            #             value="Option 1",
                            #             label="Option 1",
                            #             child=Text(
                            #                 "Option 1 (Arial Bold)",
                            #                 style=TextStyle(fontFamily="Arial", fontWeight="bold", color=Colors.primary),
                            #                 key=Key("ddi_1_text")
                            #             )
                            #         ),
                            #         DropdownMenuItem(
                            #             key=Key("ddi_2"),
                            #             value="Option 2",
                            #             label="Option 2",
                            #             child=Row(
                            #                 key=Key("ddi_2_row"),
                            #                 children=[
                            #                     Icon(Icons.star, key=Key("ddi_2_icon"), color=Colors.orange),
                            #                     SizedBox(width=8, key=Key("ddi_2_space")),
                            #                     Text("Option 2 (Courier New)", style=TextStyle(fontFamily="Courier New"), key=Key("ddi_2_text"))
                            #                 ],
                            #                 crossAxisAlignment=CrossAxisAlignment.CENTER
                            #             )
                            #         ),
                            #         DropdownMenuItem(
                            #             key=Key("ddi_3"),
                            #             value="Option Disabled",
                            #             disabled=True,
                            #             label="Option Disabled",
                            #             child=Text(
                            #                 "Option 3 (Disabled item)",
                            #                 key=Key("ddi_3_text")
                            #             )
                            #         ),
                            #         ("Option 4 - Standard text item", "Option 4"),
                            #     ],
                            #     decoration=InputDecoration(
                            #         label="Standard Dropdown",
                            #         hintText="Select an option...",
                            #         fillColor=Colors.surfaceVariant,
                            #         labelColor=Colors.onSurfaceVariant,
                            #         focusColor=Colors.primary,
                            #         borderRadius=BorderRadius.all(12),
                            #         border=BorderSide(width=2, color=Colors.outline),
                            #         focusedBorder=BorderSide(
                            #             width=2, color=Colors.primary
                            #         ),
                            #         labelStyle=TextStyle(
                            #             fontSize=18, fontFamily="Arial"
                            #         ),
                            #         hintStyle=TextStyle(fontSize=14),
                            #         filled=False,
                            #     ),
                            #     theme=DropdownTheme(
                            #         dropdownMargin=EdgeInsets.only(top=12),
                            #         elevation=12,
                            #         hoverColor=Colors.rgba(100, 255, 100, 0.2), # Testing hover theme overriding
                            #         menuPadding=EdgeInsets.symmetric(vertical=8),
                            #         itemMargin=EdgeInsets.symmetric(vertical=4, horizontal=4),
                            #         selectedItemShape=BorderRadius.all(8),
                            #         selectedItemColor=Colors.rgba(0, 100, 255, 0.1),
                            #     ),
                            # ),
                            # SizedBox(height=20, key=Key("space_between_dropdowns")),
                            # Text("System Font Picker", style=TextStyle(fontSize=16)),
                            # SizedBox(height=8, key=Key("space_before_font_dropdown")),
                            # Dropdown(
                            #     key=Key("system_font_dropdown"),
                            #     controller=self.font_controller,
                            #     onChanged=self.on_font_changed,
                            #     decoration=InputDecoration(
                            #         label="Select a Font",
                            #         border=BorderSide(width=1, color=Colors.outline),
                            #         borderRadius=BorderRadius.all(8),
                            #         contentPadding=EdgeInsets.symmetric(horizontal=12, vertical=12),
                            #         filled=False,
                            #     ),
                            #     theme=DropdownTheme(
                            #         dropDownHeight="300px",
                            #         dropdownMargin=EdgeInsets.only(top=8),
                            #         elevation=6,
                            #     ),
                            #     items=[
                            #         DropdownMenuItem(
                            #             key=Key(f"font_item_{idx}"),
                            #             value=f["val"],
                            #             label=f["label"],
                            #             child=Text(f["label"], style=TextStyle(fontFamily=f["val"], fontSize=18), key=Key(f"font_text_{idx}"))
                            #         )
                            #         for idx, f in enumerate(SYSTEM_FONTS)
                            #     ]
                            # ),
                            # SizedBox(height=20, key=Key("space_after_font_dropdown")),
                            # Text(
                            #     "The quick brown fox jumps over the lazy dog.",
                            #     style=TextStyle(
                            #         fontFamily=self.font_controller.selectedValue,
                            #         fontSize=24,
                            #         color=Colors.primary
                            #     ),
                            #     key=Key("font_preview_text")
                            # ),
                            # SizedBox(height=40, key=Key("space_after_font_preview")),
                            # VirtualDropdown(
                            #     key=Key("test_derived_dropdown"),
                            #     controller=self.derived_dropdown_controller,
                            #     onChanged=lambda v: print(
                            #         f"VirtualDropdown selected: {v}"
                            #     ),
                            #     theme=VirtualDropdownTheme(
                            #         inputDecoration=InputDecoration(
                            #             label="Fruit",
                            #             hintText="Select a fruit...",
                            #             fillColor=Colors.surfaceVariant,
                            #             labelColor=Colors.onSurfaceVariant,
                            #             focusColor=Colors.primary,
                            #             borderRadius=BorderRadius.all(12),
                            #             border=BorderSide(
                            #                 width=2, color=Colors.outline
                            #             ),
                            #             focusedBorder=BorderSide(
                            #                 width=2, color=Colors.primary
                            #             ),
                            #             contentPadding=EdgeInsets.symmetric(
                            #                 horizontal=16, vertical=14
                            #             ),
                            #             filled=True,
                            #         ),
                            #         dropdownColor=Colors.surface,
                            #         dropdownTextColor=Colors.onSurface,
                            #         selectedItemColor=Colors.rgba(103, 80, 164, 0.15),
                            #         selectedItemShape=BorderRadius.all(8),
                            #         itemPadding=EdgeInsets.symmetric(
                            #             horizontal=12, vertical=8
                            #         ),
                            #     ),
                            # ),
                            # SizedBox(height=20, key=Key("space_before_vlist")),
                            # VirtualDropdown(
                            #     key=Key("test_derived_dropdown_the_2nd"),
                            #     controller=self.derived_dropdown_controller_2,
                            #     onChanged=lambda v: print(
                            #         f"VirtualDropdown selected: {v}"
                            #     ),
                            #     theme=VirtualDropdownTheme(
                            #         inputDecoration=InputDecoration(
                            #             label="Not Fruit",
                            #             hintText="Select a fruit...",
                            #             fillColor=Colors.surfaceVariant,
                            #             labelColor=Colors.onSurfaceVariant,
                            #             focusColor=Colors.primary,
                            #             borderRadius=BorderRadius.all(12),
                            #             border=BorderSide(
                            #                 width=1, color=Colors.outline
                            #             ),
                            #             focusedBorder=BorderSide(
                            #                 width=2, color=Colors.primary
                            #             ),
                            #             contentPadding=EdgeInsets.symmetric(
                            #                 horizontal=16, vertical=14
                            #             ),
                            #             filled=True,
                            #         ),
                            #         dropdownColor=Colors.surface,
                            #         dropdownTextColor=Colors.onSurface,
                            #         selectedItemColor=Colors.rgba(103, 80, 164, 0.15),
                            #         selectedItemShape=BorderRadius.all(8),
                            #         itemPadding=EdgeInsets.symmetric(
                            #             horizontal=12, vertical=8
                            #         ),
                            #     ),
                            # ),
                            # VirtualListView(
                            #     key=Key("my_virtual_list"),
                            #     controller=self.vlist_controller,
                            #     itemCount=1000,
                            #     itemBuilder=self.vlist_item_builder,
                            #     itemExtent=68,
                            #     height=100,
                            #     width=300,
                            # ),
                            # Dropdown(
                            #     key=Key("test_dropdown"),
                            #     controller=self.dropdown_controller,
                            #     onChanged=self.on_dropdown_changed,
                            #     items=[
                            #         ("Option 1", "Option 1"),
                            #         ("Option 2 - Virtualized DOM element", "Option 2"),
                            #         ("Option 3 - Event Delegation FTW", "Option 3"),
                            #     ],
                            # ),
                            # SizedBox(height=20, key=Key("space_before_drag_2")),
                            # Transform.translate(
                            #     offset=self.drag_offset,
                            #     child=GestureDetector(
                            #         key=Key("draggable_box"),
                            #         onPanUpdate=self.on_pan_update,
                            #         child=Container(
                            #             width=150,
                            #             height=100,
                            #             key=Key("draggable_container"),
                            #             decoration=BoxDecoration(
                            #                 color=Colors.red,
                            #                 borderRadius=BorderRadius.all(12),
                            #                 boxShadow="0 4px 6px rgba(0,0,0,0.1)"
                            #             ),
                            #             child=Center(
                            #                 key=Key("draggable_center"),
                            #                 child=Text("Drag Me!", style=TextStyle(color=Colors.white, fontWeight="bold"), key=Key("draggable_text"))
                            #             )
                            #         )
                            #     )
                            # )
                        ],
                        mainAxisAlignment=MainAxisAlignment.CENTER,
                        # crossAxisAlignment=CrossAxisAlignment.CENTER,
                    ),
                ),
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


# if __name__ == "__main__":
#     #     # This allows running the app directly with `python lib/main.py`
#     #     # as well as with the CLI's `pythra run` command.
#     app = Framework.instance()
#     app.set_root(HomePage(key=Key("home_page_wrapper")))
#     app.run()
