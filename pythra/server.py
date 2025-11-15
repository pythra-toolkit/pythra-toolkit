# pythra/server.py

import http.server
import socketserver
import threading
import os
import atexit
import signal
from pathlib import Path
from typing import Dict

class MultiDirectoryRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom request handler that can serve files from multiple directories
    based on the request URL path.

    - Requests to `/` are served from the main `base_directory`.
    - Requests to `/<prefix>/...` are served from the corresponding extra directory.
    """
    base_directory: str = None
    extra_directories: Dict[str, str] = {}

    def __init__(self, *args, **kwargs):
        # We need to set the base directory for the parent class to work.
        # The actual routing will happen in our overridden translate_path.
        super().__init__(*args, directory=self.base_directory, **kwargs)

    def translate_path(self, path: str) -> str:
        """
        Translates a URL path to a local filesystem path based on our routing rules.
        """
        # Remove query parameters from the path
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Check for a matching prefix from our extra directories
        for prefix, fs_path in self.extra_directories.items():
            # Ensure prefix starts and ends with a slash for clean matching
            url_prefix = f"/{prefix.strip('/')}/"
            if path.startswith(url_prefix):
                # It's a plugin asset. Rebuild the path.
                # Example: /plugins/editor/style.css -> C:/project/plugins/editor/public/style.css
                relative_path = path[len(url_prefix):]
                translated_path = os.path.join(fs_path, relative_path)
                print(f"[AssetServer] Plugin request: '{path}' -> '{translated_path}'")
                return translated_path

        # If no prefix matched, it's a standard asset.
        # Let the parent class handle it relative to the base directory.
        translated_path = super().translate_path(path)
        print(f"[AssetServer] Base asset request: '{path}' -> '{translated_path}'")
        return translated_path

    def end_headers(self):
        """Add CORS headers to allow cross-origin requests (e.g., for fonts)."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Range')
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()


class AssetServer(threading.Thread):
    """
    A multi-directory static file server that runs in a background thread.
    It serves a main asset directory and additional directories for plugins.
    """
    def __init__(self, directory: str, port: int = 8000, extra_serve_dirs: Dict[str, str] = None):
        """
        Args:
            directory (str): The main directory to serve files from (e.g., project's `assets`).
            port (int): The port to listen on.
            extra_serve_dirs (Dict[str, str]): A mapping of URL prefixes to filesystem
                                              directories for plugins.
                                              e.g., {"plugins/editor": "/path/to/editor/public"}
        """
        super().__init__()
        # Run the server thread as a daemon so it won't block interpreter exit
        # if everything else has finished. This makes shutdown behavior simpler.
        self.daemon = True
        self.directory = directory
        self.port = port
        self.extra_serve_dirs = extra_serve_dirs or {}
        self.server = None
        self._shutdown_registered = False

    def run(self):
        """Starts the HTTP server on a separate thread."""
        
        # Create a custom handler class for this specific server instance
        # This is how we pass our directories to the handler.
        class Handler(MultiDirectoryRequestHandler):
            base_directory = self.directory
            extra_directories = self.extra_serve_dirs

        # Use a context manager for robust server setup and teardown
        # Use context manager for robust server setup and teardown

        try:
            with socketserver.TCPServer(("", self.port), Handler) as httpd:
                print(f"✅ Asset server started on http://localhost:{self.port}")
                print(f"   Serving main assets from: {self.directory}")
                for prefix, path in self.extra_serve_dirs.items():
                    print(f"   Serving plugin '{prefix}' from: {path}")
                
                self.server = httpd
                httpd.serve_forever()
        except OSError as e:
            print(f"❌ FATAL: Could not start asset server on port {self.port}. Is it already in use?")
            print(f"   Error: {e}")
            # In a real app, you might want a more graceful exit here.
            os._exit(1) # Force exit if server can't start

    def start(self):
        """Start the thread and ensure shutdown hooks are registered from
        the thread that calls `start()` (typically the main thread).
        """
        try:
            self.register_shutdown_hooks()
        except Exception:
            # Non-fatal: proceed even if hooks can't be registered
            pass
        super().start()

    def stop(self):
        """Stops the HTTP server if it is running."""
        if self.server:
            print("[AssetServer] Shutting down...")
            self.server.shutdown()
            self.server.server_close()
            print("[AssetServer] Shutdown complete.")

    def register_shutdown_hooks(self):
        """Register atexit and signal handlers to ensure the server is shut down
        when the process exits or receives termination signals.

        This method is safe to call multiple times; handlers will only be
        registered once per instance.
        """
        if self._shutdown_registered:
            return

        # Ensure the server is stopped at normal interpreter exit
        try:
            atexit.register(self.stop)
            print("[AssetServer] Registered atexit shutdown handler.")
        except Exception as e:
            print(f"[AssetServer] Warning: failed to register atexit handler: {e}")

        # Signal handlers: attempt to handle SIGINT and SIGTERM where available
        def _make_handler(sig_name):
            def _handler(signum, frame):
                print(f"[AssetServer] Received {sig_name} ({signum}), shutting down asset server...")
                try:
                    self.stop()
                except Exception as ex:
                    print(f"[AssetServer] Error during shutdown: {ex}")
                # Exit the process after cleanup.
                try:
                    os._exit(0)
                except Exception:
                    pass
            return _handler

        for sig, name in ((getattr(signal, 'SIGINT', None), 'SIGINT'), (getattr(signal, 'SIGTERM', None), 'SIGTERM')):
            if sig is None:
                continue
            try:
                signal.signal(sig, _make_handler(name))
                print(f"[AssetServer] Registered signal handler for {name}.")
            except Exception as e:
                # On some platforms (e.g., certain Windows consoles) signal registration
                # may fail for SIGTERM; ignore non-fatal failures.
                print(f"[AssetServer] Warning: could not register handler for {name}: {e}")

        self._shutdown_registered = True