# Getting Started
Relevant source files
- [CHANGELOG.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md)
- [README.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md)
- [assets/demo.gif](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/assets/demo.gif)
- [config.yaml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml)
- [pyproject.toml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml)
- [requirements.txt](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/requirements.txt)
- [src/pythra/pythra/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py)
- [src/pythra/pythra/window/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/window/__init__.py)
- [src/pythra/setup.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py)

This page provides a technical guide for setting up the PyThra Framework, initializing new projects via the Command Line Interface (CLI), and understanding the fundamental project structure. PyThra is a declarative UI toolkit for Python that utilizes a high-performance webview rendering layer inspired by Flutter's component model.

## Prerequisites

PyThra requires a modern Python environment and the PySide6 Qt bindings for its webview container.

- **Python Version:**`3.9` or higher is required [pyproject.toml12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L12-L12)
- **PySide6:** Required for the `QWebEngineView` and application loop [pyproject.toml14](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L14-L14)
- **Operating Systems:**
- **Windows:** Fully supported.
- **macOS:** Fully supported.
- **Linux:** Requires `dbus-python` for system integration [pyproject.toml28](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L28-L28)

## Installation

The framework is distributed via `pip`. Installation includes the core library and the `pythra` CLI tool.

```
# Standard installation
pip install pythra
 
# Verify the environment and dependencies
pythra doctor
```

Sources: [README.md36-55](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md#L36-L55)[pyproject.toml5-37](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L5-L37)

## Creating a New Project

The `pythra` CLI is the primary tool for scaffolding. It generates a project based on a standardized template that includes necessary JavaScript engines, assets, and platform-specific metadata.

### The `create-project` Command

When you run `pythra create-project <name>`, the CLI performs the following:

1. **Identity Generation:** It generates a unique `app_id` (e.g., `com.pythra.my-app`) and sets the `app_name` in `config.yaml`[CHANGELOG.md35-38](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L35-L38)
2. **Platform Scaffolding:** It creates `windows/`, `macos/`, and `linux/` directories containing metadata like `.desktop` files and `Info.plist`[CHANGELOG.md18-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L18-L20)
3. **Render Engine Injection:** It populates the `render/` directory with the `PythraBridge` and widget-specific JS engines (e.g., `virtual_grid.js`, `scroll-bar/`) [pyproject.toml47-52](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L47-L52)

```sh
pythra create-project my_awesome_app
cd my_awesome_app
pythra run
```

Sources: [CHANGELOG.md15-38](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L15-L38)[pyproject.toml36-37](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L36-L37)

## Project Directory Layout

A standard PyThra project follows a strict convention to ensure the `AssetServer` and `Framework` can locate resources.
Directory/FileDescription`lib/main.py`The entry point of the application. Contains the `Framework.run()` call.`assets/`Static files (images, fonts, icons). Served via `assets_server_port`[config.yaml11-12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L11-L12)`render/`Contains `index.html`, `styles.css`, and the `js/` folder for bridge logic.`config.yaml`Global application settings (window size, debug mode, ports).`plugins/`Local or downloaded plugins that extend widget functionality.`windows/`, `macos/`, `linux/`Platform-specific assets (icons, manifests) for packaging [CHANGELOG.md18](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L18-L18)
### Implementation Mapping: Project Structure to Code

The following diagram illustrates how the directory structure relates to the Python classes that consume them.

**Directory to Entity Mapping**

```
Code Entity Space

Project Root

Parsed by

Initializes

Served by

Loaded into

Uses

config.yaml

lib/main.py

assets/

render/

class Framework (core.py)

class Config (config.yaml)

class AssetServer (server.py)

class Navigator (navigation.py)
```

Sources: [config.yaml1-12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L1-L12)[src/pythra/pythra/__init__.py11-13](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py#L11-L13)[README.md62-95](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md#L62-L95)

## Running the First App

A PyThra application starts by defining a root `Widget` and passing it to the `Framework`.

### Basic Application Logic (`lib/main.py`)

The application lifecycle begins with the `Framework` singleton. Users typically define a `StatefulWidget` to manage application data.

```python
from pythra import (
    Framework,
    StatefulWidget,
    State,
    Column,
    Row,
    Text,
    Center,
    IconButton,
    Icon,
    Icons,
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
        return Center(
            child=Column(
                mainAxisAlignment=MainAxisAlignment.CENTER,
                children=[
                    Text("Simple Counter App"),
                    Text(f"Count: {self.count}"),

                    Row(
                        mainAxisAlignment=MainAxisAlignment.CENTER,
                        children=[
                            # Decrease button
                            IconButton(
                                icon=Icon(Icons.stat_minus_1_rounded),
                                onPressed=self.decrement,
                            ),

                            # Increase button
                            IconButton(
                                icon=Icon(Icons.stat_1_rounded),
                                onPressed=self.increment,
                            ),
                        ],
                    ),
                ],
            )
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
```

### Data Flow: Initialization to Display

This diagram shows the sequence of events from the CLI command to the visual rendering of the first widget.

**App Startup Sequence**

```
pythra_bridge.js
QWebEngineView
AssetServer (server.py)
Framework (core.py)
pythra CLI
pythra_bridge.js
QWebEngineView
AssetServer (server.py)
Framework (core.py)
pythra CLI
run()
start() on assets_server_port
load(index.html)
Initialize Bridge
set_root(WidgetTree)
build_subtree()
applyPatches(InitialHTML)
DOM Update
```

Sources: [src/pythra/pythra/__init__.py11](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py#L11-L11)[config.yaml12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L12-L12)[README.md112-180](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/README.md#L112-L180)

## Configuration (`config.yaml`)

The `config.yaml` file is the central authority for window management and server configuration.
KeyDefaultDescription`app_name`"My Pythra App"The title displayed in the OS window title bar.`win_width` / `win_height`1280 / 720Initial dimensions of the application window.`frameless``false`If `true`, removes the OS window decorations (close/min/max).`assets_server_port`8008The port used by the internal Python server to serve `assets/`.`Debug``true`Enables hot-reload and verbose logging in the terminal.
Sources: [config.yaml1-12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L1-L12)[CHANGELOG.md20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L20-L20)