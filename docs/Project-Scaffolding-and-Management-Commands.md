# Project Scaffolding and Management Commands
Relevant source files
- [CHANGELOG.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md)
- [config.yaml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml)
- [pyproject.toml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml)
- [requirements.txt](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/requirements.txt)
- [src/pythra/pythra/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py)
- [src/pythra/setup.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py)

The PyThra CLI (`pythra`) is the primary tool for managing the lifecycle of a PyThra application. It provides commands for project initialization, environment diagnostics, cross-platform asset generation, and development workflow automation. The CLI is built using the `typer` library and is exposed as a console script via `pyproject.toml`[pyproject.toml36-37](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L36-L37)

## CLI Entry Point and Configuration

The CLI entry point is defined in `pythra.pythra_cli.main:app`[pyproject.toml37](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L37-L37) It manages project state primarily through the `config.yaml` file located in the project root.

### config.yaml Structure

This file defines the application identity and windowing behavior.

- `app_name`: The display name of the application [config.yaml1](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L1-L1)
- `app_id`: (Added in v0.1.22) A reverse-DNS string (e.g., `com.pythra.myapp`) used for OS-level integration like Windows `AppUserModelID` and Linux `StartupWMClass`[CHANGELOG.md20-21](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L20-L21)
- `win_width` / `win_height`: Initial window dimensions [config.yaml2-3](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L2-L3)
- `render_dir` / `assets_dir`: Paths to the web-renderer and static asset directories [config.yaml10-11](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L10-L11)

## Core Management Commands

### pythra create-project

Initializes a new PyThra project directory. In version 0.1.22, this command was enhanced to generate platform-specific directories dynamically rather than copying static templates [CHANGELOG.md35-38](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L35-L38)

1. **Identity Generation**: Derives `app_name` and `app_id` from the target directory name (e.g., `my-project` becomes "My Project" and `com.pythra.my-project`) [CHANGELOG.md37-38](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L37-L38)
2. **Scaffolding**: Creates the following structure:

- `lib/main.py`: Application entry point.
- `assets/`: Icons, fonts, and images.
- `render/`: JS engines, CSS, and `index.html`.
- `windows/`, `macos/`, `linux/`: Platform-specific metadata (e.g., `.desktop`, `Info.plist`) [CHANGELOG.md18-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L18-L20)
- `config.yaml`: Populated with generated identity values.

### pythra upgrade

Synchronizes an existing project with the latest framework templates. This is critical for receiving updates to the JavaScript patching engine and CSS components without losing user modifications [CHANGELOG.md22-28](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L22-L28)

- **Render Sync**: Updates JS engines in `render/js/` but skips user-modified files like `index.html` or `styles.css` unless `--force` is used [CHANGELOG.md24-25](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L24-L25)
- **Config Merge**: Injects missing keys (like `app_id`) into an existing `config.yaml` while preserving existing user values [CHANGELOG.md26-27](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L26-L27)
- **Platform Generation**: Retroactively creates `windows/`, `macos/`, and `linux/` directories if they are missing [CHANGELOG.md25-26](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L25-L26)

### pythra generate-icons

A specialized utility that uses `Pillow` to transform a single source PNG into a complete cross-platform icon set [CHANGELOG.md15-17](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L15-L17)
PlatformOutput FormatSizes Generated**Windows**`.ico`7 sizes (16px to 256px)**macOS**`.icns**7 sizes (16px to 1024px)**Linux**Hicolor PNGs8 sizes (16px to 512px)
**Sources:**[CHANGELOG.md15-18](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L15-L18)[pyproject.toml27](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L27-L27)

### pythra install-linux

Automates the integration of the application into Linux desktop environments. This is particularly important for Wayland support, where standard window icons are often ignored in favor of `.desktop` file associations [CHANGELOG.md29-34](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L29-L34)

1. **Desktop File**: Generates and installs a `.desktop` file to `~/.local/share/applications/`.
2. **Icon Deployment**: Moves generated PNGs to `~/.local/share/icons/hicolor/` and renames them to match the `app_id`[CHANGELOG.md30-32](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L30-L32)
3. **Path Rewriting**: Dynamically updates the `Exec=` key in the desktop file to point to the current Python interpreter and `main.py` path [CHANGELOG.md31-32](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L31-L32)

## Development and Build Workflow

### pythra run

Starts the application in development mode.

- **Hot-Reload**: Monitors the project directory for changes and triggers a framework reload.
- **Asset Server**: Starts the internal `AssetServer` on the port defined in `config.yaml` (default 8008) [config.yaml12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L12-L12)
- **Debug Mode**: Enables the QWebEngine developer tools if `Debug: true` is set in `config.yaml`[config.yaml9](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L9-L9)

### pythra package / build

Wraps `PyInstaller` to create standalone executables [pyproject.toml23](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L23-L23)

- **Auto-Icon Detection**: Automatically searches for `windows/appIcon.ico` or `macos/appIcon.icns` if no icon path is provided [CHANGELOG.md68-70](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L68-L70)
- **Bundle Creation**: On macOS, it uses `--macos-create-app-bundle` to produce a native `.app` structure [CHANGELOG.md70-71](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L70-L71)
- **Resource Inclusion**: Ensures `assets/`, `render/`, and `plugins/` are bundled into the executable [CHANGELOG.md71-72](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L71-L72)

### pythra doctor

A diagnostic tool that checks the local environment for PyThra prerequisites:

- Presence of `PySide6`[pyproject.toml14](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L14-L14)
- Cython compilation status for `reconciler_cython` and `key_cython`[src/pythra/setup.py17-29](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L17-L29)
- Platform-specific dependencies (e.g., `dbus-python` on Linux) [pyproject.toml28](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L28-L28)

## Command Architecture and Data Flow

The following diagram illustrates how CLI commands interact with the project filesystem and the Framework configuration.

**CLI-to-Filesystem Interaction**

```

```

**Sources:**[CHANGELOG.md15-38](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L15-L38)[config.yaml1-12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L1-L12)

**Identity Propagation Mapping**
This diagram bridges the natural language "Project Identity" to the specific code entities and configuration keys used across the system.

```

```

**Sources:**[CHANGELOG.md18-21](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L18-L21)[config.yaml1](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/config.yaml#L1-L1)

## Technical Implementation Details

### Cython Integration

The CLI and build system prioritize performance by attempting to compile critical path components using Cython. The `setup.py` file defines extensions for:

- `pythra.reconciler_cython`: The core tree-diffing engine [src/pythra/setup.py20-23](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L20-L23)
- `pythra.key_cython`: Optimized widget key comparison [src/pythra/setup.py25-28](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L25-L28)

If Cython is unavailable during installation, the framework falls back to pure Python implementations [src/pythra/setup.py11-13](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L11-L13)

### Linux Wayland Support

The CLI plays a vital role in solving Wayland's window icon limitations. Because Wayland ignores `setWindowIcon()`, the `webwidget.py` module (triggered during `pythra run` or app startup) calls `_setup_platform_icon()`, which effectively performs a subset of `pythra install-linux` to ensure the environment recognizes the application's visual identity [CHANGELOG.md63-67](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L63-L67)

**Sources:**

- `src/pythra/pythra_cli/main.py` (CLI Entry point)
- `src/pythra/setup.py` (Cython and Script configuration)
- `pyproject.toml` (Dependencies and CLI mapping)
- `CHANGELOG.md` (Feature definitions for v0.1.22)
- `config.yaml` (Project configuration schema)