# Build, Packaging, and Distribution
Relevant source files
- [.github/workflows/build_wheels.yml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/.github/workflows/build_wheels.yml)
- [CHANGELOG.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md)
- [pyproject.toml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml)
- [setup.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/setup.py)
- [src/pythra.egg-info/requires.txt](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra.egg-info/requires.txt)
- [src/pythra/pythra.egg-info/PKG-INFO](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra.egg-info/PKG-INFO)
- [src/pythra/pythra.egg-info/SOURCES.txt](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra.egg-info/SOURCES.txt)
- [src/pythra/pythra.egg-info/requires.txt](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra.egg-info/requires.txt)
- [src/pythra/pythra.egg-info/top_level.txt](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra.egg-info/top_level.txt)
- [src/pythra/pythra/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py)
- [src/pythra/setup.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py)

This page details the mechanisms PyThra uses to transform a Python codebase into a distributable desktop application. It covers the CLI-driven build process, cross-platform icon generation, the automated CI/CD pipeline for PyPI distribution, and the performance-critical Cython compilation layer.

## Build and Packaging Architecture

PyThra utilizes a "src-layout" structure to separate framework code from project templates and CLI tools [pyproject.toml42-43](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L42-L43) The distribution process is split into two layers: the framework distribution (via PyPI) and the end-user application distribution (via PyInstaller wrappers).

### Core Distribution Flow

The following diagram illustrates how PyThra moves from source code to a user's machine.

**Figure 1: Distribution Pipeline**

```

```

Sources: [pyproject.toml1-13](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L1-L13)[.github/workflows/build_wheels.yml11-86](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/.github/workflows/build_wheels.yml#L11-L86)[src/pythra/setup.py31-72](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L31-L72)

## PyThra CLI Build System

The `pythra build` command acts as an intelligent wrapper around PyInstaller, handling the complexities of webview-based desktop apps.

### Build Enhancements

- **Icon Detection:** Automatically locates platform-specific icons if not provided (`windows/appIcon.ico` or `macos/appIcon.icns`) [CHANGELOG.md68-70](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L68-L70)
- **Asset Inclusion:** Ensures `assets/`, `render/`, and `plugins/` directories are bundled into the executable [CHANGELOG.md71](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L71-L71)
- **macOS Bundling:** Automatically applies `--macos-create-app-bundle` and `--macos-app-icon` flags for native `.app` packages [CHANGELOG.md70](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L70-L70)
- **Linux Integration:** Detects compiled binaries via `sys.frozen` to correctly set `Exec=` paths in generated `.desktop` files [CHANGELOG.md63-66](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L63-L66)

### Cross-Platform Icon Generation

The `pythra generate-icons <source.png>` command uses `Pillow` to generate a full suite of platform-standard icons from a single source image [CHANGELOG.md15-17](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L15-L17)[pyproject.toml27](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L27-L27)
PlatformOutput FormatSizes Generated**Windows**`.ico`7 sizes (16px to 256px)**macOS**`.icns`7 sizes (16px to 1024px)**Linux**Hicolor PNGs8 sizes (16px to 512px)
Sources: [CHANGELOG.md15-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L15-L20)[pyproject.toml27](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L27-L27)[src/pythra/pythra/generate_icons.py1-100](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/generate_icons.py#L1-L100)

## Cython Extension Compilation

To achieve Flutter-like performance, PyThra compiles its most critical components into C extensions using Cython. This is managed by `setup.py` which applies `-O3` (or `/Ox` on Windows) optimizations [setup.py27-36](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/setup.py#L27-L36)

**Figure 2: Cython Compilation Map**

```

```

### Compiled Modules

1. **`reconciler_cython`**: Handles the recursive tree diffing and patch generation [src/pythra/setup.py19-23](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L19-L23)
2. **`key_cython`**: Optimized `Key` class for fast widget identification during reconciliation [src/pythra/setup.py24-28](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L24-L28)

Sources: [src/pythra/setup.py15-29](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py#L15-L29)[setup.py12-38](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/setup.py#L12-L38)[CHANGELOG.md59-62](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L59-L62)

## CI/CD Pipeline (GitHub Actions)

PyThra uses a multi-stage workflow defined in `.github/workflows/build_wheels.yml` to automate releases to PyPI.

### Build Jobs

- **`build_wheels`**: Uses `pypa/cibuildwheel` to compile Cython extensions for Python 3.9 through 3.13 across Windows, macOS, and Ubuntu [ .github/workflows/build_wheels.yml12-32](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/ .github/workflows/build_wheels.yml#L12-L32)
- **`build_sdist`**: Generates the source distribution `.tar.gz`[ .github/workflows/build_wheels.yml35-55](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/ .github/workflows/build_wheels.yml#L35-L55)
- **`upload_pypi`**: Implements **Trusted Publishing**. It uses OpenID Connect (OIDC) tokens to authenticate with PyPI, eliminating the need for hardcoded API secrets [ .github/workflows/build_wheels.yml57-86](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/ .github/workflows/build_wheels.yml#L57-L86)

Sources: [ .github/workflows/build_wheels.yml1-86](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/ .github/workflows/build_wheels.yml#L1-L86)[pyproject.toml1-3](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L1-L3)

## Project Structure and Metadata

PyThra follows a strict directory layout to support both development and distribution.

### Package Data Inclusion

The `pyproject.toml` file explicitly includes non-Python assets required for the framework to function [pyproject.toml45-73](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L45-L73):

- **Render Templates:**`index.html`, `qwebchannel.js`, and the `js/` engine directory.
- **Platform Templates:**`.desktop` (Linux), `Info.plist` (macOS), and `hicolor` icon structures.
- **Project Config:**`config.yaml` which defines the `app_id` (e.g., `com.pythra.project`) used for OS-level integration [CHANGELOG.md20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L20-L20)

Sources: [pyproject.toml39-73](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml#L39-L73)[CHANGELOG.md18-21](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md#L18-L21)[src/pythra/pythra.egg-info/SOURCES.txt1-154](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra.egg-info/SOURCES.txt#L1-L154)