# main.py
import os
import sys

from pythra.base import Key
from pythra.styles import BorderRadius, ButtonStyle, CrossAxisAlignment, EdgeInsets, TextStyle
from pythra.widgets import SizedBox

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pythra import (
    Framework,
    StatefulWidget,
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


# -----------------------------
# State (logic + data)
# -----------------------------
class CounterState(State):
    def __init__(self):
        self.count = 0  # app state

    def increment(self):
        self.count += 1
        self.setState()  # triggers UI update

    def decrement(self):
        self.count -= 1
        self.setState()

    # -----------------------------
    # UI (what gets rendered)
    # -----------------------------
    def build(self):
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
                        Text(
                            "Simple Counter App",
                            key=Key("title_text"),
                            style=TextStyle(fontSize=24, fontWeight="bold"),
                        ),
                        SizedBox(height=20, key=Key("spacer_1")),  # Spacer
                        Text(
                            f"Count: {self.count}",
                            key=Key("count_text"),
                            style=TextStyle(fontSize=20, fontFamily="monospace"),
                        ),
                        SizedBox(height=20, key=Key("spacer_2")),  # Spacer
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
                                SizedBox(
                                    width=20, key=Key("spacer_3")
                                ),  # Spacer between buttons
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


# -----------------------------
# Widget wrapper
# -----------------------------
class CounterApp(StatefulWidget):
    def createState(self):
        return CounterState()


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app = Framework.instance()
    app.set_root(CounterApp())
    app.run(title="Pythra Counter App")
