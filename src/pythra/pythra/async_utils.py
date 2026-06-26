"""
Async helpers for Pythra: a shared ThreadPool and main-thread dispatcher.

DO NOT PUT FRAMEWORK-SPECIFIC LOGIC HERE. Keep this module minimal and
easy to mock in tests. It exposes:
- `submit_task(callable) -> concurrent.futures.Future`
- `dispatch_to_main(callable)` which uses `QTimer.singleShot(0, ...)`
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Optional, Any
from PySide6.QtCore import QTimer
from PySide6.QtCore import QObject, Slot, QMetaObject, Qt, Signal, QCoreApplication, QThread, QEventLoop

# Module-level singleton executor. Consumers may override by assigning
# to `executor` for testing or configuration.
executor: Optional[ThreadPoolExecutor] = None


# A small QObject that lives on the Qt main thread and exposes a slot
# to invoke Python callables. Using QMetaObject.invokeMethod with
# Qt.QueuedConnection guarantees the call will be executed on the
# receiver's thread (i.e. the main Qt thread) even when invoked from
# a worker thread.
class _MainInvoker(QObject):
    invoke_signal = Signal(object)

    def __init__(self):
        super().__init__()
        self.invoke_signal.connect(self._on_invoke)

    @Slot(object)
    def _on_invoke(self, cb: Callable[[], None]):
        try:
            cb()
        except Exception as e:
            print(f"Exception in dispatched callback: {e}")


# The invoker is lazily created so we can ensure it is moved to the
# application's main thread when possible.
_INVOKER: Optional[_MainInvoker] = None


def _ensure_invoker() -> _MainInvoker:
    global _INVOKER
    if _INVOKER is None:
        _INVOKER = _MainInvoker()
        try:
            app = QCoreApplication.instance()
            if app is not None:
                # Move the invoker to the application's main thread
                _INVOKER.moveToThread(app.thread())
        except Exception:
            pass
    return _INVOKER


def get_executor(max_workers: int = 4) -> ThreadPoolExecutor:
    global executor
    if executor is None:
        executor = ThreadPoolExecutor(max_workers=max_workers)
    return executor


def submit_task(fn: Callable[[], object]) -> Future:
    """Submit a zero-arg callable to the shared thread pool and return a Future."""
    ex = get_executor()
    return ex.submit(fn)


def dispatch_to_main(cb: Callable[[], None]) -> None:
    """Schedule `cb` to run on the Qt main thread using QTimer.singleShot.

    Keep this wrapper so callers can mock or replace the dispatcher in tests.
    """
    # Prefer using QMetaObject.invokeMethod on the invoker with a
    # QueuedConnection so the callable runs on the invoker's thread.
    try:
        inv = _ensure_invoker()
        print(f"Dispatching to main thread via invoker.signal.emit... {cb}")
        inv.invoke_signal.emit(cb)
        print("Dispatched to main thread (signal emitted).")
        return
    except Exception as e:
        print(f"Signal dispatch failed: {e}; falling back to QTimer.singleShot")

    try:
        QTimer.singleShot(0, cb)
        print("Dispatched to main thread via QTimer.singleShot.")
    except Exception as e:
        print(f"Error dispatching to main thread: {e}")

import functools

def background_task(func):
    """
    Decorator to execute a function asynchronously in the PyThra background thread pool.
    Returns the Future object so callers can optionally await or add callbacks.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        fut = submit_task(lambda: func(*args, **kwargs))
        def _check_err(f):
            try:
                f.result()
            except Exception as e:
                print(f"⚠️ Exception in @background_task {func.__name__}: {e}")
                import traceback
                traceback.print_exc()
        fut.add_done_callback(_check_err)
        return fut
    return wrapper

def ui_thread(func):
    """
    Decorator to guarantee a function executes safely on the main Qt UI thread.
    Useful for callback methods that need to update PyThra State or UI elements.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        dispatch_to_main(lambda: func(*args, **kwargs))
    return wrapper


# ── Synchronous JS Evaluation ─────────────────────────────────────────

def evaluate_js_sync(script: str, window_id: Optional[str] = None) -> Any:
    """
    Evaluate a JavaScript expression and return its result synchronously.

    If called from the main Qt UI thread, it spins a local QEventLoop to avoid
    deadlocking the application while waiting for the QWebEngineView's async callback.
    If called from a background worker thread, it dispatches the call to the UI
    thread and blocks the background thread until the result is ready.
    """
    from .core import Framework
    from .window import webwidget

    fw = Framework.instance()
    if not fw or not fw.window:
        raise RuntimeError("PyThra Framework window is not initialized.")

    w_id = window_id or getattr(fw, "id", "main_window_id")
    window = webwidget.window_manager.windows.get(w_id)
    if not window or not hasattr(window, "webview") or not window.webview:
        raise ValueError(f"Window with ID '{w_id}' not found or has no webview.")

    # Check if we are executing on the main Qt UI thread
    is_main_thread = False
    app = QCoreApplication.instance()
    if app:
        is_main_thread = (QThread.currentThread() == app.thread())

    if is_main_thread:
        # UI Thread: spin a local event loop
        loop = QEventLoop()
        result_holder = {"value": None, "error": None}

        def cb(res):
            result_holder["value"] = res
            loop.quit()

        try:
            window.webview.page().runJavaScript(script, cb)
            loop.exec()
        except Exception as e:
            result_holder["error"] = e

        if result_holder["error"]:
            raise result_holder["error"]
        return result_holder["value"]

    else:
        # Background/Worker Thread: block thread using Future
        fut = Future()

        def run_on_ui():
            try:
                loop = QEventLoop()

                def cb(res):
                    fut.set_result(res)
                    loop.quit()

                window.webview.page().runJavaScript(script, cb)
                loop.exec()
            except Exception as e:
                fut.set_exception(e)

        dispatch_to_main(run_on_ui)
        return fut.result()
