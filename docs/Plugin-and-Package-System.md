# Plugin and Package System
Relevant source files
- [PACKAGE_SYSTEM_README.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md)

The PyThra Plugin and Package System is a comprehensive, pub.dev-inspired ecosystem designed to extend the framework's capabilities through modular components. It manages the lifecycle of external widgets, themes, and utilities, providing automated dependency resolution, security sandboxing, and seamless integration with the core rendering pipeline.

### System Overview

The package system shifts PyThra from a monolithic widget library to a modular architecture. It supports both legacy `pythra_plugin.py` definitions and the modern `package.json` manifest format [PACKAGE_SYSTEM_README.md90-102](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L90-L102) The system is managed by the `PackageManager`, which coordinates discovery across local directories and installed Python site-packages [PACKAGE_SYSTEM_README.md16-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L16-L20)

### Core Components
ComponentFileResponsibility**Package Manifest**`package_system.py`Defines metadata, `PackageType` (plugin, widgets, theme, etc.), and dependency constraints [package_system.py7-15](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/package_system.py#L7-L15)**Package Manager**`package_manager.py`Handles topological sorting, circular dependency detection, and package discovery [package_manager.py16-24](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/package_manager.py#L16-L24)**Security Validator**`package_security.py`Performs AST-based static analysis to detect dangerous code patterns and verifies file integrity via SHA256 checksums [package_security.py36-44](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/package_security.py#L36-L44)**Registry Client**`package_registry.py`Interfaces with remote repositories for package installation and caching [package_registry.py30-34](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/package_registry.py#L30-L34)
### Logical to Code Entity Mapping

The following diagram illustrates how abstract package concepts map to specific Python classes and storage structures within the toolkit.

**Package Entity Relationship**

```

```

Sources: [PACKAGE_SYSTEM_README.md7-48](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L7-L48)[package_system.py7-15](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/package_system.py#L7-L15)[package_manager.py16-24](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/package_manager.py#L16-L24)

### Integration with Framework Lifecycle

The `Framework` singleton in `core.py` utilizes the `PackageManager` during initialization to auto-load local packages [PACKAGE_SYSTEM_README.md49-54](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L49-L54) This integration ensures that JS engines required by plugin widgets are only loaded into the `QWebEngineView` when the corresponding widgets are actually utilized in the render tree [PACKAGE_SYSTEM_README.md52](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L52-L52)

**Plugin Loading Pipeline**

```

```

Sources: [PACKAGE_SYSTEM_README.md49-54](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L49-L54)[package_manager.py16-24](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/package_manager.py#L16-L24)[package_security.py36-44](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/package_security.py#L36-L44)

### Sub-System Details

#### [Package System Architecture](#8.1)

This section covers the technical implementation of `PackageManifest`, `PackageDependency`, and the `PackageType` enumeration. It details the semantic versioning (semver) resolution logic and how the `PackageManager` performs discovery using `importlib`. It also explains the multi-layer security validation, including AST parsing for Python and JavaScript.
For details, see [Package System Architecture](#8.1).

#### [Creating and Using Plugins](/pythra-toolkit/pythra-toolkit/8.2-creating-and-using-plugins)

This guide provides a walkthrough for developers creating new plugins. It covers the structure of the `plugins/` directory, authoring the `package.json` manifest, and implementing the Python-to-JS bridge for interactive components. It uses the `markdown` editor plugin as a primary example, showcasing the `MarkdownToolbarItem` and `MarkdownEditingController` patterns.
For details, see [Creating and Using Plugins](/pythra-toolkit/pythra-toolkit/8.2-creating-and-using-plugins).

### CLI Tooling

The `pythra` CLI provides a dedicated suite of commands for interacting with the package system, allowing users to install, validate, and search for plugins directly from the terminal [PACKAGE_SYSTEM_README.md55-64](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L55-L64)

- `pythra package install <name>`: Fetches and installs a package from the registry.
- `pythra package validate <path>`: Runs security and integrity checks.
- `pythra package list`: Displays all currently discovered and loaded packages.

Sources: [PACKAGE_SYSTEM_README.md1-161](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/PACKAGE_SYSTEM_README.md#L1-L161)