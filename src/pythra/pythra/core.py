# pythra/core.py

# --- ADDED THESE IMPORTS AT THE TOP OF THE FILE ---
import cProfile
import pstats
import io
import logging
import base64 
# --- END OF IMPORTS ---

import os
from pathlib import Path
import importlib
import sys
import re
import shutil
import time
import json
import math
import html
import weakref
from typing import Optional, Set, List, Dict, TYPE_CHECKING, Callable, Any, Union

# PySide imports for main thread execution
from PySide6.QtCore import QTimer

# Framework imports
from .config import Config
from .server import AssetServer
from .api import Api
from .window import webwidget

# New/Refactored Imports
from .base import Widget, Key
from .state import State, StatefulWidget, StatelessWidget
from .reconciler import Reconciler, Patch, ReconciliationResult
from .widgets import *  # Import all widgets for class lookups if needed
from .package_manager import PackageManager
from .package_system import PackageType
from .styles import *
from .theme import ThemeManager
from .debug_utils import debug_print, init_debug_from_config


# Type Hinting for circular dependencies
if TYPE_CHECKING:
    from .state import State


def _json_default_handler(obj: Any) -> Any:
    """
    Default handler for JSON serialization of non-standard types.
    Optimized for use with orjson's 'default' hook.
    """
    if isinstance(obj, Widget):
        return f"<{type(obj).__name__}>"
    if callable(obj):
        return "<function>"
    if isinstance(obj, weakref.ReferenceType):
        return "<weakref>"
    if isinstance(obj, set):
        return list(obj)
    
    # Fallback for other types
    return f"<{type(obj).__name__}>"

# Fast JSON dumps: prefer orjson when available for speed-critical paths
try:
    import orjson as _orjson  # type: ignore

    def _dumps(obj: Any) -> str:
        """Fast dumps using orjson, returns str."""
        # orjson.dumps returns bytes. default hook handles custom types efficiently in C.
        return _orjson.dumps(obj, default=_json_default_handler).decode('utf-8')
except Exception:
    def _dumps(obj: Any) -> str:
        """Fallback to stdlib json.dumps with compact separators."""
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=False, default=_json_default_handler)


class Framework:
    """
    The main PyThra Framework class - this is the heart of your application!
    
    Think of this as the "manager" that handles everything:
    - Setting up your app window
    - Loading plugins and packages 
    - Managing your UI widgets
    - Serving static files (CSS, JS, images)
    - Handling user interactions
    
    This class uses the "singleton pattern" - meaning there's only ever 
    one instance of the Framework running at a time.
    """

    _instance = None  # Stores the single Framework instance

    @classmethod
    def instance(cls):
        """Gets the current Framework instance, creates one if needed"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """
        Sets up the PyThra Framework when your app starts.
        
        This method runs automatically and handles:
        - Finding your project folder
        - Loading your config file
        - Setting up asset directories
        - Initializing the package/plugin system
        - Starting the web server for static files
        """
        # Make sure only one Framework instance exists (singleton pattern)
        if Framework._instance is not None:
            raise Exception("Only one Framework instance can exist at a time!")
        Framework._instance = self

        # STEP 1: Find your project's root directory
        # This is where your config.yaml, assets/, and plugins/ folders live
        main_script_path = os.path.abspath(sys.argv[0])  # Path to your main.py file

        # If your main.py is in a 'lib' folder, go up one level to find project root
        if "lib" in Path(main_script_path).parts:
            self.project_root = Path(main_script_path).parent.parent
        else:
            # Otherwise, project root is where your main.py lives
            self.project_root = Path(main_script_path).parent

        debug_print(f"🎯 PyThra Framework | Project Root detected at: {self.project_root}")

        # STEP 2: Load your project configuration
        # This reads settings from your config.yaml file
        self.config = Config(config_path=self.project_root / 'config.yaml')
        self.config_dict = self.config.as_dict()

        # STEP 3: Set up directory paths for your app
        # render/ folder: Contains HTML, CSS, JS files for the UI
        # assets/ folder: Contains images, fonts, and other static files
        self.render_dir = self.project_root / self.config.get('render_dir', 'render')
        self.assets_dir = self.project_root / self.config.get('assets_dir', 'assets')

        # Create these directories if they don't exist yet
        self.render_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)

        # Copy default PyThra files (CSS, JS) to your project if missing
        self._ensure_default_assets()

        self.html_file_path = self.render_dir / "index.html"
        self.css_file_path = self.render_dir / "styles.css"

        # STEP 4: Initialize the Package/Plugin System
        # This handles loading plugins from your plugins/ folder
        self.package_manager = PackageManager(self.project_root)
        self.package_manager.set_framework(self)

        # Keep these for backward compatibility with older plugins
        self.plugins = {}  # Old-style plugin storage
        self.plugin_js_modules = {}  # JavaScript modules from plugins

        # STEP 4a: Auto-discover packages and plugins
        # This scans your project for any plugins you've added
        debug_print("🔍 PyThra Framework | Scanning for packages and plugins...")
        discovered_packages = self.package_manager.discover_all_packages()

        # Automatically load any plugins found in your plugins/ directory
        local_packages = [name for name, packages in discovered_packages.items() 
                         if any(pkg.path.parent.name == "plugins" for pkg in packages)]

        if local_packages:
            # Load the packages and handle any dependency issues
            loaded_packages, warnings = self.package_manager.resolve_and_load_packages(local_packages)

            # Show any warnings (like missing dependencies)
            for warning in warnings:
                print(f"⚠️  PyThra Framework | Package Warning: {warning}")

            # Populate the old-style plugins dictionary for CSS and JS module lookup
            for pkg_name, pkg_info in loaded_packages.items():
                if hasattr(pkg_info, 'manifest'):
                    manifest = pkg_info.manifest
                    
                    self.plugins[pkg_name] = {}
                    
                    if manifest.js_modules:
                        self.plugins[pkg_name]['js_modules'] = manifest.js_modules
                        print(f"📦 PyThra Framework | Found JS modules in {pkg_name}: {manifest.js_modules}")
                        
                    if manifest.css_files:
                        self.plugins[pkg_name]['css_files'] = manifest.css_files
                        print(f"🎨 PyThra Framework | Found CSS files in {pkg_name}: {manifest.css_files}")

                elif hasattr(pkg_info, 'package_json'):
                    manifest = pkg_info.package_json
                    js_modules = manifest.get('js_modules', {})
                    if js_modules:
                        self.plugins[pkg_name] = {
                            'js_modules': js_modules
                        }
                        print(f"📦 PyThra Framework | Found JS modules in {pkg_name}: {js_modules}")

            print(f"🎉 PyThra Framework | Successfully loaded {len(loaded_packages)} packages: {', '.join(loaded_packages.keys())}")

        # STEP 5: Start the Asset Server
        # This serves your static files (images, CSS, JS) to the web browser
        package_asset_dirs = self.package_manager.get_asset_server_dirs()
        self.asset_server = AssetServer(
            directory=str(self.assets_dir),  # Main assets directory
            port=self.config.get("assets_server_port"),  # Port from config
            extra_serve_dirs=package_asset_dirs  # Plugin asset directories
        )

        # STEP 6: Initialize core components
        self.api = webwidget.Api()  # Handles JavaScript <-> Python communication
        self.reconciler = Reconciler()  # Manages UI updates efficiently
        self.root_widget: Optional[Widget] = None  # Your main UI widget
        self.window = None  # The application window
        self.id = "main_window_id"  # Unique ID for the main window

        # Internal tracking variables
        self.called = False  # Tracks if the app has been started

        # State Management System
        # These handle when your UI needs to be updated
        self._reconciliation_requested: bool = False
        self._pending_state_updates: Set[State] = set()

        # Window Resize Listeners
        self._resize_listeners: Set[Callable[[int, int], None]] = set()
        self.window_width: int = 0
        self.window_height: int = 0

        self._loaded_js_engines: Set[str] = set() # Tracks JS engines already sent to the browser

        # Small in-memory caches to avoid repeated filesystem hits
        # Maps frozenset(required_engines) -> combined JS string
        self._js_utils_cache: Dict[frozenset, str] = {}
        # Cache for file contents to avoid reopening the same file repeatedly
        self._js_file_content_cache: Dict[str, str] = {}
        self._engine_to_file_map = {
            'generateRoundedPath': "render/js/pathGenerator.js",
            'ResponsiveClipPath': "render/js/clipPathUtils.js", 
            'scalePathAbsoluteMLA': "render/js/clipPathUtils.js",
            'PythraSlider': "render/js/slider.js",
            'PythraDropdown': "render/js/dropdown.js",
            'PythraGestureDetector': "render/js/gesture_detector.js",
            'PythraGradientClipPath': "render/js/gradient_border.js",
            'PythraVirtualList': "render/js/virtual_list.js",
            'PythraVirtualGrid': "render/js/virtual_grid.js",
            'PythraTextField': "render/js/textfield.js",
            'PythraVirtualizedDropdownInternal': "render/js/virtual_dropdown.js"
        }

        self._result = None  # Stores UI update results
        # Track whether initial files were written and keep their last content
        self._initial_files_written: bool = False
        self._cached_initial_html: Optional[str] = None
        self._cached_initial_css: Optional[str] = None
        self._cached_font_css: Optional[str] = None 

        # Tracks JS blueprint classes for clip-paths initialized in this exact instance to skip duplications.
        self._clip_blueprint_registry: Set[str] = set()

        # STEP 7: Start the asset server and finalize setup
        self.asset_server.start()  # Begin serving static files

        # Tell widgets where to find the Framework instance
        Widget.set_framework(self)
        StatefulWidget.set_framework(self)
        self._last_update_time = time.time()

        debug_print("🚀 PyThra Framework | Initialization Complete! Ready to build your amazing app! 🎯")

    # Package management methods are now handled by PackageManager
    # Legacy methods kept for backward compatibility if needed
        import atexit
        atexit.register(self._maybe_auto_run)

    def _maybe_auto_run(self):
        """Automatically calls run() if a root widget is set but the app hasn't started yet."""
        if not self.called and self.root_widget:
            # We check if we are in the main script to avoid accidental runs during imports
            # But usually, if root_widget is set, the user intended to run the app.
            debug_print("✨ PyThra Framework | triggering implicit app.run()...")
            self.run()

    def get_loaded_packages(self) -> Dict[str, Any]:
        """Get information about loaded packages"""
        return self.package_manager.get_loaded_packages()

    def list_packages(self, package_type: Optional[PackageType] = None) -> List[Any]:
        """List all discovered packages, optionally filtered by type"""
        return self.package_manager.list_packages(package_type)

    def register_resize_listener(self, listener: Callable[[int, int], None]):
        """Register a callback for window resize events."""
        self._resize_listeners.add(listener)

    def unregister_resize_listener(self, listener: Callable[[int, int], None]):
        """Unregister a window resize callback."""
        if listener in self._resize_listeners:
            self._resize_listeners.remove(listener)

    def handle_resize(self, width: int, height: int):
        """Notify all registered listeners about a window resize."""
        self.window_width = width
        self.window_height = height
        for listener in list(self._resize_listeners):
            listener(width, height)

    def get_html_id_for_key(self, key: Key) -> Optional[str]: # pyright: ignore[reportInvalidTypeForm]
        """
        Look up the live browser element ID (e.g. ``'fw_id_42'``) for a widget
        identified by a ``Key``.

        The reconciler stores every rendered widget in
        ``reconciler.context_maps["main"]`` keyed by the widget's
        ``get_unique_id()`` return value (which is the widget's ``Key`` when one
        is set).  This method searches that map and returns the corresponding
        ``html_id`` string that uniquely identifies the DOM element in the
        browser.

        Args:
            key: The ``Key`` object that was assigned to the widget at
                 construction time (e.g. ``Key("my_button")``).

        Returns:
            The DOM element id string (``"fw_id_<n>"``) when found, or
            ``None`` if no rendered widget with that key exists in the current
            render map.

        Example::

            fw = Framework.instance()
            html_id = fw.get_html_id_for_key(Key("my_button"))
            if html_id:
                fw.window.evaluate_js(fw.id, f"document.getElementById('{html_id}').style.opacity = '0.5';")
        """
        main_map = self.reconciler.get_map_for_context("main")

        # Fast path: the map is keyed by get_unique_id() which equals the Key
        # when the widget has one.
        node_data = main_map.get(key)
        if node_data is not None:
            return node_data.get("html_id")

        # Slow path: search all entries for a stored `key` field that matches.
        # This handles widgets whose map key is an internal UUID (no explicit Key).
        for node_data in main_map.values():
            if node_data.get("key") == key:
                return node_data.get("html_id")

        return None

    def _ensure_default_assets(self):
        """
        Ensures your project has all the essential files PyThra needs to work properly.
        
        Think of this as "copying the blueprint files" to your project:
        - JavaScript files that handle UI interactions
        - CSS files for styling
        - Font files for icons (Material Symbols)
        - Other static assets PyThra needs
        
        This method only copies files that are missing - it won't overwrite
        files you've customized in your project.
        
        How it works:
        1. Finds the template files inside the PyThra package installation
        2. Copies web files (JS, CSS) to your project's render/ folder
        3. Copies asset files (fonts, images) to your project's assets/ folder
        4. Only copies if the files don't already exist in your project
        """
        # Find the source path inside the installed pythra package
        package_root = Path(__file__).parent
        source_render_dir = package_root / 'web_template'
        source_assets_dir = package_root / 'assets_template'

        # Copy web files (js, etc.)
        if source_render_dir.exists():
            for item in source_render_dir.iterdir():
                dest_item = self.render_dir / item.name
                if not dest_item.exists():
                    if item.is_dir():
                        shutil.copytree(item, dest_item)
                    else:
                        shutil.copy(item, dest_item)

        # Copy asset files (fonts, etc.)
        if source_assets_dir.exists():
            for item in source_assets_dir.iterdir():
                dest_item = self.assets_dir / item.name
                if not dest_item.exists():
                    if item.is_dir():
                        shutil.copytree(item, dest_item)
                    else:
                        shutil.copy(item, dest_item)

    def set_root(self, widget: Widget):
        """
        Sets the main widget that will be displayed when your app starts.
        
        Think of this as telling PyThra: "This is the main screen I want to show"
        
        Args:
            widget: The main widget of your application (usually a Scaffold, 
                   MaterialApp, or custom widget you've created)
        
        Example:
            app = Framework.instance()
            app.set_root(MyMainWidget())
            app.run()
        """
        self.root_widget = widget

    # We will refactor the rendering logic out of `run` into its own method
    def _perform_initial_render(self, root_widget: Widget, title: str):
        """
        The "magic moment" where PyThra converts your Python widgets into a web page!
        
        This is like a master chef preparing a complex meal - lots happens behind the scenes:
        
        What this method does:
        1. **Build Phase**: Converts your widget tree into a detailed blueprint
        2. **Reconcile Phase**: Figures out what HTML elements need to be created
        3. **Analyze Phase**: Determines what JavaScript engines are needed (sliders, dropdowns, etc.)
        4. **Generate Phase**: Creates the actual HTML, CSS, and JavaScript code
        5. **Write Phase**: Saves everything to files that the browser can display
        
        Args:
            root_widget: Your main app widget (set via set_root())
            title: The window title that appears in the browser tab
        
        Think of it as PyThra's "rendering engine" - similar to how a game engine
        converts 3D models into pixels on your screen, but for web UI!
        """
        print("\n🎨 PyThra Framework | Performing Initial UI Render...")
        debug_print("\n🎨 PyThra Framework | Performing Initial UI Render...")

        # 1. Build the full widget tree
        built_tree_root = self._build_widget_tree(root_widget, context_map={})
        initial_tree_to_reconcile = built_tree_root

        # 2. Perform initial reconciliation
        result = self.reconciler.reconcile(
            previous_map={},
            new_widget_root=initial_tree_to_reconcile,
            parent_html_id="root-container",
        )
        self._result = result # Store the result

        _v_items_required_engines = []

        for init in result.js_initializers:
            if init['type'] == 'virtual_grid':
                # for k in init['data']['virtual_grid_options']['initialItems']:
                _v_items_required_engines = init['data']['virtual_grid_options']['virtualItemsEngines']

        # 3. Update framework state from the result
        self.reconciler.context_maps["main"] = result.new_rendered_map
        for cb_id, cb_func in result.registered_callbacks.items():
            self.api.register_callback(cb_id, cb_func)

        # 4. Analyze required JS engines for optimization
        required_engines = self._analyze_required_js_engines(built_tree_root, result)
        print(f"⚙️  PyThra Framework | Analysis Complete: {len(required_engines)} JS engines needed: {', '.join(required_engines) if required_engines else 'None'}")

        self._loaded_js_engines = required_engines.update(_v_items_required_engines) if _v_items_required_engines else required_engines  # Store the initially loaded engines

        # 5. Generate initial HTML, CSS, and JS with optimized loading
        root_key = initial_tree_to_reconcile.get_unique_id() if initial_tree_to_reconcile else None
        html_content = self._generate_html_from_map(root_key, result.new_rendered_map)
        css_rules = self._generate_css_from_details(result.active_css_details)
        js_script = self._generate_initial_js_script(result, required_engines)

        # 6. Write files
        self._write_initial_files(title, html_content, css_rules, js_script)

        # 7. Set flag to prevent re-injection during reconciliation
        self.called = True  # JS utilities are already included in initial render

    def run(
        self,
        title: str = config.get("app_name"),
        width: int = config.get("win_width"),
        height: int = config.get("win_height"),
        min_width: int = config.get("min_win_width"),
        min_height: int = config.get("min_win_height"),
        frameless: bool = config.get("frameless"),
        maximized: bool = config.get("maximixed"),
        fixed_size: bool = config.get("fixed_size"),
        video_overlay: bool = False,
        # --- THIS IS THE CRUCIAL ADDITION ---
        block: bool = True
    ):
        """
        The "GO!" button for your PyThra application - this starts everything!
        
        This is the final step in launching your app. Think of it like starting your car:
        1. Checks that everything is ready (root widget is set)
        2. Renders your UI into HTML, CSS, and JavaScript
        3. Creates the application window with your specified settings
        4. Starts the event loop (keeps your app running and responsive)
        
        Args:
            title: What appears in the window title bar (default from config)
            width: Window width in pixels (default from config)
            height: Window height in pixels (default from config) 
            frameless: If True, removes window decorations (no title bar, borders)
            maximized: If True, starts the window maximized
            fixed_size: If True, prevents user from resizing the window
            video_overlay: If True, creates a video_frame widget underneath and
                          promotes the webview to a floating transparent overlay
                          (mirrors VLCPlayer stacking). Access the native window
                          ID via Framework.video_frame_window_id.
                          Automatically set to True when the VideoPlayer plugin is used.
            block: If True, keeps the program running (you almost always want this)
        
        Example:
            app = Framework.instance()
            app.set_root(MyMainWidget())
            app.run(title="My Awesome App", width=1200, height=800)
        
        Note: This method will block (not return) until the user closes the app,
        unless you set block=False (which is rarely what you want).
        """
        if not self.root_widget:
            raise ValueError("Root widget not set. Use set_root() before run().")

        # print("\n>>> Framework: Performing Initial Render <<<")

        # Now `run` just calls the new helper method
        self._perform_initial_render(self.root_widget, title)

        # Allow plugins (e.g., pythra-video-player) to request video_overlay mode.
        # The plugin sets _video_overlay_requested = True during widget initState().
        if getattr(self, '_video_overlay_requested', False):
            video_overlay = True

        self.window = webwidget.create_window(
            title,
            self.id,
            self.html_file_path,
            self.api,
            width,
            height,
            min_width=min_width,
            min_height=min_height,
            frameless=frameless,
            maximized=maximized,
            fixed_size=fixed_size,
            video_overlay=video_overlay,
            debug=bool(self.config.get("Debug", False)),
        )

        # If any plugins or states queued injections while the window was not
        # yet created, flush and execute them now. This avoids AttributeError
        # caused by calling evaluate_js on a None window.
        pending_injections = getattr(self, '_pending_window_injections', None)
        if pending_injections:
            print(f"🔁 PyThra Framework | Executing {len(pending_injections)} deferred window injections")
            for inj in pending_injections:
                try:
                    inj()
                except Exception as e:
                    print('Error running deferred injection:', e)
            # Clear the list so they don't run again
            self._pending_window_injections = []

        # 9. Start the application event loop.
        print("🎆 PyThra Framework | Starting application event loop...")
        debug_print("🎆 PyThra Framework | Starting application event loop...")
        webwidget.start(window=self.window, debug=bool(self.config.get("Debug", False)))

    def close(self):
        # self.asset_server.stop()
        self.window.close_window() if self.window else debug_print("unable to close window: window is None")
        self.asset_server.stop()

    def minimize(self):
        self.window.minimize() if self.window else debug_print("unable to close window: window is None")

    @property
    def video_frame_window_id(self) -> Optional[int]:
        """
        Returns the native platform window ID of the video_frame widget,
        suitable for passing to VLC's set_xwindow() / set_hwnd() / set_nsobject().

        Only available when the app was started with video_overlay=True.
        Returns None otherwise.
        """
        if self.window and hasattr(self.window, 'video_frame'):
            return int(self.window.video_frame.winId())
        return None

    @property
    def theme(self):
        return ThemeManager.instance().current_theme

    def set_theme(self, theme):
        """Updates the application theme instantly."""
        ThemeManager.instance()._current_theme = theme
        css_vars = theme.to_css_vars()
        escaped_css = _dumps(css_vars).replace("`", "\\`")

        js_cmd = f"""
            var themeSheet = document.getElementById('theme-styles');
            if (themeSheet) {{
                 themeSheet.textContent = {escaped_css};
            }} else {{
                 var style = document.createElement('style');
                 style.id = 'theme-styles';
                 style.textContent = {escaped_css};
                 document.head.prepend(style);
            }}
        """
        if self.window:
            self.window.evaluate_js(self.id, js_cmd)
        else:
            print("Warning: Window not ready, theme will be applied on startup.")

    def _dispose_widget_tree(self, widget: Optional[Widget]):
        """Recursively disposes of the state of a widget and its children."""
        if widget is None:
            return

        # Dispose of the current widget's state if it's stateful
        if isinstance(widget, StatefulWidget):
            state = widget.get_state()
            if state:
                state.dispose()

        # Recurse on all children
        if hasattr(widget, 'get_children'):
            for child in widget.get_children():
                self._dispose_widget_tree(child)

    # --- State Update and Reconciliation Cycle ---

    # Place this new helper method somewhere in the Framework class
    def _get_js_utility_functions(self, required_engines: set = None) -> str:
        """
        Reads only the required JS engine and utility files based on actual usage.
        
        :param required_engines: Set of engine names that are actually needed
        :return: Combined JavaScript code string
        """
        # --- MAPPING OF ENGINES TO FILES ---
        engine_to_file_map = {
            'generateRoundedPath': "render/js/pathGenerator.js",
            'ResponsiveClipPath': "render/js/clipPathUtils.js", 
            'scalePathAbsoluteMLA': "render/js/clipPathUtils.js",
            'PythraSlider': "render/js/slider.js",
            'PythraDropdown': "render/js/dropdown.js",
            'PythraGestureDetector': "render/js/gesture_detector.js",
            'PythraGradientClipPath': "render/js/gradient_border.js",
            'PythraVirtualList': "render/js/virtual_list.js",
            'PythraVirtualGrid': "render/js/virtual_grid.js",
            'PythraTextField': "render/js/textfield.js",
            'PythraVirtualizedDropdownInternal': "render/js/virtual_dropdown.js"
            #'PythraMarkdownEditor': "render/js/dropdown.js", # Placeholder key to suppress warning, actual loaded via plugin
        }
        # Build a cache key. None means 'ALL' engines load; use a stable frozenset.
        cache_key = frozenset(required_engines) if required_engines is not None else frozenset({'__ALL__'})

        self._engine_to_file_map = engine_to_file_map

        # Return cached result if present
        cached = self._js_utils_cache.get(cache_key)
        if cached is not None:
            debug_print(f"🔁 Reusing cached JS utilities for key={set(cache_key)}")
            return cached

        # Determine files to load
        if required_engines is None:
            # print("🔧 Loading all JS engines (no optimization applied)")
            files_to_load = set(engine_to_file_map.values())
        else:
            # print(f"🎯 Optimized loading: Only loading engines for {required_engines}")
            files_to_load = set()
            for engine in required_engines:
                if engine in engine_to_file_map:
                    files_to_load.add(engine_to_file_map[engine])
                else:
                    # Plugin engines are loaded via plugin_js_modules — only warn for truly unknown engines
                    print(f"Plugin js modules: {self.plugin_js_modules}")
                    if engine not in self.plugin_js_modules:
                        print(f"⚠️  Unknown engine requested: {engine}")

        all_js_code = []
        loaded_files = set()

        for file_path in files_to_load:
            if file_path in loaded_files:
                continue
            loaded_files.add(file_path)

            try:
                full_path = str(self.project_root / file_path)

                # Use cached file content when available
                content = self._js_file_content_cache.get(full_path)
                if content is None:
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Cache the raw content for future requests
                        self._js_file_content_cache[full_path] = content
                    except FileNotFoundError:
                        print(f"⚠️ Warning: JS utility file not found: {full_path}")
                        continue

                # Cleanup and wrap as before
                cleaned = content.replace('export class', 'class').replace('export function', 'function')
                cleaned = re.sub(r'import\s+.*\s+from\s+.*?;?\n?', '', cleaned)

                filename = os.path.basename(file_path)

                wrapped_content = (
                    f"""try {{
                        \n{cleaned}\n
                        // Make common names available on window if defined\n
                        if (typeof ResponsiveClipPath !== 'undefined') window.ResponsiveClipPath = ResponsiveClipPath;\n
                        if (typeof PythraSlider !== 'undefined') window.PythraSlider = PythraSlider;\n
                        if (typeof PythraDropdown !== 'undefined') window.PythraDropdown = PythraDropdown;\n
                        if (typeof PythraGestureDetector !== 'undefined') window.PythraGestureDetector = PythraGestureDetector;\n
                        if (typeof PythraGradientClipPath !== 'undefined') window.PythraGradientClipPath = PythraGradientClipPath;\n
                        if (typeof PythraVirtualList !== 'undefined') window.PythraVirtualList = PythraVirtualList;\n
                        if (typeof PythraVirtualGrid !== 'undefined') window.PythraVirtualGrid = PythraVirtualGrid;\n
                        if (typeof generateRoundedPath !== 'undefined') window.generateRoundedPath = generateRoundedPath;\n
                        if (typeof scalePathAbsoluteMLA !== 'undefined') window.scalePathAbsoluteMLA = scalePathAbsoluteMLA;\n
                        if (typeof PythraTextField !== 'undefined') window.PythraTextField = PythraTextField;\n
                    }} catch (e) {{ console.error('Error loading {filename}:', e); }}"""
                )

                all_js_code.append(f"// --- Injected from {os.path.basename(file_path)} ---\n{wrapped_content}")
                print(f"✅ Loaded JS engine: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️ Error while loading JS utility '{file_path}': {e}")

        # Load plugin JS modules (cache file contents similarly)
        for engine_name, module_info in self.plugin_js_modules.items():
            try:
                full_path = str(Path(module_info['path']))
                content = self._js_file_content_cache.get(full_path)
                if content is None:
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self._js_file_content_cache[full_path] = content
                    except FileNotFoundError:
                        print(f"⚠️ Warning: Plugin JS file not found: {full_path}")
                        continue

                cleaned = re.sub(r'import\s+.*\s+from\s+.*?;?\n?', '', content)
                cleaned = cleaned.replace('export class', 'class').replace('export function', 'function')
                wrapped_content = f"try {{\n{cleaned}\n}} catch (e) {{ console.error('Error loading plugin {module_info['plugin']} - {os.path.basename(full_path)}:', e); }}"
                all_js_code.append(f"// --- Injected Plugin '{module_info['plugin']}': {os.path.basename(full_path)} ---\n{wrapped_content}")
                print(f"✅ Loaded plugin JS: {module_info['plugin']} - {os.path.basename(full_path)}")
            except Exception as e:
                print(f"⚠️ Error while loading plugin JS for {engine_name}: {e}")

        combined = "\n\n".join(all_js_code)
        # Cache the combined result for this set of engines
        try:
            self._js_utils_cache[cache_key] = combined
        except Exception:
            # If for some reason the key isn't hashable, skip caching silently
            pass

        return combined

    def _analyze_required_js_engines(self, widget_tree: Widget, result: 'ReconciliationResult') -> set:
        """
        Analyzes the widget tree and reconciliation result to determine which JS engines are needed.
        
        :param widget_tree: The built widget tree
        :param result: Reconciliation result with rendered map and initializers
        :return: Set of required JS engine names
        """
        required_engines = set()

        # Check reconciliation result for JS initializers
        for init in result.js_initializers:
            init_type = init.get("type")
            debug_print('init_type: ', init_type)
            if init_type == "ResponsiveClipPath":
                required_engines.update(['ResponsiveClipPath', 'generateRoundedPath', 'scalePathAbsoluteMLA'])
            elif init_type == "SimpleBar":
                # SimpleBar is external, no engine needed
                pass
            elif init_type == "_RenderableSlider":
                required_engines.add('PythraSlider')
            elif init_type == "VirtualList":
                required_engines.add('PythraVirtualList')

        # Check rendered widgets for engine requirements
        for node_data in result.new_rendered_map.values():
            props = node_data.get("props", {})
            # print('init_type: ', props)

            # Check for various initialization flags
            if props.get("init_slider"):
                required_engines.add('PythraSlider')
            if props.get("init_dropdown"):
                required_engines.add('PythraDropdown')
            if props.get("init_gesture_detector"):
                required_engines.add('PythraGestureDetector')
            if props.get("init_gradient_clip_border"):
                required_engines.add('PythraGradientClipPath')
            if props.get("init_virtual_list"):
                required_engines.add('PythraVirtualList')
            if props.get("init_virtual_grid"):
                required_engines.add('PythraVirtualGrid')
            if props.get("init_textfield"):
                required_engines.add('PythraTextField')
            if props.get("responsive_clip_path"):
                required_engines.update(['ResponsiveClipPath', 'generateRoundedPath', 'scalePathAbsoluteMLA'])

            # Check for js_init configuration
            js_init = props.get("js_init")
            if js_init and isinstance(js_init, dict):
                # engine_name = js_init.get("engine")
                # print(engine_name)
                if engine_name:
                    required_engines.add(engine_name)
            if props.get("_js_init"):
                engine_name = props["_js_init"].get("engine")
                # print(engine_name)
                if engine_name:
                    required_engines.add(engine_name)

        # Check for ClipPath widgets (which need ResponsiveClipPath)
        self._check_widget_for_clip_path(widget_tree, required_engines)

        return required_engines

    def _check_widget_for_clip_path(self, widget: Widget, required_engines: set):
        """
        Recursively checks widget tree for ClipPath widgets that need JS engines.
        """
        if widget is None:
            return

        # Check if this is a ClipPath widget
        widget_class_name = widget.__class__.__name__
        if widget_class_name == 'ClipPath':
            # ClipPath widgets need the path generation engines
            required_engines.update(['ResponsiveClipPath', 'generateRoundedPath', 'scalePathAbsoluteMLA'])

        # Recursively check children
        if hasattr(widget, 'get_children'):
            for child in widget.get_children():
                self._check_widget_for_clip_path(child, required_engines)

    def request_reconciliation(self, state_instance: State):
        """Called by State.setState to schedule a UI update."""
        self._pending_state_updates.add(state_instance)

        if not self._reconciliation_requested:
            self._reconciliation_requested = True
            QTimer.singleShot(0, self._process_reconciliation)

    def _process_reconciliation(self):
        """
        Performs a targeted, high-performance reconciliation cycle for only the
        widgets whose state has changed.
        """
        self._reconciliation_requested = False
        if not self.window:
            print("Error: Window not available for reconciliation.")
            return

        if hasattr(self.window, "is_document_ready") and not self.window.is_document_ready():
            from PySide6.QtCore import QTimer
            # document is not ready yet, defer reconciliation so patches are not lost into the void
            # debug_print("⏳ PyThra Framework | Document not ready, deferring UI update cycle...")
            self._reconciliation_requested = True
            QTimer.singleShot(50, self._process_reconciliation)
            return

        is_debug = getattr(self, 'config', None) and self.config.get('Debug', False)
        profiler = None
        if is_debug:
            try:
                import cProfile
                profiler = cProfile.Profile()
                profiler.enable()
            except (ValueError, RuntimeError, ImportError):
                # Profiling might already be active or unsupported in some environments
                profiler = None

        print("\n🔄 PyThra Framework | Processing Smart UI Update Cycle...")
        start_time = time.time()

        main_context_map = self.reconciler.get_map_for_context("main")
        all_patches = []
        all_new_callbacks = {}
        all_active_css_details = {}

        # --- NEW: Track required engines for this entire update cycle ---
        all_required_engines_this_cycle = set()
        all_js_initializers = []

        # Fix A: Copy and clear to allow setState calls during iteration
        updates = list(self._pending_state_updates)
        self._pending_state_updates.clear()

        for state_instance in updates:
            widget_to_rebuild = state_instance.get_widget()
            if not widget_to_rebuild:
                print(f"Warning: Widget for state {state_instance} lost. Skipping update.")
                continue

            widget_key = widget_to_rebuild.get_unique_id()
            old_widget_data = main_context_map.get(widget_key)

            parent_html_id = "root-container"
            if old_widget_data:
                parent_html_id = old_widget_data["parent_html_id"]
            elif widget_to_rebuild is not self.root_widget:
                print(f"Error: Could not find previous state for widget {widget_key}. A full rebuild may be required.")
                continue

            # Use __str_key__ if available (for Key objects), otherwise fallback to str (for UUID strings)
            widget_id_str = widget_key.__str_key__() if hasattr(widget_key, '__str_key__') else str(widget_key)
            print(f"🔧 PyThra Framework | Updating: {widget_to_rebuild.__class__.__name__} (ID: {widget_id_str[:8]}...)")

            new_subtree = self._build_widget_tree(
                widget_to_rebuild, context_map=main_context_map
            )
            subtree_result = self.reconciler.reconcile(
                previous_map=main_context_map,
                new_widget_root=new_subtree,
                parent_html_id=parent_html_id,
                old_root_key=widget_key,
                is_partial_reconciliation=True
            )

            all_patches.extend(subtree_result.patches)
            all_new_callbacks.update(subtree_result.registered_callbacks)
            all_active_css_details.update(subtree_result.active_css_details)
            main_context_map.update(subtree_result.new_rendered_map)

            # --- NEW: Analyze this subtree and aggregate required engines ---
            required_in_subtree = self._analyze_required_js_engines(new_subtree, subtree_result)
            all_required_engines_this_cycle.update(required_in_subtree)
            all_js_initializers.extend(subtree_result.js_initializers)
            # --- END NEW ---

        for cb_id, cb_func in all_new_callbacks.items():
            self.api.register_callback(cb_id, cb_func)

        # --- NEW: DYNAMIC JS ENGINE INJECTION LOGIC ---
        js_injection_script = ""
        newly_required_engines = all_required_engines_this_cycle - self._loaded_js_engines

        if newly_required_engines:
            print(f"🚀 PyThra Framework | Dynamically loading {len(newly_required_engines)} new JS engine(s): {newly_required_engines}")
            js_injection_script = self._get_js_utility_functions(newly_required_engines)
            self._loaded_js_engines.update(newly_required_engines)
        # --- END OF NEW LOGIC ---

        # Defensive: also regenerate CSS when any patch modifies css_class,
        # even if _collect_details wasn't called (e.g. Cython path).
        css_changed_in_patches = any(
            p.action in ("UPDATE", "REPLACE", "INSERT")
            and "css_class" in (p.data.get("props") or {})
            for p in all_patches
        )
        new_css_keys = set(all_active_css_details.keys())
        css_update_script = ""
        if (
            css_changed_in_patches
            or not hasattr(self, "_last_css_keys")
            or self._last_css_keys != new_css_keys
        ):
            print("🎨 PyThra Framework | CSS styles changed - Updating stylesheet...")
            full_css_details = {}
            for data in main_context_map.values():
                if "css_class" in data["props"] and hasattr(
                    data["widget_instance"], "style_key"
                ):
                    for css_class in data["props"]["css_class"].split():
                        full_css_details[css_class] = (
                            type(data["widget_instance"]).generate_css_rule,
                            data["widget_instance"].style_key,
                        )
            css_rules = self._generate_css_from_details(full_css_details)
            css_update_script = self._generate_css_update_script(css_rules)
            self._last_css_keys = new_css_keys
        else:
            print("✅ PyThra Framework | CSS styles unchanged - Skipping regeneration")

        dom_patch_script = self._generate_dom_patch_script(all_patches, js_initializers=all_js_initializers)

        # --- CRITICAL: Prepend the JS injection script to the DOM patches ---
        combined_script = (js_injection_script + "\n" + css_update_script + "\n" + dom_patch_script).strip()

        if combined_script:
            print(f"🛠️  PyThra Framework | Applying {len(all_patches)} UI changes to app...")
            debug_print(f"📝 PyThra Framework | Patch Details: {[f'{p.action}({p.html_id[:8]}...)' for p in all_patches]}")
            self.window.evaluate_js(self.id, combined_script)
        else:
            print("✨ PyThra Framework | UI is up-to-date - No changes needed")

        # Fix A: Already cleared at the start to catch concurrent setState calls

        end_time = time.time()
        cycle_duration = end_time - start_time
        fps = 1.0 / cycle_duration if cycle_duration > 0 else float('inf')

        print(f"🎉 PyThra Framework | UI Update Complete! at (⏱️ {cycle_duration:.4f}s) ({(cycle_duration * 1000):.2f}ms) ({fps:.2f} FPS)")

        if profiler and is_debug:
            profiler.disable()
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(20)
            print("\n--- cProfile Report ---")
            print(s.getvalue())
            print("--- End of Report ---\n")

    # --- Widget Tree Building ---
    def build_subtree_async(self, widget: Optional[Widget]):
        """
        Builds the widget subtree in a background thread to prepare for navigation.
        
        This sets `_preloaded = True` on the widget when complete.
        """
        if not widget:
            return

        def _worker():
            try:
                # print(f"🧵 Starting background build for {widget}...")
                self._build_widget_tree(widget, context_map={})
                widget._preloaded = True
                # print(f"✅ Background build complete for {widget}")
            except Exception as e:
                print(f"⚠️ Background build failed: {e}")

        import threading
        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _build_widget_tree(
        self, widget: Optional[Widget], context_map: Optional[Dict] = None
    ) -> Optional[Widget]:
        """
        The "Widget Tree Builder" - converts your nested widgets into a complete tree structure.
        
        Think of this like building a family tree, but for widgets:
        - Each widget might have children (other widgets inside it)
        - StatefulWidgets need special handling (they have changing data)
        - StatelessWidgets are simpler (they just display things)
        
        What this method does:
        1. **StatelessWidget**: Calls its build() method to get its child widget
        2. **StatefulWidget**: Gets its current state, calls state.build() to get child
        3. **Regular Widget**: Just processes any children it already has
        4. **Recursive**: Does this for every widget and all their children
        
        Args:
            widget: The widget to build (could be any type of widget)
            
        Returns:
            The same widget, but with all its children properly built and connected
            
        Example Widget Tree:
        ```
        Scaffold (StatelessWidget)
        └─ Column (Regular Widget)
            ├─ Text("Hello") (Regular Widget)
            └─ Counter (StatefulWidget)
                └─ Text("Count: 5") (Built from Counter's state)
        ```
        
        This method makes sure every widget in your tree is "ready to render".
        """
        if widget is None:
            return None

        # --- OPTIMIZATION: Check for preloaded subtree ---
        # If this widget was built in the background, use the prebuilt result
        # and clear the flag to ensure future updates rebuild normally.
        if getattr(widget, '_preloaded', False):
            # print(f"🚀 Using preloaded subtree for {widget}")
            widget._preloaded = False
            return widget

        # --- THIS IS THE FIX ---
        # Handle StatelessWidget and StatefulWidget with the same pattern.
        if isinstance(widget, StatelessWidget):
            # 1. Build the child widget from the StatelessWidget.
            built_child = widget.build()
            # 2. Recursively process the built child to build its own subtree.
            processed_child = self._build_widget_tree(built_child, context_map)
            # 3. CRITICAL: The StatelessWidget's children list becomes the processed child.
            #    This keeps the StatelessWidget in the tree as the parent.
            widget._children = [processed_child] if processed_child else []
            return widget # Return the original StatelessWidget
        # --- END OF FIX ---

        if isinstance(widget, StatefulWidget):
            state = widget.get_state()

            # Attempt to rescue state from context_map if no state exists yet
            if not state:
                if context_map:
                    widget_key = widget.get_unique_id()
                    old_node = context_map.get(widget_key)
                    if old_node:
                        old_widget = old_node.get("widget_instance")
                        if old_widget and type(old_widget) == type(widget):
                            old_state = old_widget.get_state()
                            if old_state:
                                widget._state = old_state
                                old_state._set_widget(widget)
                                old_state.didUpdateWidget(old_widget, widget)
                                state = old_state

            # If still no state (first render), create it fresh
            if not state:
                state = widget.createState()
                widget._state = state
                state._set_widget(widget)
                state.initState()

            # Build the child widget from the state.
            built_child = state.build()

            # Recursively process the built child to build its own subtree.
            processed_child = self._build_widget_tree(built_child, context_map)

            # CRITICAL: The StatefulWidget's children list becomes the *single* processed child.
            # This keeps the StatefulWidget as the parent node in the tree.
            widget._children = [processed_child] if processed_child else []

            # Return the original StatefulWidget, now with its subtree correctly built.
            return widget

        # For regular widgets, just recurse on their children.
        else:
            if hasattr(widget, "get_children"):
                new_children = []
                for child in widget.get_children():
                    # Recursively build each child.
                    built_child = self._build_widget_tree(child, context_map)
                    if built_child:
                        new_children.append(built_child)
                # Replace the old children list with the newly built one.
                widget._children = new_children
            return widget

    # --- HTML and CSS Generation ---

    # --- ADD THIS NEW METHOD ---
    def find_ancestor_state_of_type(self, start_widget: Widget, state_type: type) -> Optional[State]:
        """
        Traverses up the widget tree from a given widget to find the state
        of the nearest ancestor that is an instance of a specific StatefulWidget type,
        or whose State is of state_type.
        """
        main_context_map = self.reconciler.get_map_for_context("main")
        if not main_context_map:
            return None

        current_key = start_widget.get_unique_id()

        # Loop up the tree using parent references stored in the reconciler's map
        while current_key in main_context_map:
            node_data = main_context_map[current_key]
            widget_instance = node_data.get('widget_instance')

            # Check if the current widget's state is the type we're looking for
            if isinstance(widget_instance, StatefulWidget):
                state = widget_instance.get_state()
                if isinstance(state, state_type):
                    return state

            # Move up to the parent
            parent_key = node_data.get('parent_key') # We'll need to add this to the map
            if not parent_key:
                break
            current_key = parent_key

        return None

    def _generate_html_from_map(
        self, root_key: Optional[Union[Key, str]], rendered_map: Dict # pyright: ignore[reportInvalidTypeForm]
    ) -> str:
        """Generates the full HTML string by recursively traversing the flat rendered_map."""
        if root_key is None or root_key not in rendered_map:
            return ""

        node_data = rendered_map.get(root_key)
        if not node_data:
            return ""

        # A StatefulWidget doesn't render itself, so we render its child.
        if node_data["widget_type"] == "StatefulWidget":
            child_keys = node_data.get("children_keys", [])
            if child_keys:
                return self._generate_html_from_map(child_keys[0], rendered_map)
            return ""

        html_id = node_data["html_id"]
        props = node_data["props"]
        widget_instance = node_data["widget_instance"]


        stub = self.reconciler._generate_html_stub(widget_instance, html_id, props)
        # print("stub: ", stub)

        children_html = "".join(
            self._generate_html_from_map(child_key, rendered_map)
            for child_key in node_data.get("children_keys", [])
        )

        if "{children}" in stub:
            return stub.replace("{children}", children_html)
        
        if ">" in stub and "</" in stub:
            tag = self.reconciler._get_widget_render_tag(widget_instance)
            closing_tag = f"</{tag}>"
            if stub.endswith(closing_tag):
                content_part = stub[: -len(closing_tag)]
                return f"{content_part}{children_html}{closing_tag}"

        return stub

    def _generate_css_from_details(
        self, css_details: Dict[str, Tuple[Callable, Any]]
    ) -> str:
        """Generates CSS rules directly from the details collected by the Reconciler."""
        all_rules = []
        for css_class, (generator_func, style_key) in css_details.items():
            try:
                rule = generator_func(style_key, css_class)
                if rule:
                    all_rules.append(rule)
                    # print("Rule: ",rule)
            except Exception as e:
                import traceback

                print(f"💥 ERROR generating CSS for class '{css_class}': {e}")
                traceback.print_exc()

        debug_print(f"🪄  PyThra Framework | Generated CSS for {len(all_rules)} active shared classes.")
        # print(f"Rules: {all_rules}")
        return "\n".join(all_rules)

    # --- Script Generation and File Writing ---

    def _generate_css_update_script(self, css_rules: str) -> str:
        """Generates JS to update the <style id="dynamic-styles"> tag."""
        escaped_css = _dumps(css_rules).replace("`", "\\`")
        return f"""
            var styleSheet = document.getElementById('dynamic-styles');
            var newCss = {escaped_css};
            if (styleSheet.textContent !== newCss) {{
                 styleSheet.textContent = newCss;
            }}
        """

    def _build_path_from_commands(self, commands_data: List[Dict]) -> str:
        """
        Builds an SVG path data string from serialized command data.
        This is the Python-side logic that mirrors your JS path generators.
        """
        return ""

    def _generate_dom_patch_script(self, patches: List[Patch], js_initializers=None) -> str: # type: ignore
        """
        Converts the list of Patch objects into a JSON payload for the JS Bridge.
        
        OPTIMIZATION: Instead of generating thousands of lines of JS code strings,
        we now generate a single lightweight JSON object and let the 
        client-side 'PythraBridge' handle the DOM manipulation.
        """
        if not patches:
            return ""

        # Prepare the data-only list for serialization
        patches_data = []

        for patch in patches:
            # We convert the dataclass to a simple dict.
            # _dumps will handle recursive serialization of widgets/functions implicitly.
            patch_dict = {
                "action": patch.action,
                "html_id": patch.html_id,
                "data": patch.data
            }
            patches_data.append(patch_dict)

        # Fast serialization using orjson (if available)
        json_payload = _dumps(patches_data)

        # Log payload size in debug mode
        if getattr(self, 'config', None) and self.config.get('Debug'):
            print(f"📦 Bridge Payload: {len(json_payload)} bytes")

        # The efficient bridge call
        bridge_script = f"if (window.PythraBridge) {{ PythraBridge.applyPatches({json_payload}); }}"

        if js_initializers:
            # Iterate and convert initializers (strings or dicts) into executable JS
            processed_inits = []
            for init in js_initializers:
                if isinstance(init, str):
                    processed_inits.append(init)
                elif isinstance(init, dict):
                    init_type = init.get("type")

                    if init_type == "ResponsiveClipPath":
                        # Generate JS for ResponsiveClipPath dynamic init
                        target_id = init["target_id"]
                        clip_data = init["data"]
                        blueprint_class = clip_data.get("blueprint_class", target_id)

                        if blueprint_class in self._clip_blueprint_registry:
                            continue
                        self._clip_blueprint_registry.add(blueprint_class)

                        points_json = _dumps(clip_data["points"])
                        radius_json = _dumps(clip_data["radius"])
                        ref_w_json = _dumps(clip_data["viewBox"][0])
                        ref_h_json = _dumps(clip_data["viewBox"][1])

                        processed_inits.append(f"""
                        (function() {{
                            if (!window._pythra_instances['{blueprint_class}']) {{
                                const points = {points_json}.map(p => ({{x: p[0], y: p[1]}}));
                                const pathStr = window.generateRoundedPath(points, {radius_json});
                                if (window.ResponsiveClipPath) {{
                                    window._pythra_instances['{blueprint_class}'] = new window.ResponsiveClipPath(
                                        '.{blueprint_class}', 
                                        pathStr, 
                                        {ref_w_json}, 
                                        {ref_h_json}, 
                                        {{ uniformArc: true, decimalPlaces: 2 }}
                                    );
                                }}
                            }}
                        }})();
                        """)

                    elif init_type == "SimpleBar":
                        target_id = init["target_id"]
                        options_json = _dumps(init.get("options", {}))
                        processed_inits.append(f"""
                        setTimeout(() => {{
                            const el = document.getElementById('{target_id}');
                            if (el && !el.simplebar) {{
                                new SimpleBar(el, {options_json});
                            }}
                        }}, 0);
                        """)

                    elif init_type == "slider":
                        target_id = init["target_id"]
                        options_json = _dumps(init.get("data", {}).get("slider_options", {}))
                        processed_inits.append(f"""
                        setTimeout(() => {{
                            if (typeof PythraSlider !== 'undefined') {{
                                window._pythra_instances['{target_id}'] = new PythraSlider('{target_id}', {options_json});
                            }}
                        }}, 0);
                        """)

                    elif init_type == "virtual_list":
                        target_id = init["target_id"]
                        debug_print("Virtual List: ", target_id)
                        data = init.get("data", {})
                        widget_instance =data['widget_instance']
                        if widget_instance and widget_instance.key:
                            widget_key_val = widget_instance.key.value
                        else:
                            # Fallback, though widgets with controllers should always have keys.
                            widget_key_val = html_id # pyright: ignore[reportUndefinedVariable]
                        # print(data)
                        instance_name = f"{widget_key_val}_vlist"
                        estimated_height = data.get("estimated_height", 50) # Fallback if missing
                        item_count = data.get("item_count", 0)
                        options_json = _dumps(data['virtual_list_options'])
                        processed_inits.append(f"""
                        console.log("Vlist re initialized {target_id} instance name: {instance_name}");
                         setTimeout(() => {{
                             if (typeof PythraVirtualList !== 'undefined') {{
                                 window._pythra_instances['{instance_name}'] = new PythraVirtualList(
                                '{target_id}', 
                                {options_json}
                                );
                             }}
                         }}, 0);
                         """)

                    elif init_type == "dropdown":
                        target_id = init["target_id"]
                        # The 'data' dict usually contains 'dropdown_options' based on reconciler logic
                        options_json = _dumps(init.get("data", {}).get("dropdown_options", {}))
                        processed_inits.append(f"""
                        setTimeout(() => {{
                            if (typeof PythraDropdown !== 'undefined') {{
                                window._pythra_instances['{target_id}'] = new PythraDropdown('{target_id}', {options_json});
                            }}
                        }}, 0);
                        """)

                    elif init_type == "gesture_detector":
                        target_id = init["target_id"]
                        options_json = _dumps(init.get("data", {}).get("gesture_options", {}))
                        processed_inits.append(f"""
                        setTimeout(() => {{
                            if (typeof PythraGestureDetector !== 'undefined') {{
                                window._pythra_instances['{target_id}'] = new PythraGestureDetector('{target_id}', {options_json});
                            }}
                        }}, 0);
                        """)

                    elif init_type == "gradient_clip_border":
                        target_id = init["target_id"]
                        options_json = _dumps(init.get("data", {}).get("gradient_clip_options", {}))
                        processed_inits.append(f"""
                        setTimeout(() => {{
                            if (typeof PythraGradientClipPath !== 'undefined') {{
                                window._pythra_instances['{target_id}'] = new PythraGradientClipPath('{target_id}', {options_json});
                            }}
                        }}, 0);
                        """)

                    # Reconciler stores generic JS init info with the type set to the engine name
                    # We can detect this pattern by checking if 'engine' is in the init dict or relying on fallback.
                    # However, Reconciler line 499 sets: "type": js_init_data['engine']
                    # So we should probably handle that case by exclusion or a specific check?
                    # Actually, the user's snippet showed:
                    # elif init_type == "_js_init": ...
                    # But Reconciler line 499 sets type=engine_name.
                    # Let's check init['data'] to see if it has 'engine' for the generic case.
                    elif isinstance(init.get("data"), dict) and "engine" in init["data"]:
                        # This matches the generic _js_init pattern from Reconciler line 492+
                        js_init_data = init["data"]
                        target_id = init["target_id"]
                        engine_name = js_init_data.get("engine")
                        instance_name = js_init_data.get("instance_name")
                        options_json = _dumps(js_init_data.get("options", {}))
                        # print("init data: ", js_init_data)

                        processed_inits.append(f"""
                        setTimeout(() => {{
                            const targetElement = document.getElementById('{target_id}');
                            if (targetElement && typeof window['{engine_name}'] !== 'undefined') {{
                                window._pythra_instances = window._pythra_instances || {{}};
                                if (window._pythra_instances['{instance_name}'] && typeof window._pythra_instances['{instance_name}'].destroy === 'function') {{
                                    window._pythra_instances['{instance_name}'].destroy();
                                }}
                                window._pythra_instances['{instance_name}'] = new window['{engine_name}'](targetElement, {options_json});
                            }}
                        }}, 0);
                        """)

            if processed_inits:
                bridge_script += "\n" + "\n".join(processed_inits)

        return bridge_script

    def _generate_initial_js_script(self, result: 'ReconciliationResult', required_engines: set = None) -> str:
        """Generates a script tag to run initializations after the DOM loads with optimized JS loading."""
        if not result.js_initializers:
            # Even if no initializers, we might need engines for widgets
            if not required_engines:
                return ""

        js_commands = []
        imports = set()

        for node_data in result.new_rendered_map.values():
            props = node_data.get("props", {})
            html_id = node_data.get("html_id")
            # print(">>>init_slider<<<", html_id)
            widget_instance = node_data.get("widget_instance")

            # --- NEW: Generic JS Initializer ---
            js_init_data = props.get("_js_init")
            if js_init_data:
                # print("js_init_data:: ", js_init_data)
                engine_name = js_init_data.get("engine")
                instance_name = js_init_data.get("instance_name")
                options = js_init_data.get("options", {})

                # Find the module path from the plugin manifest
                js_module_info = self._find_js_module(engine_name)
                engine_to_file_map = self._engine_to_file_map
                # print("js_module_info: ", js_module_info)
                if js_module_info:
                    # Check if path is absolute
                    module_path = js_module_info['path']
                    if not os.path.isabs(module_path):
                        module_path = os.path.join(self.project_root, module_path)
                    path_js = module_path
                    imports.add(f"import {{ {engine_name} }} from '{path_js}';")

                    options_json = _dumps(options)
                    js_commands.append(f"""
                    function waitForAndInit(className, initCallback) {{
                            const interval = setInterval(() => {{
                                // Check if the class is now available on the window object
                                if (typeof window[className] === 'function') {{
                                    clearInterval(interval); // Stop checking
                                    console.log(`Class ${{className}} is defined. Initializing...`);
                                    initCallback(); // Run the initialization code
                                }} else {{
                                    console.log(`Waiting for class ${{className}}...`);
                                }}
                            }}, 100); // Check every 100ms
                        }}
                        waitForAndInit('{engine_name}', () => {{
                            window._pythra_instances['{instance_name}'] = new {engine_name}(
                                document.getElementById('{html_id}'),
                                {options_json}
                            );
                            
                        }});
                        """)

                elif engine_name.endswith('Internal'):
                    engine_path = engine_to_file_map.get(engine_name, '').replace('render', '.')
                    imports.add(f"import {{ {engine_name} }} from '{engine_path}';")

                    options_json = _dumps(options)
                    js_commands.append(f"""
                    function waitForAndInit(className, initCallback) {{
                            const interval = setInterval(() => {{
                                // Check if the class is now available on the window object
                                if (typeof window[className] === 'function') {{
                                    clearInterval(interval); // Stop checking
                                    console.log(`Class ${{className}} is defined. Initializing...`);
                                    initCallback(); // Run the initialization code
                                }} else {{
                                    console.log(`Waiting for class ${{className}}...`);
                                }}
                            }}, 100); // Check every 100ms
                        }}
                        waitForAndInit('{engine_name}', () => {{
                            window._pythra_instances['{instance_name}'] = new {engine_name}(
                                document.getElementById('{html_id}'),
                                {options_json}
                            );
                            
                        }});
                        """)
                else:
                    print(f"⚠️ Warning: JS engine '{engine_name}' not found in any plugin manifest.")
            # --- END OF NEW LOGIC ---

            # --- THE FIX ---
            # Use the widget's key for a stable instance name.
            if widget_instance and widget_instance.key:
                widget_key_val = widget_instance.key.__str_key__() if hasattr(widget_instance.key, '__str_key__') else str(widget_instance.key)
            else:
                # Fallback, though widgets with controllers should always have keys.
                widget_key_val = html_id
            # --- END OF FIX ---

            # --- ADD THIS BLOCK ---
            if props.get("init_gradient_clip_border"):
                imports.add("import { PythraGradientClipPath } from './js/gradient_border.js';")
                imports.add("import { generateRoundedPath } from './js/pathGenerator.js';")
                options = props.get("gradient_clip_options", {})
                options_json = _dumps(options)
                js_commands.append(f"""window._pythra_instances['{html_id}'] = new PythraGradientClipPath('{html_id}', {options_json});""")
            # --- END OF BLOCK ---

            # --- ADD THIS BLOCK ---
            # --- SIMPLIFIED VLIST LOGIC ---
            if props.get("init_virtual_list"):
                # print("Initializing Virtual List...")
                imports.add("import { PythraVirtualList } from './js/virtual_list.js';")
                options = props.get("virtual_list_options", {})
                options_json = _dumps(options)
                # Use the stable key for the instance name
                instance_name = f"{widget_key_val}_vlist"
                # No more checks or timeouts. We just instantiate our engine.
                js_commands.append(f"""
                function waitForAndInit(className, initCallback) {{
                            const interval = setInterval(() => {{
                                // Check if the class is now available on the window object
                                if (typeof window[className] === 'function') {{
                                    clearInterval(interval); // Stop checking
                                    console.log(`Class ${{className}} is defined. Initializing...`);
                                    initCallback(); // Run the initialization code
                                }} else {{
                                    console.log(`Waiting for class ${{className}}...`);
                                }}
                            }}, 100); // Check every 100ms
                        }}
                        waitForAndInit('PythraVirtualList', () => {{
                            window._pythra_instances['{instance_name}'] = new PythraVirtualList(
                                '{html_id}', 
                                {options_json}
                                );
                        }});
                """)
            # --- END OF CHANGE ---

            # --- VIRTUAL GRID LOGIC ---
            if props.get("init_virtual_grid"):
                debug_print("Initializing Virtual Grid...")
                imports.add("import { PythraVirtualGrid } from './js/virtual_grid.js';")
                options = props.get("virtual_grid_options", {})
                # print("options", options)
                options_json = _dumps(options)
                # Use the stable key for the instance name
                instance_name = f"{widget_key_val}_vgrid"

                js_commands.append(f"""
                console.log('Initializing Virtual Grid...');
                function waitForAndInit(className, initCallback) {{
                            const interval = setInterval(() => {{
                                if (typeof window[className] === 'function') {{
                                    clearInterval(interval); 
                                    initCallback(); 
                                }}
                            }}, 100); 
                        }}
                        waitForAndInit('PythraVirtualGrid', () => {{
                            window._pythra_instances['{instance_name}'] = new PythraVirtualGrid(
                                '{html_id}', 
                                {options_json}
                                );
                        }});
                """)
            # --- END VIRTUAL GRID LOGIC ---
            # --- END OF BLOCK ---

            # --- ADD THIS BLOCK ---
            if props.get("init_gesture_detector"):
                imports.add("import { PythraGestureDetector } from './js/gesture_detector.js';")
                options = props.get("gesture_options", {})
                options_json = _dumps(options)
                debug_print("options: ", options_json)
                js_commands.append(f"window._pythra_instances['{html_id}'] = new PythraGestureDetector('{html_id}', {options_json});")
            # --- END OF BLOCK ---

            # --- ADD THIS BLOCK ---
            if props.get("init_dropdown"):
                imports.add("import { PythraDropdown } from './js/dropdown.js';")
                options = props.get("dropdown_options", {})
                options_json = _dumps(options)
                js_commands.append(f"window._pythra_instances['{html_id}'] = new PythraDropdown('{html_id}', {options_json});")
            # --- END OF BLOCK ---

            if props.get("init_textfield"):
                imports.add("import { PythraTextField } from './js/textfield.js';")
                options = props.get("textfield_options", {})
                options_json = _dumps(options)
                js_commands.append(f"""
                    if (typeof PythraTextField !== 'undefined') {{
                        if (!window._pythra_instances['{html_id}']) {{
                            window._pythra_instances['{html_id}'] = new PythraTextField('{html_id}', {options_json});
                        }}
                    }}
                """)

            # Check for our new Slider's flag
            if props.get("init_slider"):
                # print(">>>init_slider<<<", html_id)
                imports.add("import { PythraSlider } from './js/slider.js';")
                options = props.get("slider_options", {})
                options_json = _dumps(options)

                # Generate the JS command to instantiate the slider engine
                js_commands.append(f"""
                    if (typeof PythraSlider !== 'undefined') {{
                        // Make sure we don't re-initialize if it somehow already exists
                        if (!window._pythra_instances['{html_id}']) {{
                            console.log('Initializing PythraSlider for #{html_id}');
                            window._pythra_instances['{html_id}'] = new PythraSlider('{html_id}', {options_json});
                        }}
                    }} else {{
                        console.error('PythraSlider class not found. Make sure slider.js is included.');
                    }}
                """)
        # --- END OF NEW LOGIC ---
        # Your initializer logic for ClipPath etc. goes here if needed
        for init in result.js_initializers:
            self._generate_js_for_initializer(init, js_commands, imports)

        # --- INCLUDE JS UTILITIES IN INITIAL RENDER ---
        # Get JS utilities for initial render so all functions are available
        # Get the required engines from the current reconciliation result
        js_utilities = self._get_js_utility_functions(required_engines)

        full_script = f"""
        <script>
            document.addEventListener('DOMContentLoaded', () => {{
                window._pythra_instances = window._pythra_instances || {{}};
                try {{
                    // First, DEFINE all our JS classes and functions
                    {js_utilities}
                    
                    // Then, RUN the initialization commands that were generated
                    {''.join(js_commands)}

                }} catch (e) {{
                    console.error("Error running Pythra initializers:", e);
                }}
            }});
        </script>
        """
        return full_script

    def _generate_js_for_initializer(self, init: Dict[str, Any], js_commands: List[str], imports: Set[str]):
        """Generates JS code for a single initializer."""
        init_type = init.get("type")
        target_id = init.get("target_id")

        # --- SIMPLEBAR ---
        if init_type == "SimpleBar":
            options_json = _dumps(init.get("options", {}))
            js_commands.append(
                f"""
                const el_{target_id} = document.getElementById('{target_id}');
                if (el_{target_id} && !el_{target_id}.simplebar) {{
                    new SimpleBar(el_{target_id}, {options_json} );
                }};
            """
            )

        # --- SLIDER ---
        elif init_type == "_RenderableSlider":
            options_json = _dumps(init.get("options", {}))
            js_commands.append(f"""
                if (typeof PythraSlider !== 'undefined') {{
                    window._pythra_instances['{target_id}'] = new PythraSlider('{target_id}', {options_json});
                }} else {{
                    console.error('PythraSlider class not found.');
                }}
            """)

        # --- VIRTUAL LIST ---
        elif init_type == "VirtualList":
            estimated_height = init["estimated_height"]
            item_count = init["item_count"]
            js_commands.append(
                f"""
                new VirtualList(
                    "{target_id}",
                    {item_count},
                    {estimated_height},
                    (i) => {{
                        const div = document.createElement("div");
                        div.dataset.index = i;
                        return div;
                    }}
                );
            """
            )

        # --- VIRTUAL GRID ---
        elif init_type == "VirtualGrid":
            estimated_height = init["estimated_height"]
            item_count = init["item_count"]
            js_commands.append(
                f"""
                new VirtualGrid(
                    "{target_id}",
                    {item_count},
                    {estimated_height},
                    (i) => {{
                        const div = document.createElement("div");
                        div.dataset.index = i;
                        return div;
                    }}
                );
            """
            )

        # --- CLIP PATH ---
        elif init_type == "ResponsiveClipPath":
            imports.add("import { generateRoundedPath } from './js/pathGenerator.js';")
            imports.add("import { ResponsiveClipPath } from './js/clipPathUtils.js';")

            clip_data = init["data"]
            blueprint_class = clip_data.get("blueprint_class", target_id)

            if blueprint_class in self._clip_blueprint_registry:
                return # Skip redundant initializations for identically sized ClipPaths
            self._clip_blueprint_registry.add(blueprint_class)

            points_json = _dumps(clip_data["points"])
            radius_json = _dumps(clip_data["radius"])
            ref_w_json = _dumps(clip_data["viewBox"][0])
            ref_h_json = _dumps(clip_data["viewBox"][1])
            bp_var = blueprint_class.replace("-", "_")

            js_commands.append(f"""
                if (!window._pythra_instances['{blueprint_class}']) {{
                    const pointsForGenerator_{bp_var} = {points_json}.map(p => ({{x: p[0], y: p[1]}}));
                    const initialPathString_{bp_var} = window.generateRoundedPath(pointsForGenerator_{bp_var}, {radius_json});
                    
                    window._pythra_instances['{blueprint_class}'] = new window.ResponsiveClipPath(
                        '.{blueprint_class}', 
                        initialPathString_{bp_var}, 
                        {ref_w_json}, 
                        {ref_h_json}, 
                        {{ uniformArc: true, decimalPlaces: 2 }}
                    );
                }}
            """)

    # Helper method to find JS modules from discovered plugins
    def _find_js_module(self, engine_name: str) -> Optional[Dict]:
        """Find a JS module by its engine name"""
        # print("Looking for JS module:", engine_name)
        # print("Plugins:", self.plugins)
        # print("Plugin JS Modules:", self.plugin_js_modules)
        if engine_name.endswith('Internal'):
            # print(f"{engine_name} is an internal engine")
            return None

        # First check the new-style plugin_js_modules
        if engine_name in self.plugin_js_modules:
            module_info = self.plugin_js_modules[engine_name]
            print(f"✅ Found module in plugin_js_modules: {module_info}")
            return module_info

        # Fall back to old-style plugins dict
        for plugin_name, plugin_info in self.plugins.items():
            modules = plugin_info.get("js_modules", {})
            print(f"Checking plugin {plugin_name} modules:", modules)
            if engine_name in modules:
                return {
                    "plugin": plugin_name,
                    "path": f"/plugins/{plugin_name}/{modules[engine_name]}"
                }

        # If not found, look in package manager's loaded packages
        if hasattr(self, 'package_manager'):
            loaded_packages = self.package_manager.get_loaded_packages()
            print("Checking loaded packages:", loaded_packages.keys())
            for pkg_name, pkg_info in loaded_packages.items():
                js_modules = pkg_info.manifest.js_modules
                if engine_name in js_modules:
                    module_path = pkg_info.get_js_module_path(engine_name)
                    if module_path:
                        return {
                            "plugin": pkg_name,
                            "path": str(module_path)
                        }

        print(f"⚠️ No JS module found for engine: {engine_name}")
        return None

    def _generate_embedded_font_css(self) -> str:
        """
        Reads TTF files from assets/fonts, converts to Base64, and returns CSS.
        This eliminates FOUT (Flash of Unstyled Text) by embedding fonts directly.
        """
        if self._cached_font_css:
            return self._cached_font_css

        print("🔤 PyThra Framework | Embedding fonts into CSS for instant rendering...")

        # Map the Font Name to the Filename
        fonts_to_load = [
            ("Material Symbols Outlined", "MaterialSymbolsOutlined.ttf"),
            ("Material Symbols Rounded", "MaterialSymbolsRounded.ttf"),
            ("Material Symbols Sharp", "MaterialSymbolsSharp.ttf"),
        ]

        css_rules = []
        fonts_dir = self.assets_dir / "fonts"

        for font_family, filename in fonts_to_load:
            file_path = fonts_dir / filename

            # 1. Try to load file and converting to Base64
            if file_path.exists():
                try:
                    with open(file_path, "rb") as f:
                        # Read binary, encode to b64 bytes, decode to utf-8 string
                        b64_str = base64.b64encode(f.read()).decode("utf-8")

                    rule = f"""
@font-face {{
    font-family: '{font_family}';
    font-style: normal;
    font-weight: 100 700;
    font-display: block; /* Hides text until icon is ready */
    src: url(data:font/truetype;charset=utf-8;base64,{b64_str}) format('truetype');
}}
                    """
                    css_rules.append(rule)
                    # print(f"   ✅ Embedded {filename}")
                except Exception as e:
                    print(f"   ⚠️ Error embedding {filename}: {e}")
                    # Fallback logic below will trigger
            else:
                # 2. Fallback: Use Localhost URL if file is missing
                print(f"   ⚠️ Font file missing: {filename}. Falling back to network URL.")
                port = self.config.get('assets_server_port')
                rule = f"""
@font-face {{
    font-family: '{font_family}';
    font-style: normal;
    font-weight: 100 700;
    src: url(http://localhost:{port}/fonts/{filename}) format('truetype');
}}
                """
                css_rules.append(rule)

        self._cached_font_css = "\n".join(css_rules)
        return self._cached_font_css

    def _write_initial_files(
        self, title: str, html_content: str, initial_css_rules: str, initial_js: str
    ):
        # --- THIS IS THE NEW FONT DEFINITION CSS ---
        plugin_css_links = []
        for name, info in self.plugins.items():
            if 'css_files' in info:
                for css_file in info['css_files']:
                    # The asset server will handle this.
                    port = self.config.get('assets_server_port', 8000)
                    url_path = f"http://localhost:{port}/packages/{name}/{css_file}"
                    plugin_css_links.append(f'<link rel="stylesheet" href="{url_path}">')

        plugin_css_str = "\n    ".join(plugin_css_links)

        font_face_rules = self._generate_embedded_font_css()
        # f"""
        #  /* Define the Material Symbols fonts hosted by our server */
        #  @font-face {{
        #    font-family: 'Material Symbols Outlined';
        #    font-style: normal;
        #    font-weight: 100 700; /* The range of weights the variable font supports */
        #    src: url(http://localhost:{self.config.get('assets_server_port')}/fonts/MaterialSymbolsOutlined.ttf) format('truetype');
        #  }}

        #  @font-face {{
        #    font-family: 'Material Symbols Rounded';
        #    font-style: normal;
        #    font-weight: 100 700;
        #    src: url(http://localhost:{self.config.get('assets_server_port')}/fonts/MaterialSymbolsRounded.ttf) format('truetype');
        #  }}

        #  @font-face {{
        #    font-family: 'Material Symbols Sharp';
        #    font-style: normal;
        #    font-weight: 100 700;
        #    src: url(http://localhost:{self.config.get('assets_server_port')}/fonts/MaterialSymbolsSharp.ttf) format('truetype');
        #  }}
        #  """
        # --- END OF DEPRECATED FONT CSS ---
        # Use transparent background if video overlay is requested
        bg_color = "transparent" if getattr(self, '_video_overlay_requested', False) else "#f0f0f0"

        base_css = f"""
body {{ 
    margin: 0; 
    font-family: sans-serif; 
    background-color: {bg_color}; 
    overflow: hidden;
    user-select: none;
}}
* {{ 
    box-sizing: border-box; 
}}
#root-container, #overlay-container {{ 
    height: 100vh; 
    width: 100vw; 
    overflow: hidden; 
    position: relative;
}}
#overlay-container {{ 
    position: absolute; 
    top: 0; 
    left: 0; 
    pointer-events: none; 
}}
#overlay-container > * {{ 
    pointer-events: auto; 
}}
.custom-widget {{
    width: 100%;
    height: 100%;
}}
.custom-scrollbar::-webkit-scrollbar {{
    display: none; /* for Chrome, Safari, and Opera */
}}
.custom-scrollbar {{
    -ms-overflow-style: none;  /* for IE and Edge */
    scrollbar-width: none;  /* for Firefox */
}}

/* Fix deprecated inset-area warnings by suppressing and using position-area */
* {{
    inset-area: unset !important;  /* Remove deprecated inset-area */
}}

/* If any elements need positioning, use position-area instead */
[style*="inset-area"] {{
    inset-area: unset !important;
    /* Add position-area equivalent if needed */
}}
"""
        # Prepare the strings we may write
        css_output = base_css + font_face_rules

        # Note: remove the timestamp query param to keep the generated HTML stable
        # so we don't rewrite files every run. Dynamic updates are handled via
        # the <style id="dynamic-styles"> tag and JS patches.
    #     <link rel=\"stylesheet\" href=\"./js/scroll-bar/simplebar.min.css\" />
    # <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css\">\n
               
        html_output = (
            f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <title>{html.escape(title)}</title>
    <!-- ADD SIMPLEBAR CSS -->
    <link rel=\"stylesheet\" href=\"./js/scroll-bar/simplebar.min.css\" />
     <link id=\"base-stylesheet\" type=\"text/css\" rel=\"stylesheet\" href=\"styles.css\">\n
                <style id=\"theme-styles\">{ThemeManager.instance().current_theme.to_css_vars()}</style>\n
                <style id=\"dynamic-styles\">{initial_css_rules}</style>\n
                {self._get_js_includes()}\n
                {plugin_css_str}\n
            </head>\n<body>\n    <div id=\"root-container\">{html_content}</div>\n    <div id=\"overlay-container\"></div>\n\n    <!-- ADD SIMPLEBAR JS -->\n    <script src=\"./js/scroll-bar/simplebar.min.js\"></script>\n    <script src=\"./js/pythra_bridge.js\"></script>\n    <!-- ADD THE NEW SLIDER JS ENGINE -->\n    {initial_js}\n</body>\n</html>"""
        )

        try:
            # If we've written initial files before and cached content matches, skip writes
            if self._initial_files_written:
                css_same = (self._cached_initial_css == css_output)
                html_same = (self._cached_initial_html == html_output)
                if css_same and html_same:
                    print("✅ Initial files unchanged — skipping disk write")
                    return

            # Write CSS if different
            try:
                existing_css = None
                if self.css_file_path.exists():
                    with open(self.css_file_path, 'r', encoding='utf-8') as rc:
                        existing_css = rc.read()
                if existing_css != css_output:
                    with open(self.css_file_path, 'w', encoding='utf-8') as c:
                        c.write(css_output)
                    print(f"📝 Wrote styles to {self.css_file_path}")
                else:
                    print("✅ styles.css already up-to-date")
            except IOError as e:
                print(f"Error writing CSS file: {e}")

            # Write HTML if different
            try:
                existing_html = None
                if self.html_file_path.exists():
                    with open(self.html_file_path, 'r', encoding='utf-8') as rh:
                        existing_html = rh.read()
                if existing_html != html_output:
                    with open(self.html_file_path, 'w', encoding='utf-8') as f:
                        f.write(html_output)
                    print(f"📝 Wrote HTML to {self.html_file_path}")
                else:
                    print("✅ index.html already up-to-date")
            except IOError as e:
                print(f"Error writing HTML file: {e}")

            # Cache the written content so subsequent calls can skip I/O
            self._cached_initial_css = css_output
            self._cached_initial_html = html_output
            self._initial_files_written = True

        except Exception as e:
            print(f"Error preparing initial files: {e}")

    def _get_js_includes(self):
        """Generates standard script includes for QWebChannel and event handling."""
        return f"""
        <script src="qwebchannel.js"></script>
        <script>
            // Suppress inset-area deprecation warnings
            (function() {{
                const originalWarn = console.warn;
                console.warn = function(...args) {{
                    const message = args.join(' ');
                    if (message.includes('inset-area') || 
                        message.includes('position-area') ||
                        message.includes('has been deprecated')) {{
                        return; // Suppress these specific warnings
                    }}
                    originalWarn.apply(console, args);
                }};
            }})();
            
            document.addEventListener('DOMContentLoaded', () => {{
                new QWebChannel(qt.webChannelTransport, (channel) => {{
                    window.pywebview = channel.objects.pywebview;
                    console.log("PyWebChannel connected.");

                    // --- Client-side viewport resize detection ---
                    // ResizeObserver fires only after the DOM is loaded and the
                    // JS-Python bridge is connected, avoiding premature events.
                    const root = document.getElementById('root-container');
                    if (root) {{
                        const ro = new ResizeObserver(entries => {{
                            for (const entry of entries) {{
                                const w = Math.round(entry.contentRect.width);
                                const h = Math.round(entry.contentRect.height);
                                if (window.pywebview) {{
                                    window.pywebview.on_viewport_resize(w, h);
                                }}
                            }}
                        }});
                        ro.observe(root);
                    }}
                }});
                window.__PYTHRA_CONFIG__ = {_dumps(self.config_dict)};
                try {{
                    setFloatingLabelBg(color=getFinalSolidColor());
                }} catch (error) {{
                    console.error(error);
                }}
            }});
            function sendMessage(message) {{ if(window.pywebview) window.pywebview.send_message(message, ()=>{{}}); }}
            function handleClick(name) {{ if(window.pywebview) window.pywebview.on_pressed_str(name, ()=>{{}}); }}
            function handleClickWithArgs(callback_name, ...args) {{
                if (window.pywebview) {{
                    console.log("index", args);
                    window.pywebview.on_pressed(callback_name, ...args).then(function(response) {{
                        console.log(response);
                    }}).catch(function(error) {{
                        console.error(error);
                    }});
                }} else {{
                    console.error('pywebview is not defined');
                }}
            }}
            function handleItemTap(name, index) {{ if(window.pywebview) window.pywebview.on_item_tap(name, index, ()=>{{}}); }}
            function handleInput(name, value) {{
                if(window.pywebview) {{
                    window.pywebview.on_input_changed(name, value, ()=>{{}});
                }}
            }}
            function setFloatingLabelBg(key, color) {{
                let el;

                if (key) {{
                    el = document.querySelector(`[data-key="${{key}}"]`);
                }} else {{
                    el = document.querySelector(`[data-role="floating-label-container"]`);
                }}
                console.log("Floating label bg:", color);

                if (!el) return;

                el.style.setProperty('--ptf-bg', color);
            }}
            function getFinalSolidColor(key) {{
                function getElement(key) {{
                    if (key) {{
                        return document.querySelector(`[data-key="${{key}}"]`);
                    }} else {{
                        return document.querySelector(`[data-role="dropdown-button"]`);
                    }}
                }}

                const container = getElement(key);
                console.log(container);
                if (!container) return null;

                function parseColor(colorStr) {{
                    const matches = colorStr.match(/[\\d.]+/g);
                    if (!matches) return [255, 255, 255, 1];
                    const values = matches.map(Number);
                    if (values.length === 3) values.push(1);
                    return values;
                }}

                // Step 1: Find background behind container
                let parent = container.parentElement;
                let bgRgb = [255, 255, 255];

                while (parent) {{
                    const parentBg = window.getComputedStyle(parent).backgroundColor;

                    if (parentBg !== 'rgba(0, 0, 0, 0)' && parentBg !== 'transparent') {{
                        const parsed = parseColor(parentBg);
                        bgRgb = parsed;

                        if (parsed[3] >= 0.99) break;
                    }}

                    parent = parent.parentElement;
                }}

                // Step 2: Get container bg
                const containerBg = window.getComputedStyle(container).backgroundColor;
                const fgRgba = parseColor(containerBg);

                // Step 3: Alpha blend
                const alpha = fgRgba[3];
                const r = Math.round((fgRgba[0] * alpha) + (bgRgb[0] * (1 - alpha)));
                const g = Math.round((fgRgba[1] * alpha) + (bgRgb[1] * (1 - alpha)));
                const b = Math.round((fgRgba[2] * alpha) + (bgRgb[2] * (1 - alpha)));

                return `rgb(${{r}}, ${{g}}, ${{b}})`;
            }}
        </script>
        """