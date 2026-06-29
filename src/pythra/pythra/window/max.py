

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow
from PySide6.QtCore import Qt, QObject, Slot, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel
import sys

class Bridge(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window

    @Slot()
    def startWindowDrag(self):
        if self.window.windowHandle():
            self.window.windowHandle().startSystemMove()

    @Slot(int)
    def startWindowResize(self, edge):
        if self.window.windowHandle():
            self.window.windowHandle().startSystemResize(Qt.Edge(edge))

    @Slot(str)
    def on_pressed_str(self, name):
        pass

    @Slot(str, str)
    def on_input_changed(self, name, value):
        pass

    @Slot(str, float, bool)
    def on_drag_update(self, name, value, dragBool):
        pass

class DebugWindow(QWebEngineView):
    """A separate window for inspecting HTML elements."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug Window")
        self.resize(800, 600)

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maximized PySide6 Window")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Maximize the window
        # self.showMaximized()
        self.resize(800, 600)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.webview = QWebEngineView(self)
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
        
        # Suppress various console warnings and messages
        self.webview.settings().setAttribute(
            QWebEngineSettings.ShowScrollBars, False
        )
        self.webview.page().setBackgroundColor(Qt.transparent)
        self.webview.setUrl(QUrl.fromLocalFile('/home/red-x/Documents/pythra-toolkit/src/pythra/pythra/window/ind.html'))
        self.layout.addWidget(self.webview) 

        self.channel = QWebChannel()
        self.bridge = Bridge(self)
        self.channel.registerObject("pywebview", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        # Developer Tools
        self.debug_window = DebugWindow()
        self.webview.page().setDevToolsPage(self.debug_window.page())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
