

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow
from PySide6.QtCore import Qt, QObject, Slot, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel
import sys

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
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        # Maximize the window
        self.showMaximized()
        self.layout = QVBoxLayout(self)
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
        self.webview.setUrl(QUrl.fromLocalFile('/home/red-x/Documents/pythra-toolkit/src/pythra/pythra/window/vid.html'))
        self.layout.addWidget(self.webview) 
        # Developer Tools
        self.debug_window = DebugWindow()
        self.webview.page().setDevToolsPage(self.debug_window.page())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec())
