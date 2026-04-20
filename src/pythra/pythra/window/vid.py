import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

import sys
import vlc

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Qt, QEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtGui import QKeySequence, QShortcut

class CustomWebPage(QWebEnginePage):
    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if "VID_RECT:" in message:
            try:
                rect_str = message.split("VID_RECT:")[1].strip()
                x, y, w, h = map(float, rect_str.split(","))
                self.main_app.update_video_rect(x, y, w, h)
            except Exception as e:
                pass
        super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)

class VLCPlayer(QWidget):
    def __init__(self, video_path, debug=False):
        super().__init__()
        self.debug = debug

        self.setWindowTitle("VLC in PySide6")
        self.resize(800, 600)

        # Video container (will be moved dynamically)
        self.video_frame = QWidget(self)
        self.video_frame.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.video_frame.setAttribute(Qt.WidgetAttribute.WA_DontCreateNativeAncestors, True)

        # 1b. Stylized UI Frame over Video (Rounded Corners)
        # self.frame_overlay = QWidget(self)
        # self.frame_overlay.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.WindowStaysOnTopHint)
        # self.frame_overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # self.frame_overlay.setStyleSheet("""
        #     background: transparent;
        #     border: 2px solid rgba(255,255,255,0.3);
        #     border-radius: 20px;
        # """)

        # Floating WebEngine Overlay (TOP)
        self.web_view = QWebEngineView(self)
        self.web_page = CustomWebPage(self, self.web_view)
        self.web_view.setPage(self.web_page)

        # Transparent overlay covering the ENTIRE window, no WindowTransparentForInput so you can scroll!
        self.web_view.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        )
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.web_view.page().setBackgroundColor(Qt.transparent)

        # Developer Tools window
        self.dev_tools_wrapper = QWidget()
        self.dev_tools_wrapper.setWindowTitle("Web Inspector (F12 to Toggle)")
        self.dev_tools_wrapper.resize(800, 600)
        self.dev_tools_wrapper.setWindowFlags(Qt.WindowType.Window)

        layout = QVBoxLayout(self.dev_tools_wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.dev_tools = QWebEngineView(self.dev_tools_wrapper)
        layout.addWidget(self.dev_tools)
        
        self.web_view.page().setDevToolsPage(self.dev_tools.page())
        
        # Toggle DevTools shortcut
        self.shortcut = QShortcut(QKeySequence("F12"), self)
        self.shortcut.activated.connect(self.toggle_dev_tools)

        overlay_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body { 
                margin: 0; 
                padding: 0; 
                background: transparent; 
                overflow-y: auto; 
                overflow-x: hidden;
                font-family: sans-serif;
            }
            .content {
                height: 2000px;
                position: relative;
            }
            .vid-box { 
                position: absolute;
                top: 400px; /* Put it somewhere down the page to force scrolling */
                left: 100px;
                width: 600px; 
                height: 350px;
                background: transparent; 
                border-radius: 24px;
                box-shadow: 0 0 0 9999px rgba(44, 62, 80, 0.95);
                box-sizing: border-box; 
                z-index: 1;
            }
            #shadow-canvas {
                position: absolute;
                top: -50px;
                left: -50px;
                pointer-events: none; 
                z-index: 1;
            }
            .border-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                box-sizing: border-box; 
                border-radius: inherit; 
                border: 3px solid rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 1.25rem;
                color: white;
                z-index: 2; 
            }
            .instruction {
                font-size: 24px;
                color: white;
                background: rgba(0,0,0,0.5);
                padding: 20px;
                margin: 20px;
                border-radius: 10px;
                position: relative;
                z-index: 10;
            }
        </style>
        </head>
        <body>
            <div class="content">
                <div class="instruction">Scroll down to find the video box! ⬇️</div>
                <div class="vid-box" id="vid-box">
                    <canvas id="shadow-canvas"></canvas>
                    <div class="border-overlay">Floating card</div>
                </div>
                <div class="instruction" style="position: absolute; top: 800px; width: calc(100% - 40px);">Keep scrolling... the video will easily clip!</div>
            </div>
            <script>
                function sendRect() {
                    let box = document.getElementById('vid-box');
                    let rect = box.getBoundingClientRect();
                    console.log("VID_RECT:" + rect.x + "," + rect.y + "," + rect.width + "," + rect.height);
                }
                
                const canvas = document.getElementById('shadow-canvas');
                const ctx = canvas.getContext('2d');
                const holeElement = document.getElementById('vid-box');

                const offsetY = 10;
                const blur = 20;
                const spread = 19;
                const shadowColor = 'red';
                const padding = 50; 

                function drawDynamicShadow() {
                  const rect = holeElement.getBoundingClientRect();
                  const holeWidth = rect.width;
                  const holeHeight = rect.height;
                  
                  const computedStyle = window.getComputedStyle(holeElement);
                  const holeRadius = parseFloat(computedStyle.borderRadius) || 0;

                  canvas.width = holeWidth + (padding * 2);
                  canvas.height = holeHeight + (padding * 2);

                  ctx.shadowColor = shadowColor;
                  ctx.shadowOffsetY = offsetY;
                  ctx.shadowOffsetX = 9999;
                  ctx.shadowBlur = blur;

                  // Render the actual form way off-screen (X - 9999) so it doesn't leave a black ring
                  // Because shadowOffsetX is +9999, the shadow will project precisely into view!
                  ctx.fillStyle = 'black'; 
                  ctx.beginPath();
                  if (ctx.roundRect) {
                      ctx.roundRect(
                        (padding - spread) - 9999,           
                        padding - spread,           
                        holeWidth + (spread * 2),   
                        holeHeight + (spread * 2),  
                        holeRadius + (spread / 2)   
                      );
                  } else {
                      ctx.rect((padding - spread) - 9999, padding - spread, holeWidth + (spread * 2), holeHeight + (spread * 2));
                  }
                  ctx.fill();

                  // Surgically clean out the inner boundary hole where video shines through
                  ctx.globalCompositeOperation = 'destination-out';
                  ctx.shadowColor = 'transparent'; 
                  ctx.shadowOffsetX = 0; // reset shadow offset before erasing
                  
                  ctx.beginPath();
                  if (ctx.roundRect) {
                      ctx.roundRect(padding, padding, holeWidth, holeHeight, holeRadius);
                  } else {
                      ctx.rect(padding, padding, holeWidth, holeHeight);
                  }
                  ctx.fill();
                  
                  ctx.globalCompositeOperation = 'source-over'; 
                }

                // Track scrolls, resizes, and run initially
                window.addEventListener('scroll', sendRect);
                window.addEventListener('resize', () => {
                    sendRect();
                    drawDynamicShadow();
                });
                
                setTimeout(() => {
                    sendRect();
                    drawDynamicShadow();
                }, 50);
                setTimeout(() => {
                    sendRect();
                    drawDynamicShadow();
                }, 500);
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(overlay_html)

        # Create VLC instance + player
        self.instance = vlc.Instance("--no-xlib")
        self.player = self.instance.media_player_new()

        # Load media
        media = self.instance.media_new(video_path)
        self.player.set_media(media)

        # Important: delay attaching until widget is ready
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.attach_player)
        self.timer.start(100)

    def attach_player(self):
        win_id = int(self.video_frame.winId())

        if sys.platform.startswith("linux"):
            self.player.set_xwindow(win_id)
        elif sys.platform == "win32":
            self.player.set_hwnd(win_id)
        elif sys.platform == "darwin":
            self.player.set_nsobject(win_id)

        self.player.play()

    def update_video_rect(self, x, y, w, h):
        self.video_frame.setGeometry(int(x), int(y), int(w), int(h))
        if hasattr(self, "frame_overlay"):
            global_pos = self.mapToGlobal(self.rect().topLeft())
            self.frame_overlay.setGeometry(
                global_pos.x() + int(x), global_pos.y() + int(y), int(w), int(h)
            )

    def moveEvent(self, event):
        super().moveEvent(event)
        self.update_overlay_pos()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_overlay_pos()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_overlay_pos()
        if hasattr(self, "frame_overlay"):
            self.frame_overlay.show()
        if hasattr(self, "web_view"):
            self.web_view.show()

    def closeEvent(self, event):
        super().closeEvent(event)
        if hasattr(self, "frame_overlay"):
            self.frame_overlay.close()
        if hasattr(self, "web_view"):
            self.web_view.close()
        if hasattr(self, "dev_tools_wrapper"):
            self.dev_tools_wrapper.close()

    def toggle_dev_tools(self):
        if not self.debug:
            return
        if hasattr(self, "dev_tools_wrapper"):
            if self.dev_tools_wrapper.isVisible():
                self.dev_tools_wrapper.hide()
            else:
                self.dev_tools_wrapper.show()
                self.dev_tools_wrapper.raise_()

    def changeEvent(self, event):
        super().changeEvent(event)
        # Manually hide WebEngine overlays before Chromium can protest being minimized
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                # Disconnect DevTools to prevent "Failed to transition to Discarded state: DevTools open" crash
                if hasattr(self, "web_view"):
                    try:
                        self.web_view.page().setDevToolsPage(None)
                    except Exception:
                        pass
                    self.web_view.hide()
                if hasattr(self, "dev_tools_wrapper") and self.dev_tools_wrapper.isVisible():
                    self.dev_tools_wrapper.hide()
                    self._dev_tools_was_visible = True
            else:
                if hasattr(self, "web_view"):
                    self.web_view.show()
                if hasattr(self, "_dev_tools_was_visible") and self._dev_tools_was_visible:
                    # Reconnect DevTools automatically on restore
                    if hasattr(self, "web_view") and hasattr(self, "dev_tools"):
                        self.web_view.page().setDevToolsPage(self.dev_tools.page())
                    self.dev_tools_wrapper.show()
                    self._dev_tools_was_visible = False

    def update_overlay_pos(self):
        if hasattr(self, 'web_view'):
            global_pos = self.mapToGlobal(self.rect().topLeft())
            self.web_view.setGeometry(global_pos.x(), global_pos.y(), self.width(), self.height())
            self.web_view.page().runJavaScript(
                "if (typeof sendRect !== 'undefined') sendRect();"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    player = VLCPlayer("/home/red-x/Videos/In Your Radiant Season/In Your Radiant Season Episode 11.mkv", debug=True)  # <-- change this
    player.show()

    sys.exit(app.exec())
