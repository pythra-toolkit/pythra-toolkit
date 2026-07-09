"""
=============================================================================
                    PYTHRA WEBWIDGET MODULE
=============================================================================

This module is the core web interface component of the PyThra Framework.
It handles the creation and management of desktop windows that display web content
using Qt's WebEngine (which is based on Chromium browser engine).

🎯 MAIN PURPOSES:
    1. Create desktop application windows
    2. Display web content (HTML/CSS/JavaScript) inside Qt widgets
    3. Enable communication between Python backend and JavaScript frontend
    4. Handle window management (minimize, maximize, close, etc.)
    5. Suppress browser deprecation warnings for clean console output

📚 KEY CONCEPTS FOR STUDENTS:
    - Qt: Cross-platform application framework (think of it as the "engine")
    - WebEngine: Embeds a web browser inside a desktop application
    - WebChannel: Allows Python and JavaScript to talk to each other
    - QApplication: The main application container (every Qt app needs one)

🔧 TECHNICAL STACK:
    - PySide6: Python bindings for Qt framework
    - QtWebEngine: Web browser component based on Chromium
    - WebChannel: Bidirectional communication bridge

Author: PyThra Framework Team
Last Modified: 2025
=============================================================================
"""

import os
import platform

# =============================================================================
# BROWSER ENGINE CONFIGURATION
# =============================================================================

# 🌐 CHROMIUM ENGINE SETUP
# These environment variables configure the underlying Chromium browser engine
# that powers Qt's WebEngine component. Think of this as "browser settings"
# that we set before the browser starts up.

# Set Chromium flags to suppress CSS deprecation warnings and console messages
# This is like passing command-line arguments to Chrome/Chromium when it starts
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-logging "                    # Turn off Chromium's internal logging
    "--silent "                            # Run in silent mode (less console noise)
    "--log-level=3 "                       # Only show critical errors (0=INFO, 3=FATAL)
    "--disable-web-security "              # Allow cross-origin requests (for local development)
    "--disable-features=VizDisplayCompositor " # Disable certain GPU features that can cause warnings
    "--suppress-message-center-popups "    # No popup notifications
    "--disable-dev-shm-usage"             # Prevents /dev/shm usage issues on some systems
)

# This is needed for some systems
if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
# windows equivalent will be
if platform.system() == "Windows":
    os.environ["QT_QPA_PLATFORM"] = "windows"
# mac equivalent will be
if platform.system() == "Darwin":
    os.environ["QT_QPA_PLATFORM"] = "cocoa"


# 📝 ALTERNATIVE CONFIGURATIONS (Currently commented out)
# These are other Chromium flags you might use for different purposes:
# - GPU acceleration control
# - Software rendering fallbacks
# - Sandbox security settings
# - OpenGL driver selection
# Uncomment and modify these if you encounter graphics or performance issues

# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
# os.environ["QT_QUICK_BACKEND"] = "software"         # Force software rendering
# os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"          # Completely disable GPU
# os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"      # Disable security sandbox
# os.environ["QT_OPENGL"] = "software"                # Use software OpenGL

# =============================================================================
# LIBRARY IMPORTS
# =============================================================================

# 📦 PySide6 (Qt for Python) - Main GUI Framework
# These imports give us the building blocks for creating desktop applications
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout    # Basic UI components
from PySide6.QtCore import Qt, QObject, Slot, QUrl, QSize, qInstallMessageHandler, QtMsgType, QTimer, QEvent, Signal  # Core functionality
from PySide6.QtWebEngineWidgets import QWebEngineView               # Web browser widget
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage # Browser configuration
from PySide6.QtWebChannel import QWebChannel                        # Python ↔ JavaScript communication
from PySide6.QtGui import QShortcut, QKeySequence, QGuiApplication  # Keyboard shortcuts and UI helpers
from PySide6.QtCore import (
    Qt, QObject, Slot, QUrl, QSize, qInstallMessageHandler, 
    QtMsgType, QTimer, QEvent, Signal, QStandardPaths
)

# 🐍 Standard Python Libraries
import sys                                      # System-specific parameters and functions
import re                                       # Regular expressions for pattern matching
import io                                       # Input/Output operations
from contextlib import redirect_stdout, redirect_stderr  # Context managers for stream redirection

import threading


from .window_manager import SystemSleepManager 

# =============================================================================
# PYTHRA FRAMEWORK IMPORTS
# =============================================================================

# 🎯 Import PyThra's Event System
# These classes define the data structures for touch and gesture events
# that get passed between the JavaScript frontend and Python backend
try:
    from ..events import TapDetails, PanUpdateDetails
    from ..debug_utils import debug_print
except Exception:
    class TapDetails:
        pass
    class PanUpdateDetails:
        def __init__(dx, dy):
            self.dx = dx
            self.dy = dy

    def debug_print(*args, **kwargs):
        """
        Print debug output only if debug mode is enabled.
        
        This function behaves exactly like the built-in print() function,
        but only prints if debug mode is enabled via set_debug(True).
        
        Args:
            *args: Positional arguments to print (same as print())
            **kwargs: Keyword arguments (same as print())
        
        Example:
            debug_print("Value of x:", x)
            debug_print("List:", items, sep=", ")
        """
        print(*args, **kwargs)

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# =============================================================================
# CONSOLE OUTPUT FILTERING SYSTEM
# =============================================================================

# 📝 PROBLEM: Web browsers (including Qt's WebEngine) often output deprecation warnings
# and other messages that clutter the console. This affects user experience.

# 🛡️ SOLUTION: Create a custom output stream wrapper that intercepts all console
# output and filters out unwanted messages before they reach the terminal.

class FilteredOutput:
    """
    🎯 PURPOSE: A "smart filter" for console output that suppresses unwanted messages
    
    📚 HOW IT WORKS:
        1. Wraps around the normal output streams (stdout/stderr)
        2. Intercepts every message before it gets #printed
        3. Checks if the message contains unwanted keywords
        4. Either suppresses the message or lets it through
    
    🎮 ANALOGY: Like a spam filter for your email, but for console messages
    
    🔧 TECHNICAL DETAILS:
        - Implements the same interface as sys.stdout/sys.stderr
        - Uses duck typing to replace the original streams seamlessly
        - Preserves all original functionality while adding filtering
    """
    
    def __init__(self, original_stream):
        """
        Initialize the filter with the original output stream to wrap.
        
        Args:
            original_stream: The original sys.stdout or sys.stderr object
        """
        self.original_stream = original_stream
        
    def write(self, message):
        """
        📝 The main filtering logic - decides whether to show or hide a message.
        
        This method gets called every time something tries to #print to the console.
        We check the message content and either suppress it or pass it through.
        
        Args:
            message (str): The text that something is trying to #print
        """
        # 🔍 Check if the message contains any unwanted keywords
        # We convert to lowercase to catch variations in capitalization
        unwanted_keywords = [
            'inset-area',                    # CSS deprecation warnings
            'position-area',                 # CSS deprecation warnings  
            'has been deprecated',           # General deprecation messages
            'autofill.enable failed',       # Browser autofill errors
            'autofill.setaddresses failed',  # Browser autofill errors
            'setLifecycleState:',
            'DevTools open',
            'failed to transition from Active to Discarded state:'
        ]
        
        # If the message contains any unwanted keywords, suppress it
        if any(keyword in message.lower() for keyword in unwanted_keywords):
            return  # 🚫 SUPPRESS: Don't #print this message
        
        # ✅ ALLOW: Message is clean, pass it to the original stream
        self.original_stream.write(message)
    
    def flush(self):
        """
        Force any buffered output to be written immediately.
        This is required for proper stream compatibility.
        """
        self.original_stream.flush()
    
    def __getattr__(self, name):
        """
        🧿 Magic method that forwards any other method calls to the original stream.
        
        This ensures our FilteredOutput behaves exactly like the original stream
        for any methods we haven't explicitly overridden.
        
        Args:
            name (str): The name of the attribute/method being accessed
            
        Returns:
            The corresponding attribute/method from the original stream
        """
        return getattr(self.original_stream, name)

# =============================================================================
# QT MESSAGE FILTERING SYSTEM
# =============================================================================

def custom_message_handler(msg_type, context, message):
    """
    🎯 PURPOSE: Custom Qt message handler to filter system-level messages
    
    📚 BACKGROUND: Qt (the GUI framework) has its own internal logging system
    that can output various types of messages (debug, warnings, errors, etc.).
    By default, these messages go directly to the console.
    
    🔧 HOW IT WORKS:
        1. Qt calls this function whenever it wants to log a message
        2. We examine the message content and type
        3. We either suppress the message or let it through with formatting
        4. This works at a lower level than the stdout/stderr filtering
    
    🎮 ANALOGY: Like having a security guard at the Qt framework level
    who decides which messages are allowed to reach the console
    
    Args:
        msg_type (QtMsgType): The type of message (Debug, Warning, Critical, Fatal)
        context (QMessageLogContext): Information about where the message came from
        message (str): The actual message text
    """
    # 🔍 Check if this message contains unwanted content
    # This catches Qt-level messages that might not go through stdout/stderr
    unwanted_keywords = [
        'inset-area',                    # CSS deprecation warnings
        'position-area',                 # CSS deprecation warnings
        'has been deprecated',           # General deprecation messages
        'autofill.enable failed',       # Browser autofill errors
        'autofill.setaddresses failed',  # Browser autofill errors
        'setLifecycleState:',
        'DevTools open',
        'failed to transition from Active to Discarded state:'
    ]
    
    if any(keyword in message.lower() for keyword in unwanted_keywords):
        return  # 🚫 SUPPRESS: Don't #print this Qt message
    
    # ✅ ALLOW: Format and display the message based on its severity level
    if msg_type == QtMsgType.QtDebugMsg:
        debug_print(f"🐛 Debug: {message}")        # Debug info (usually for developers)
    elif msg_type == QtMsgType.QtWarningMsg:
        debug_print(f"⚠️  Warning: {message}")       # Warning messages
    elif msg_type == QtMsgType.QtCriticalMsg:
        debug_print(f"🔴 Critical: {message}")     # Critical errors
    elif msg_type == QtMsgType.QtFatalMsg:
        debug_print(f"☠️  Fatal: {message}")         # Fatal errors (app will likely crash)

# =============================================================================
# APPLICATION INITIALIZATION AND FILTERING SETUP
# =============================================================================

# 🚀 CREATE THE MAIN APPLICATION INSTANCE
# QApplication is the heart of any Qt application - it manages the event loop,
# system resources, and provides the foundation for all GUI operations
app = QApplication(sys.argv)  # sys.argv allows the app to process command-line arguments
if app is None:
    # 🛡️ Fallback: Create a new application if one doesn't exist
    # This shouldn't normally happen, but it's good defensive programming
    app = QApplication(sys.argv)

# =============================================================================
# INSTALL THE MULTI-LAYER FILTERING SYSTEM
# =============================================================================

# 🎯 LAYER 1: Qt Framework Level Filtering
# Install our custom message handler to intercept Qt's internal logging system
# This catches messages at the framework level before they reach any output streams
qInstallMessageHandler(custom_message_handler)

# 🎯 LAYER 2: Python Output Stream Filtering
# Replace the standard output streams with our filtered versions
# This catches any messages that bypass Qt's logging system

# 📝 WHY WE NEED BOTH LAYERS:
# - Qt messages might use Qt's logging system OR Python's #print/stdout
# - JavaScript console messages from WebEngine go through different channels
# - By filtering both layers, we ensure comprehensive message suppression

# Install the output stream filters
sys.stdout = FilteredOutput(sys.stdout)  # Filter normal #print() statements
sys.stderr = FilteredOutput(sys.stderr)  # Filter error messages and warnings


# =============================================================================
# CROSS-PLATFORM APPLICATION ICON SETUP
# =============================================================================
# This section configures the application icon for each platform.
# It runs once at module load time, right after the QApplication is created.
#
# 🪟 Windows: Sets AppUserModelID so the taskbar groups our app icon properly
#             (otherwise it shows the generic Python icon)
# 🍎 macOS:   Sets the window icon which updates the Dock icon at runtime
# 🐧 Linux:   Sets the window icon AND links to the .desktop file for Wayland
# =============================================================================

from PySide6.QtGui import QIcon

def _setup_platform_icon():
    """
    Configure the application icon once for the current platform.
    
    Icon search priority:
    1. Platform-specific directory (windows/, macos/, linux/)
    2. assets/icons/icon.ico or assets/appIcon.png (legacy fallback)
    
    On Linux (Wayland): Automatically installs .desktop file and hicolor
    icons to ~/.local/share/ so the taskbar shows the app's icon instead
    of the generic gear icon. Wayland ignores setWindowIcon() entirely.
    
    This is a best-effort operation — it silently does nothing if called
    outside a GUI context (e.g. from a CLI command like `pythra upgrade`).
    """
    try:
        from pathlib import Path
        import shutil as _shutil

        # Guard: only run if a QApplication exists (skip for CLI tools)
        if app is None:
            return

        # --- Resolve the project root ---
        main_script = os.path.abspath(sys.argv[0])
        if 'lib' in os.path.normpath(main_script).split(os.sep):
            project_root = str(Path(main_script).parent.parent)
        else:
            project_root = str(Path(main_script).parent)

        # --- Read app_id and app_name from config if available ---
        app_id = 'com.pythra.app'
        app_name = 'PyThra App'
        debug_mode = True
        try:
            import yaml
            config_path = os.path.join(project_root, 'config.yaml')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f)
                if isinstance(cfg, dict):
                    app_id = cfg.get('app_id', app_id)
                    app_name = cfg.get('app_name', app_name)
                    debug_mode = cfg.get("Debug", True)
        except Exception:
            pass

        # --- 1. WINDOWS: Set AppUserModelID for correct taskbar icon grouping ---
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            except Exception:
                pass

        # --- 2. Set the application-wide icon (all platforms) ---
        icon_search_paths = []
        resolved_icon = None

        if sys.platform == 'win32':
            icon_search_paths = [
                os.path.join(project_root, 'windows', 'appIcon.ico'),
                os.path.join(project_root, 'assets', 'icons', 'icon.ico'),
            ]
        elif sys.platform == 'darwin':
            icon_search_paths = [
                os.path.join(project_root, 'macos', 'appIcon.icns'),
            ]
        else:
            # Linux: prefer largest hicolor PNG
            icon_search_paths = [
                os.path.join(project_root, 'linux', 'hicolor', '512x512', 'apps', 'appIcon.png'),
                os.path.join(project_root, 'linux', 'hicolor', '256x256', 'apps', 'appIcon.png'),
                os.path.join(project_root, 'linux', 'hicolor', '128x128', 'apps', 'appIcon.png'),
            ]

        # Universal fallback: PNG in assets
        icon_search_paths.append(os.path.join(project_root, 'assets', 'appIcon.png'))

        for icon_path in icon_search_paths:
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
                resolved_icon = icon_path
                break

        # --- 3. LINUX: Auto-install .desktop + hicolor icons for Wayland taskbar ---
        # Wayland completely ignores setWindowIcon() for the taskbar.
        # It relies 100% on setDesktopFileName() matching a real .desktop file
        # installed in ~/.local/share/applications/ with matching hicolor icons.
        if sys.platform.startswith('linux'):
            try:
                # Only automatically create/install .desktop and hicolor icons in debug mode
                if debug_mode and not getattr(sys, "frozen", False):
                    home = Path.home()
                    apps_dir = home / ".local" / "share" / "applications"
                    icons_base = home / ".local" / "share" / "icons" / "hicolor"

                    apps_dir.mkdir(parents=True, exist_ok=True)

                    # Determine executable — if running from a compiled binary,
                    # use the binary itself; otherwise use python3 + script
                    if getattr(sys, "frozen", False):
                        # Running as compiled binary (Nuitka/PyInstaller)
                        exec_line = f"Exec={sys.executable}"
                    else:
                        exec_line = f"Exec=python3 {os.path.abspath(main_script)}"

                    # Find the best icon to reference (absolute path for dev .desktop)
                    icon_line = f"Icon={app_id}"  # Default: FreeDesktop theme lookup
                    if resolved_icon:
                        icon_line = f"Icon={os.path.abspath(resolved_icon)}"

                    # Write the .desktop file
                    desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment=A PyThra desktop application
{exec_line}
{icon_line}
Terminal=false
Categories=Utility;
StartupWMClass={app_id}
"""
                    desktop_path = apps_dir / f"{app_id}.desktop"
                    desktop_path.write_text(desktop_content)

                    # Install hicolor icons to system dir
                    linux_hicolor = os.path.join(project_root, "linux", "hicolor")
                    if os.path.isdir(linux_hicolor):
                        for size_dir in Path(linux_hicolor).iterdir():
                            if not size_dir.is_dir():
                                continue
                            for apps_subdir in size_dir.iterdir():
                                if not apps_subdir.is_dir():
                                    continue
                                for icon_file in apps_subdir.iterdir():
                                    if icon_file.is_file():
                                        dest_dir = (
                                            icons_base
                                            / size_dir.name
                                            / apps_subdir.name
                                        )
                                        dest_dir.mkdir(parents=True, exist_ok=True)
                                        dest_file = dest_dir / f"{app_id}.png"
                                        _shutil.copy2(str(icon_file), str(dest_file))

                    # Silently update icon cache
                    try:
                        import subprocess as _sp

                        _sp.run(
                            ["gtk-update-icon-cache", str(icons_base)],
                            capture_output=True,
                            timeout=5,
                        )
                    except Exception:
                        pass

            except Exception:
                pass  # Icon install is best-effort

            # Tell Wayland which .desktop file to use
            app.setDesktopFileName(app_id)

    except Exception:
        # Icon setup is best-effort — never block app startup
        pass


# Run the platform icon setup
_setup_platform_icon()


def watch_for_power_events(sleep_manager, on_resume_callback):
    """
    Run in background thread, call sleep_manager methods on sleep/resume,
    and call the original on_resume_callback for repaint logic.
    """
    import wmi
    c = wmi.WMI()
    watcher = c.watch_for(
        notification_type="Creation",
        wmi_class="Win32_PowerManagementEvent"
    )
    print("Watching for Windows power management events (sleep/resume)...")
    while True:
        event = watcher()
        # EventType 4 corresponds to the system entering a suspended state (sleep).
        if event.EventType == 4:
            print("System is entering sleep state.")
            # =============================================================================
            # FIXED: Instead of callLater, call the trigger method which emits a signal.
            # This is thread-safe.
            # =============================================================================
            sleep_manager.trigger_sleep_event()

        # EventType 7 corresponds to the system resuming from a suspended state.
        elif event.EventType == 7:
            print("System has resumed from sleep.")
            # =============================================================================
            # FIXED: Use the trigger method here as well.
            # =============================================================================
            sleep_manager.trigger_resume_event()
            
            # The original on_resume_callback for repainting is still needed.
            on_resume_callback()


def setup_platform_watchers(window, sleep_manager):
    """
    Starts the appropriate sleep/resume watchers for the current OS.
    """
    if platform.system() == "Windows":
        def on_resume():
            try:
                print("watcher: emitting resume_signal for repaint.")
                window.resume_signal.emit()
            except Exception as e:
                print("watcher: failed to emit resume_signal:", e)

        # Run watcher in background thread, passing it the sleep manager
        thread = threading.Thread(
            target=watch_for_power_events,
            args=(sleep_manager, on_resume),
            daemon=True
        )
        thread.start()
    
    elif platform.system() == "Linux":
        # On Linux, the manager handles its own listener
        sleep_manager.setup_event_listener()


class WindowManager:
    def __init__(self):
        self.windows = {}

    def register_window(self, window_id, window):
        self.windows[window_id] = window

    def set_window_state(self, window_id, state):
        if window_id in self.windows:
            window = self.windows[window_id]
            if state == "minimized":
                window.setWindowState(Qt.WindowMinimized)
            elif state == "maximized":
                window.setWindowState(Qt.WindowMaximized)
            elif state == "normal":
                window.setWindowState(Qt.WindowNoState)
            else:
                print(f"Invalid state: {state}")
        else:
            print(f"Window ID {window_id} not found.")


class Api(QObject):
    def __init__(self):
        super().__init__()
        self.callbacks = {}

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Api, cls).__new__(cls)
        return cls._instance

    def register_callback(self, name, callback):
        self.callbacks[name] = callback
        # print("Callbacks: ", self.callbacks)

    def clear_callbacks(self):
        """Removes all registered callbacks."""
        # print("API: Clearing all callbacks.")
        debug_print("API: Clearing all callbacks.")
        self.callbacks.clear()

    def _execute_callback(self, cb, *args):
        import inspect
        if inspect.iscoroutinefunction(cb):
            import asyncio
            try:
                asyncio.create_task(cb(*args))
            except RuntimeError as e:
                from ..debug_utils import debug_print
                debug_print(f"Cannot run async callback - no running event loop (did you install qasync?): {e}")
        else:
            cb(*args)

    @Slot(str, int, result=str)
    @Slot(str, str, result=str)
    @Slot(str, list, result=str)
    def on_pressed(self, callback_name, *args):
        if callback_name in self.callbacks:
            self._execute_callback(self.callbacks[callback_name], *args)
            return f"Callback '{callback_name}' executed successfully."
        else:
            return f"Callback '{callback_name}' not found."

    @Slot(str, result=str)
    def on_pressed_str(self, callback_name):
        if callback_name in self.callbacks:
            self._execute_callback(self.callbacks[callback_name])
            return f"Callback '{callback_name}' executed successfully."
        else:
            return f"Callback '{callback_name}' not found."

    @Slot(str, str, result=None)
    def on_input_changed(self, callback_name, value):
        """
        Slot to handle 'oninput' events from text fields.
        Finds the registered callback by its name and executes it with the new value.
        """
        callback = self.callbacks.get(callback_name)
        # print("callback: ", callback)
        debug_print("callback: ", callback)
        if callback:
            try:
                # The callback will be the state method (e.g., self.on_username_changed)
                self._execute_callback(callback, value)
            except Exception as e:
                print(f"Error executing input callback '{callback_name}': {e}")
                debug_print(f"Error executing input callback '{callback_name}': {e}")
        else:
            print(f"Warning: Input callback '{callback_name}' not found.")
            debug_print(f"Warning: Input callback '{callback_name}' not found.")

    # --- ADD THIS NEW SLOT FOR THE SLIDER ---
    @Slot(str, float, bool, result=None)
    def on_drag_update(self, callback_name, value, drag_ended):
        """
        Slot to handle 'oninput' events from range sliders.
        Executes the registered callback with the new float value.
        """
        callback = self.callbacks.get(callback_name)
        # print("callback drag_ended: ", drag_ended)
        debug_print("callback drag_ended: ", drag_ended)
        if callback:
            try:
                self._execute_callback(callback, value, drag_ended)
            except Exception as e:
                # print(f"Error executing slider callback '{callback_name}': {e}")
                debug_print(f"Error executing slider callback '{callback_name}': {e}")
        else:
            # print(f"Warning: Slider callback '{callback_name}' not found.")
            debug_print(f"Warning: Slider callback '{callback_name}' not found.")
    # --- END OF NEW SLOT ---

    @Slot(str, int)
    def send_message(self, message, *args):
        # print(f"Frontend message: {message}, ", *args)
        print(f"Frontend message: {message}, ", *args)
        return "Message received!"

    @Slot(str)
    def on_button_clicked(self, message):
        # print(f"Message from JavaScript: {message}")
        debug_print(f"Message from JavaScript: {message}")

    # --- THIS IS THE NEW SLOT ---
    # It's specifically for building virtual list items.
    # It returns a QVariantMap, which maps to a JavaScript object.
    @Slot(str, int, result='QVariantMap')
    def build_list_item(self, builder_name, index):
        """
        Called by the virtual list JS engine to build the HTML and CSS
        for a single item.
        """
        callback = self.callbacks.get(builder_name)
        if callback and callable(callback):
            try:
                # This call now returns a dict: {"html": "...", "css": "..."}
                return callback(index)
            except Exception as e:
                # print(f"Error executing item builder '{builder_name}' for index {index}: {e}")
                debug_print(f"Error executing item builder '{builder_name}' for index {index}: {e}")
                return {"html": "<div>Error</div>", "css": ""}
        else:
            # print(f"Warning: Item builder '{builder_name}' not found.")
            debug_print(f"Warning: Item builder '{builder_name}' not found.")
            return {"html": "<div>Builder not found</div>", "css": ""}

    # --- ADD THIS NEW GENERIC SLOT ---
    @Slot(str, 'QVariantMap', result=None)
    def on_gesture_event(self, callback_name, details):
        """
        Generic slot to handle all events from the GestureDetector JS engine.
        """
        callback = self.callbacks.get(callback_name)
        # print("Callback tap debug info: ",callback, " " ,details)
        # print("Callback tap debug info: ",callback, " " ,details)
        if callback:
            try:
                # Based on the callback name, we can construct the correct data class.
                if "pupdate" in callback_name:
                    # For PanUpdate, details is a dict {'dx': float, 'dy': float}
                    self._execute_callback(callback, PanUpdateDetails(dx=details.get('dx', 0), dy=details.get('dy', 0)))
                elif "tap" in callback_name and "dbtap" not in callback_name:
                    self._execute_callback(callback, TapDetails())
                else:
                    # For DoubleTap, LongPress, PanStart, PanEnd, no details are needed.
                    self._execute_callback(callback)
            except Exception as e:
                # print(f"Error executing gesture callback '{callback_name}': {e}")
                debug_print(f"Error executing gesture callback '{callback_name}': {e}")
        else:
            # print(f"Warning: Gesture callback '{callback_name}' not found.")
            debug_print(f"Warning: Gesture callback '{callback_name}' not found.")

    # --- Video Player rect update Slot ---
    @Slot(str, str, result=None)
    def on_video_rect(self, callback_name, rect_data):
        """
        Slot to receive vid-box bounding rect updates from the
        PythraVideoPlayer JS engine via QWebChannel.
        """
        callback = self.callbacks.get(callback_name)
        if callback:
            try:
                self._execute_callback(callback, rect_data)
            except Exception as e:
                debug_print(f"Error executing video rect callback '{callback_name}': {e}")
        else:
            debug_print(f"Warning: Video rect callback '{callback_name}' not found.")

    # --- Video Player command Slot ---
    @Slot(str, str, str, result=None)
    def on_video_command(self, callback_name, cmd_type, value):
        """
        Slot to receive video commands (volume, seek) from the JS engine.
        """
        debug_print(f"DEBUG: on_video_command received: cb={callback_name}, type={cmd_type}, val={value}")
        callback = self.callbacks.get(callback_name)
        if callback:
            try:
                self._execute_callback(callback, cmd_type, value)
            except Exception as e:
                debug_print(f"Error executing video command callback '{callback_name}': {e}")
        else:
            debug_print(f"Warning: Video command callback '{callback_name}' not found.")

    # --- Viewport Resize Slot (called from browser ResizeObserver) ---
    @Slot(int, int, result=None)
    def on_viewport_resize(self, width, height):
        """Slot called from JS ResizeObserver when the browser viewport resizes."""
        try:
            from ..core import Framework
            framework = Framework.instance()
            if framework:
                framework.handle_resize(width, height)
        except Exception as e:
            debug_print("Failed to handle viewport resize:", e)

    # --- Frameless Window Drag & Resize Slots ---
    @Slot()
    def startWindowDrag(self):
        window = window_manager.windows.get("main_window_id")
        if window and window.windowHandle():
            window.windowHandle().startSystemMove()

    @Slot(int)
    def startWindowResize(self, edge):
        window = window_manager.windows.get("main_window_id")
        if window and window.windowHandle():
            window.windowHandle().startSystemResize(Qt.Edge(edge))

    @Slot(result=None)
    def hot_restart(self):
        """Triggers framework-level hot restart by exiting with code 3 (which pythra run catches to restart)."""
        try:
            print("🔄 Hot Restart triggered from UI...")
            # Shut down asset server and close window gracefully first
            try:
                from ..core import Framework

                framework = Framework.instance()
                if framework:
                    framework.close()
            except Exception:
                pass

            # Exit with our special exit code 3
            import sys

            sys.exit(3)
        except Exception as e:
            print(f"Error during hot restart: {e}")

    @Slot(result=None)
    def hot_reload_from_ui(self):
        """Triggers framework-level hot reload from the UI debug banner."""
        try:
            from ..core import Framework
            framework = Framework.instance()
            if framework:
                framework.hot_reload()
        except Exception as e:
            print(f"Error during hot reload from UI: {e}")

    @Slot(result=None)
    def close_app(self):
        """Closes the application."""
        try:
            from ..core import Framework

            framework = Framework.instance()
            if framework:
                print("❌ Close App triggered from UI...")
                framework.close()
        except Exception as e:
            print(f"Error closing app: {e}")


# Create a global instance of the WindowManager
window_manager = WindowManager()


class DebugWindow(QWebEngineView):
    """A separate window for inspecting HTML elements."""

    def __init__(self, overlay: bool = None):
        super().__init__()
        self.setWindowTitle("Debug Window")
        if overlay: 
            print(f"overlay is: {True}") 
            # Ensure the debug window stays at the bottom of the application for visibility
            # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnBottomHint)
        else: print(f"overlay is: {False}")
        
        self.resize(800, 600)



# ── Custom WebEngine Page ─────────────────────────────────────────────
class PythraWebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage subclass to capture and route browser console.log/error messages to python output."""
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        level_str = "INFO"
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel:
            level_str = "WARNING"
        elif level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            level_str = "ERROR"
        print(f"[JS {level_str}] ({sourceID}:{lineNumber}): {message}")


class WebWindow(QWidget):
    resume_signal = Signal()   # queued, thread-safe
    document_ready = Signal(bool)  # emitted when webview finishes loading
    def __init__(
        self,
        title,
        window_id="main_window",
        html_file=None,
        js_api=None,
        width=800,
        height=600,
        min_width=400,
        min_height=300,
        window_state="normal",
        frameless=False,
        on_top=False,
        maximized=False,
        fixed_size=False,
        video_overlay=False,
        debug=False,
    ):
        self.video_overlay = video_overlay
        self.debug = debug
        super().__init__()
        self.setWindowTitle(title)
        self.fixed_size = fixed_size
        if not maximized and not fixed_size:
            self.setGeometry(100, 100, width, height)
            self.setMinimumSize(QSize(min_width, min_height))

        if fixed_size and not maximized:
            self.setFixedSize(QSize(width, height))
            self.setMinimumSize(QSize(min_width, min_height))

        if on_top:
            # Make the window stay on top
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        if frameless:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
            self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout(self)

        # Register the window with the WindowManager
        window_manager.register_window(window_id, self)

        # --- CONFIGURE CACHING ---
        # Set up a persistent profile for caching (including fonts)
        profile = QWebEngineProfile.defaultProfile()
        cache_path = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.CacheLocation),
            "pythra",
            "webcache"
        )
        profile.setCachePath(cache_path)
        profile.setPersistentStoragePath(cache_path)
        # Enable disk cache
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setSpellCheckEnabled(True)
        try:
            profile.setSpellCheckLanguages(["en-US"])
        except Exception as e:
            debug_print(f"⚠️ Failed to set spellcheck languages: {e}")

        # print("📁 Setup WebEngine Config: ", cache_path)
        debug_print("📁 Setup WebEngine Config: ", cache_path)

        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- VIDEO OVERLAY MODE (mirrors VLCPlayer stacking from vid.py) ---
        # When enabled, a native video_frame widget sits underneath the
        # webview which is created as a floating transparent Tool window.
        # CRITICAL: The Tool flags MUST be set immediately at creation time
        # (before layout/HTML), matching vid.py's order. Setting flags after
        # the widget has been laid out causes Qt to destroy and recreate the
        # native window, breaking the parent-child association.
        if self.video_overlay:
            # Match vid.py's transparency for overlay stacking
            # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

            # 1. Create a native video_frame child (VLC attaches to its winId)
            self.video_frame = QWidget(self)
            self.video_frame.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
            self.video_frame.setAttribute(
                Qt.WidgetAttribute.WA_DontCreateNativeAncestors, True
            )

            # 2. Create webview as child of self (same as vid.py)
            self.webview = QWebEngineView(self)
            self.webview.setPage(PythraWebEnginePage(self.webview))

            # 3. Set Tool flags IMMEDIATELY — before any layout or HTML load
            self.webview.setWindowFlags(
                Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
            )
            self.webview.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.webview.page().setBackgroundColor(Qt.GlobalColor.transparent)

            # Do NOT add webview to layout — it floats as a Tool window
        else:
            # --- DEFAULT MODE (webview inside layout) ---
            self.webview = QWebEngineView(self)
            self.webview.setPage(PythraWebEnginePage(self.webview))

            # Enable transparency for frameless windows
            if frameless:
                self.webview.setAttribute(Qt.WA_TranslucentBackground, True)
                self.webview.setStyleSheet("background: transparent;")
                self.webview.page().setBackgroundColor(Qt.transparent)

            self.layout.addWidget(self.webview)

        # --- Common webview settings (both modes) ---
        self.webview.settings().setAttribute(
            QWebEngineSettings.LocalContentCanAccessRemoteUrls, True
        )
        self.webview.settings().setAttribute(
            QWebEngineSettings.LocalContentCanAccessFileUrls, True
        )
        self.webview.settings().setAttribute(
            QWebEngineSettings.AllowRunningInsecureContent, True
        )
        self.webview.settings().setAttribute(
            QWebEngineSettings.JavascriptCanOpenWindows, True
        )
        self.webview.settings().setAttribute(
            QWebEngineSettings.ShowScrollBars, False
        )

        if html_file:
            self.webview.setUrl(QUrl.fromLocalFile(html_file))
            debug_print("⚡ HTML loaded:")
        else:
            debug_print("HTML not loaded: ", html_file)
        debug_print("⚡ WEBVIEW loaded:")

        # Setup QWebChannel
        self.channel = QWebChannel()
        if js_api:
            self.channel.registerObject("pywebview", js_api)
        self.webview.page().setWebChannel(self.channel)

        # Change window state
        window_manager.set_window_state(window_id, window_state)

        # Developer Tools (only when debug=True)
        if self.debug:
            self.debug_window = DebugWindow(self.video_overlay)
            self.webview.page().setDevToolsPage(self.debug_window.page())
            self.debug_window.hide()
            # F12 shortcut to toggle DevTools
            self.shortcut = QShortcut(QKeySequence("F12"), self)
            self.shortcut.activated.connect(self.toggle_debug_window)
        else:
            self.debug_window = None
        # Connect to app state changes so we can detect resume/activate
        app.applicationStateChanged.connect(self._on_application_state_changed)
        # Connect resume signal to slot that runs in the GUI thread
        self.resume_signal.connect(self._on_system_resume_slot)

        # Track whether the underlying document has finished loading
        self._document_ready = False
        # Emit `document_ready` when webview load finishes
        try:
            self.webview.loadFinished.connect(self._on_load_finished)
        except Exception:
            pass

        self._base_dpi = None
        self._base_device_pixel_ratio = None
        self._zoom_override_enabled = True  # toggle if you prefer recreate-only behavior
        self._dpi_probe_timeout_ms = 5000  # max time to try to probe DPR on startup

        QTimer.singleShot(0, self._ensure_initial_dpi)

    def toggle_debug_window(self):
        minimized = False
        if not self.debug_window:
            return
        if self.debug_window.isVisible():
            self.debug_window.hide()
        else:
            # if not minimized:
            #     self.debug_window.showMinimized()
            #     minimized = True
            # else:
            #     print(minimized)
            self.debug_window.show()

    def show_window(self):
        self.show()

    def show_max_window(self):
        self.showMaximized()
        size = self.size()
        screen = QApplication.primaryScreen()
        size = screen.availableGeometry().size()
        max_size = screen.availableGeometry().size()
        # self.setFixedSize(max_size)

        if self.fixed_size:
            self.setFixedSize(max_size)

    def minimize(self):
        self.showMinimized()

    def restore_normal(self):
        self.showNormal()

    def close_window(self):
        self.close()
        if self.video_overlay and hasattr(self, "webview"):
            self.webview.close()
        if self.debug_window:
            self.debug_window.close()

    def reload(self):
        """Reloads the webview content."""
        if hasattr(self, "webview") and self.webview:
            self.webview.reload()

    def evaluate_js(self, window_id, *scripts):
        # Define a dummy callback function to make the call non-blocking.
        def dummy_callback(result):
            # We can log the result here for debugging if needed.
            # #print(f"JS execution finished with result: {result}")
            pass
        if window_id in window_manager.windows:
            window = window_manager.windows[window_id]
            if hasattr(window, "webview") and window.webview:
                # Batch all script fragments into a single script to reduce
                # overhead from multiple runJavaScript calls.
                try:
                    combined = "\n".join(s for s in scripts if s)
                    if combined:
                        window.webview.page().runJavaScript(combined, dummy_callback)
                except Exception as e:
                    debug_print("evaluate_js: failed to run combined script:", e)
            else:
                # print(f"Window {window_id} does not have a webview.")
                debug_print(f"Window {window_id} does not have a webview.")
        else:
            # print(f"Window ID {window_id} not found.")
            debug_print(f"Window ID {window_id} not found.")

    def toggle_overlay(self):
        self.overlay_box.setVisible(not self.overlay_box.isVisible())

    @Slot()
    def _on_system_resume_slot(self):
        """Runs on the GUI thread when system resumes."""
        try:
            # print("GUI: handling system resume — syncing webview viewport now.")
            debug_print("GUI: handling system resume — syncing webview viewport now.")
            # call the sync helper which sets viewport and fires JS resize
            self._sync_webview_viewport()
            # AFTER a small delay probe DPR and apply zoom if needed.
            # This handles cases where QScreen reports 96 but page DPR changed.
            QTimer.singleShot(100, self._on_dpi_changed)
            # optional: force a small delayed re-sync in case DPI changes arrive slightly later
            QTimer.singleShot(200, self._sync_webview_viewport)
        except Exception as e:
            # print("Error in _on_system_resume_slot:", e)
            debug_print("Error in _on_system_resume_slot:", e)

    def resizeEvent(self, event):
        # Ensure Qt does the normal handling
        super().resizeEvent(event)

        # NOTE: Viewport resize is now handled by the browser-side ResizeObserver
        # which calls Api.on_viewport_resize via QWebChannel. This avoids
        # premature resize events during window creation/show that would
        # trigger setState before the DOM is loaded.

        # Defer the sync very slightly so all layout updates have happened
        QTimer.singleShot(0, self._sync_webview_viewport)
        # Keep floating overlay in sync when in video_overlay mode
        if self.video_overlay:
            self._update_overlay_pos()

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.video_overlay:
            self._update_overlay_pos()

    def showEvent(self, event):
        super().showEvent(event)
        # Sync on show as well
        QTimer.singleShot(0, self._sync_webview_viewport)
        # Show the floating overlay when in video_overlay mode
        if self.video_overlay and hasattr(self, "webview"):
            self._update_overlay_pos()
            self.webview.show()

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.video_overlay and hasattr(self, "webview"):
            self.webview.close()
        if self.debug_window:
            self.debug_window.close()

    def changeEvent(self, event):
        super().changeEvent(event)
        # Handle minimize/restore for floating overlay windows (video_overlay mode)
        if self.video_overlay and event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                # Disconnect DevTools to prevent lifecycle crash
                if self.debug_window:
                    try:
                        self.webview.page().setDevToolsPage(None)
                    except Exception:
                        pass
                if hasattr(self, "webview"):
                    self.webview.hide()
                if self.debug_window and self.debug_window.isVisible():
                    self.debug_window.hide()
                    self._dev_tools_was_visible = True
            else:
                if hasattr(self, "webview"):
                    self.webview.show()
                if getattr(self, "_dev_tools_was_visible", False):
                    # Reconnect DevTools on restore
                    if self.debug_window and hasattr(self, "webview"):
                        self.webview.page().setDevToolsPage(self.debug_window.page())
                        self.debug_window.show()
                    self._dev_tools_was_visible = False

    def _update_overlay_pos(self):
        """Sync floating webview overlay to match parent window geometry (video_overlay mode)."""
        if hasattr(self, "webview") and self.video_overlay:
            global_pos = self.mapToGlobal(self.rect().topLeft())
            self.webview.setGeometry(
                global_pos.x(), global_pos.y(), self.width(), self.height()
            )
            self.webview.page().runJavaScript(
                "if (typeof sendRect !== 'undefined') sendRect();"
            )

    def _on_application_state_changed(self, state):
        # Qt.ApplicationActive means app is now active (user returned / woke PC)
        if state == Qt.ApplicationActive:
            # Wait a little for the OS/Qt to finish restoring screens/DPI
            QTimer.singleShot(150, self._sync_webview_viewport)

    def _sync_webview_viewport(self):
        """
        Force web engine to match the widget size and dispatch a browser resize
        so web content reflows correctly after sleep/resize/DPI changes.
        """
        try:
            # In video_overlay mode, the webview is a floating Tool window —
            # delegate to _update_overlay_pos which handles global positioning.
            if self.video_overlay:
                self._update_overlay_pos()
                # Still dispatch a resize event so JS/CSS reflows
                self.webview.page().runJavaScript(
                    'window.dispatchEvent(new Event("resize"));'
                )
                self.webview.update()
                return

            # Make sure view has correct widget geometry
            w = self.webview.width()
            h = self.webview.height()

            # Resize the internal view (defensive — should be same)
            self.webview.resize(w, h)

            # Tell the QWebEnginePage about the new viewport size
            # This helps Chromium re-create the compositor/viewport properly.
            page = self.webview.page()
            if hasattr(page, "setViewportSize"):
                page.setViewportSize(self.webview.size())

            # Trigger a browser 'resize' event so any JS/CSS reflow happens
            page.runJavaScript('window.dispatchEvent(new Event("resize"));')

            # force repaint
            self.webview.update()
        except Exception as e:
            # print("Warning: failed to sync webview viewport:", e)
            debug_print("Warning: failed to sync webview viewport:", e)

    def _ensure_initial_dpi(self):
        """
        Attempt to determine a correct base DPI/DPR.
        Prefer the page's window.devicePixelRatio (most reliable for CSS scaling).
        Fall back to QScreen.logicalDotsPerInch if JS probe fails.
        """
        # default safe values
        fallback_dpi = 96.0
        fallback_dpr = 1.0

    @Slot(bool)
    def _on_load_finished(self, ok: bool):
        """Called when the QWebEngineView finishes loading its page.

        Emits `document_ready` and records readiness for external checks.
        """
        try:
            self._document_ready = bool(ok)
            debug_print(f"WebWindow: loadFinished -> {ok}")
            # emit signal (queued)
            self.document_ready.emit(bool(ok))
        except Exception as e:
            debug_print(f"Error in _on_load_finished: {e}")

    def is_document_ready(self) -> bool:
        """Return whether the webview has finished loading its initial document."""
        return getattr(self, "_document_ready", False)

        # helper to finalize baseline using either values we obtained
        def finalize(base_dpr, base_dpi=None):
            try:
                if base_dpr is None or base_dpr <= 0:
                    base_dpr = fallback_dpr
                if base_dpi is None:
                    base_dpi = fallback_dpi * base_dpr
                self._base_device_pixel_ratio = float(base_dpr)
                self._base_dpi = float(base_dpi)
                debug_print(f"Base DPI: {self._base_dpi}, base DPR: {self._base_device_pixel_ratio}")
            except Exception as e:
                debug_print("finalize base dpi failed:", e)
                self._base_device_pixel_ratio = fallback_dpr
                self._base_dpi = fallback_dpi

        # 1) Try to capture DPR from the page (preferred)
        def got_dpr(value):
            """
            Callback from runJavaScript. value is string from JS.
            If we get it, compute base_dpi = 96 * dpr.
            """
            try:
                if value is not None:
                    dpr = float(value)
                    if dpr > 0:
                        finalize(dpr, 96.0 * dpr)
                        return
            except Exception:
                pass

            # If JS failed, try screen DPI fallback
            try:
                screen = QGuiApplication.primaryScreen()
                if screen:
                    logical = screen.logicalDotsPerInch() or fallback_dpi
                    # some platforms return 96 as fallback even when scaled; attempt devicePixelRatio from screen
                    try:
                        scr_dpr = screen.devicePixelRatio() or 1.0
                    except Exception:
                        scr_dpr = 1.0
                    finalize(scr_dpr, logical)
                    return
            except Exception:
                pass

            # final fallback
            finalize(None, None)

        # run the JS probe (async). If no webview/page, fallback to screen immediately
        try:
            if hasattr(self, "webview") and self.webview and self.webview.page():
                # ask page for its devicePixelRatio; cast to string to avoid numeric conversions issues
                self.webview.page().runJavaScript("window.devicePixelRatio.toString();", got_dpr)
                # also set a timeout: if JS doesn't respond within timeout, use screen values
                QTimer.singleShot(self._dpi_probe_timeout_ms, lambda: (
                    finalize(self._base_device_pixel_ratio, self._base_dpi) if self._base_device_pixel_ratio is None else None
                ))
                return
        except Exception as e:
            debug_print("JS DPR probe failed to start:", e)

        # fallback immediate attempt using screen
        try:
            screen = QGuiApplication.primaryScreen()
            if screen:
                logical = screen.logicalDotsPerInch() or fallback_dpi
                try:
                    scr_dpr = screen.devicePixelRatio() or 1.0
                except Exception:
                    scr_dpr = 1.0
                finalize(scr_dpr, logical)
                return
        except Exception:
            pass

        # absolute fallback
        finalize(None, None)

    def _on_dpi_changed(self):
        """
        Called on screen DPI/geometry changes or system resume.
        Probes the page DPR and applies the correct zoom factor relative to baseline DPR.
        Falls back to QScreen.logicalDotsPerInch if JS probe fails.
        Also updates the debug window if it is visible.
        """
        try:
            if not hasattr(self, "webview") or not self.webview or not self.webview.page():
                QTimer.singleShot(0, self._sync_webview_viewport)
                return

            def apply_scale_from_dpr(js_value):
                try:
                    new_dpr = float(js_value) if js_value is not None else None
                except Exception:
                    new_dpr = None

                # compute scale
                scale = 1.0
                if new_dpr is not None:
                    base_dpr = float(self._base_device_pixel_ratio or 1.0)
                    if base_dpr <= 0:
                        base_dpr = 1.0
                    scale = new_dpr / base_dpr
                else:
                    try:
                        screen = QGuiApplication.primaryScreen()
                        if screen:
                            logical_dpi = screen.logicalDotsPerInch() or 96.0
                            base_dpi = float(self._base_dpi or 96.0)
                            scale = logical_dpi / base_dpi
                    except Exception:
                        scale = 1.0

                debug_print(f"Computed scale: {scale} (base_dpr={self._base_device_pixel_ratio})")

                try:
                    if self._zoom_override_enabled:
                        # Apply absolute baseline DPR as zoom factor
                        zoom_factor = float(self._base_device_pixel_ratio or 1.0)
                        self.webview.page().setZoomFactor(zoom_factor)
                        debug_print(f"Applied zoomFactor to main webview: {zoom_factor}")

                        # Resize viewport
                        QTimer.singleShot(50, self._sync_webview_viewport)

                        # Also apply to debug window if visible
                        if self.debug_window and self.debug_window.isVisible():
                            try:
                                self.debug_window.page().setZoomFactor(zoom_factor)
                                self.debug_window.update()
                                self.debug_window.page().runJavaScript('window.dispatchEvent(new Event("resize"));')
                                debug_print(f"Applied zoomFactor to debug window: {zoom_factor}")
                            except Exception as e:
                                debug_print("Failed to apply zoom to debug window:", e)

                        # Signal JS resize for main webview
                        try:
                            self.webview.page().runJavaScript('window.dispatchEvent(new Event("resize"));')
                        except Exception as e:
                            debug_print("Failed to dispatch resize JS after setZoomFactor:", e)
                        return

                    # For minor scale changes, just sync viewport
                    if abs(scale - 1.0) < 0.03:
                        QTimer.singleShot(0, self._sync_webview_viewport)
                        if self.debug_window and self.debug_window.isVisible():
                            QTimer.singleShot(0, lambda: self.debug_window.update())
                        return

                    # Fallback: sync viewport
                    QTimer.singleShot(0, self._sync_webview_viewport)
                    if self.debug_window and self.debug_window.isVisible():
                        QTimer.singleShot(0, lambda: self.debug_window.update())

                except Exception as e:
                    debug_print("Error applying scale:", e)
                    QTimer.singleShot(0, self._sync_webview_viewport)
                    if self.debug_window and self.debug_window.isVisible():
                        QTimer.singleShot(0, lambda: self.debug_window.update())

            # Probe page DPR asynchronously
            try:
                self.webview.page().runJavaScript("window.devicePixelRatio.toString();", apply_scale_from_dpr)
            except Exception as e:
                debug_print("JS DPR probe failed in _on_dpi_changed:", e)
                QTimer.singleShot(0, self._sync_webview_viewport)
                if self.debug_window and self.debug_window.isVisible():
                    QTimer.singleShot(0, lambda: self.debug_window.update())

        except Exception as e:
            debug_print("Error in _on_dpi_changed:", e)
            QTimer.singleShot(0, self._sync_webview_viewport)
            if self.debug_window and self.debug_window.isVisible():
                QTimer.singleShot(0, lambda: self.debug_window.update())

    def _apply_zoom_safely(self, target_zoom_candidate, desired_base_dpi, verify_timeout=250):
        """
        Try a candidate zoom factor first, then verify by probing window.devicePixelRatio.
        If verification fails, return False so caller can try an alternative strategy.
        """
        try:
            # guard values
            if target_zoom_candidate <= 0 or target_zoom_candidate > 10:
                debug_print("Refusing to apply out-of-range zoom:", target_zoom_candidate)
                return False

            debug_print(f"Attempting zoom candidate: {target_zoom_candidate}")
            try:
                self.webview.page().setZoomFactor(target_zoom_candidate)
            except Exception as e:
                debug_print("setZoomFactor call failed:", e)
                return False

            # short wait then probe DPR to verify
            verified = {"ok": False}

            def verify_cb(val):
                try:
                    if val is None:
                        verified["ok"] = False
                        return
                    new_dpr_after = float(val)
                    # Convert to DPI to compare with desired base DPI
                    new_dpi_after = new_dpr_after * 96.0
                    debug_print(f"Verification probe after zoom -> DPR: {new_dpr_after}, DPI: {new_dpi_after}")
                    # Accept if within ~3% of desired DPI
                    if abs(new_dpi_after - desired_base_dpi) / max(desired_base_dpi, 1.0) < 0.03:
                        verified["ok"] = True
                    else:
                        verified["ok"] = False
                except Exception as e:
                    debug_print("Error in verify_cb:", e)
                    verified["ok"] = False

            # schedule a small delayed probe
            QTimer.singleShot(verify_timeout, lambda: self.webview.page().runJavaScript("window.devicePixelRatio.toString();", verify_cb))
            # busy-wait-ish polling (non-blocking) — poll a few times until verify_timeout*2
            wait_attempts = 0
            max_attempts = 6
            poll_interval = max(50, verify_timeout // max_attempts)
            while wait_attempts < max_attempts:
                QTimer.singleShot(wait_attempts * poll_interval, lambda: None)
                # We can't block the event loop; instead we rely on the verify callback to flip 'verified'
                # So just sleep a small amount here to let the event loop run (very small)
                import time
                time.sleep(poll_interval / 1000.0)
                if verified["ok"]:
                    break
                wait_attempts += 1

            return bool(verified["ok"])
        except Exception as e:
            debug_print("Error in _apply_zoom_safely:", e)
            return False


# Create Window Function
def create_window(
    title: str,
    window_id: str,
    html_file: str = None,
    js_api: Api = None,
    width: int = 800,
    height: int = 600,
    min_width: int = 400,
    min_height: int = 300,
    window_state: str = "normal",
    frameless: bool = True,
    maximized: bool = False,
    fixed_size: bool = False,
    video_overlay: bool = False,
    debug: bool = False,
):
    window = WebWindow(
        title,
        window_id=window_id,
        html_file=html_file,
        js_api=js_api,
        width=width,
        height=height,
        window_state=window_state,
        frameless=frameless,
        maximized=maximized,
        fixed_size=fixed_size,
        min_width=min_width,
        min_height=min_height,
        video_overlay=video_overlay,
        debug=debug,
    )
    if maximized:
        window.show_max_window()
    else:
        window.show_window()

    return window


def change_color():
    window.run_js("main_window", "document.body.style.backgroundColor = 'lightblue';")


def start(window, debug):

    sleep_manager = SystemSleepManager(window_manager)

    # DevTools toggling is now handled inside WebWindow.__init__ via F12 shortcut
    # when debug=True — no need to auto-open it here.

    setup_platform_watchers(window, sleep_manager)

    try:
        import qasync
        import asyncio
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        debug_print("⚡ PyThra Framework | Started Native qasync Event Loop!")
        with loop:
            sys.exit(loop.run_forever())
    except ImportError:
        debug_print("⚠️ PyThra Framework | qasync not found, running standard Qt Event Loop.")
        sys.exit(app.exec())
    except Exception as e:
        debug_print(f"⚠️ PyThra Framework | Failed to start qasync event loop: {e}")
        sys.exit(app.exec())


"""
if __name__ == '__main__':

    # Create API instance and register callbacks
    api = Api()
    api.register_callback("bg", change_color)
    api.register_callback("testCallback", lambda: #print("Button clicked!"))
    window = create_window("Test Window", window_id="main_window", html_file="/home/red-x/Engine/ind.html", js_api=api, frameless=False)
    start(debug=True)

"""
