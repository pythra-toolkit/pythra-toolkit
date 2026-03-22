from __future__ import annotations

from typing import Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum, auto

from .base import Widget, Key
from .state import StatefulWidget, State
from .async_utils import submit_task, dispatch_to_main
from PySide6.QtCore import QTimer
from .core import Framework


class ConnectionState(Enum):
    NONE = auto()
    WAITING = auto()
    ACTIVE = auto()
    DONE = auto()


@dataclass
class Snapshot:
    connectionState: ConnectionState
    data: Optional[Any] = None
    error: Optional[BaseException] = None

    @property
    def hasData(self) -> bool:
        return self.data is not None

    @property
    def hasError(self) -> bool:
        return self.error is not None


class FutureBuilder(StatefulWidget):
    """A widget that runs a Future/callable on a worker pool and rebuilds
    with snapshot updates on the main thread.

    Parameters:
    - future: zero-arg callable or concurrent.futures.Future-like object, (most have atleast 3 sec delay, (working on fixing that))
    - builder: callable(context, snapshot) -> Widget
    - initialData: optional initial value
    - key: optional widget key
    """

    def __init__(
        self,
        future,
        builder: Callable[[object, Snapshot], Widget],
        initialData: Any = None,
        key: Optional[Key] = None, # type: ignore
        retry_policy: Optional[object] = None,
    ):
        self.future = future
        self.builder = builder
        self.initialData = initialData
        self.retry_policy = retry_policy
        super().__init__(key=key)

    def createState(self) -> State:
        return _FutureBuilderState()


class _FutureBuilderState(State):
    def __init__(self):
        super().__init__()
        self._snapshot = Snapshot(connectionState=ConnectionState.NONE)
        self._active_token = 0
        self._future_handle = None
        self._disposed = False

    def initState(self):
        # The core framework now safely defers reconciliation until the 
        # QtWebEngineView document is completely ready, so we can start immediately!
        self._start_if_needed(self.widget.future)

    def didUpdateWidget(self, oldWidget, new_widget):
        # If the future identity changed, restart
        if oldWidget.future != new_widget.future:
            self._cancel_active()
            self._start_if_needed(new_widget.future)

    def dispose(self):
        self._disposed = True
        self._cancel_active()

    def _start_if_needed(self, future_param):
        if future_param is None:
            return

        token = self._active_token + 1
        self._active_token = token

        # set waiting snapshot and request a rebuild
        self._snapshot = Snapshot(
            connectionState=ConnectionState.WAITING, data=self.widget.initialData
        )
        self.setState()

        # If future_param is a callable, submit it; if it looks like a Future, observe it
        try:
            if callable(future_param):
                fut = submit_task(future_param)
            else:
                # Assume it's a Future-like object
                fut = future_param

            self._future_handle = fut

            # Attach a done callback that marshals to main thread
            def _on_done_callback(f: Any, token=token):
                print(f"Future done callback triggered for token {token}")
                def _deliver():
                    print(f"Delivering future result for token {token}...")
                    # ignore if disposed or stale
                    if self._disposed or token != self._active_token:
                        print(f"Future result ignored for token {token} (disposed={self._disposed}, active_token={self._active_token})")
                        return
                    try:
                        result = f.result()
                        print(f"Future result obtained for token {token}: {result}")
                        self._snapshot = Snapshot(
                            connectionState=ConnectionState.DONE, data=result
                        )
                    except BaseException as e:
                        self._snapshot = Snapshot(
                            connectionState=ConnectionState.DONE, error=e
                        )
                    # Ask framework to rebuild
                    self.setState()

                dispatch_to_main(_deliver)

            try:
                fut.add_done_callback(_on_done_callback)
            except Exception:
                # Some Future implementations may not support add_done_callback
                # Fallback: poll in background (best-effort)
                def _poll_and_deliver():
                    try:
                        res = fut.result()

                        def _cb():
                            if self._disposed or token != self._active_token:
                                return
                            self._snapshot = Snapshot(
                                connectionState=ConnectionState.DONE, data=res
                            )
                            self.setState()

                        dispatch_to_main(_cb)
                    except BaseException as e:

                        def _cb_err():
                            if self._disposed or token != self._active_token:
                                return
                            self._snapshot = Snapshot(
                                connectionState=ConnectionState.DONE, error=e
                            )
                            self.setState()

                        dispatch_to_main(_cb_err)

                # start a small helper background submit to wait on fut
                submit_task(lambda: _poll_and_deliver())

        except BaseException as e:
            # Immediate failure
            self._snapshot = Snapshot(connectionState=ConnectionState.DONE, error=e)
            self.setState()

    def _cancel_active(self):
        h = self._future_handle
        try:
            if h and hasattr(h, "cancel"):
                h.cancel()
        except Exception:
            pass
        self._future_handle = None

    def build(self):
        # Provide the snapshot to the builder; builder should return a Widget
        return self.widget.builder(self, self._snapshot)
