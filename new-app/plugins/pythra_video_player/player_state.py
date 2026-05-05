import sys
import subprocess
import time
import os
import signal

from pythra import State, Container, Framework, Key
from PySide6.QtCore import Signal, QThread
from PySide6.QtWebSockets import QWebSocketServer
from PySide6.QtNetwork import QHostAddress

framework = Framework.instance()


def get_audio_args():
    if sys.platform.startswith('linux'):
        return ['-f', 'alsa', 'default']
    elif sys.platform == 'darwin':
        return ['-f', 'audiotoolbox', 'default']
    elif sys.platform == 'win32':
        return ['-f', 'dsound', 'default']
    return ['-f', 'sdl', 'default']


class FFmpegWorker(QThread):
    frame_ready = Signal(bytes)

    def __init__(self, video_path: str, seek_sec: float):
        super().__init__()
        self.video_path = video_path
        self.seek_sec = seek_sec
        self.is_running = True
        self.process = None

    def run(self):
        audio_args = get_audio_args()
        cmd = [
            'ffmpeg', '-re',
            '-ss', str(self.seek_sec),
            '-i', self.video_path,
            '-af', 'aresample=async=1',
            '-f', 'image2pipe',
            '-vcodec', 'mjpeg',
            '-q:v', '5',
            '-fps_mode', 'cfr',
            '-threads', '0',
            '-' # stdout
        ] + audio_args

        kwargs = {}
        if sys.platform != 'win32':
            kwargs['start_new_session'] = True

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**7,
                **kwargs
            )
        except Exception as e:
            print(f"⚠️  pythra-video-player | FFmpeg start error: {e}")
            return

        buffer = b''
        while self.is_running and self.process:
            try:
                # Optimized chunk size to 64KB for faster IO reads on high-bandwidth local pipes
                chunk = self.process.stdout.read(65536)
                if not chunk:
                    break
                buffer += chunk

                while True:
                    start = buffer.find(b'\xff\xd8')
                    if start == -1:
                        buffer = buffer[-2:]
                        break

                    end = buffer.find(b'\xff\xd9', start)
                    if end == -1:
                        break

                    jpeg_data = buffer[start:end+2]
                    buffer = buffer[end+2:]
                    self.frame_ready.emit(jpeg_data)
            except Exception:
                break
        
        self.is_running = False
        self._cleanup()

    def stop(self):
        self.is_running = False
        self._cleanup()

    def _cleanup(self):
        if self.process:
            try:
                if sys.platform != 'win32':
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
            except Exception:
                pass
            self.process = None


import json

class VideoPlayerState(State):
    def __init__(self):
        super().__init__()
        self._server = None
        self._port = None
        self._clients = []
        
        self._worker = None
        self._start_time = 0
        self._seek_offset = 0
        self._is_paused = False
        
        self._duration = 0.0
        self._status_timer = None
        
        self._cached_js_init = None

    def initState(self):
        from PySide6.QtCore import QTimer
        
        widget = self.widget
        if not widget:
            return

        if widget.controller:
            widget.controller._attach(self)

        # Start PySide6 WebSocket Server for delivering MJPEG frames and Status locally
        self._server = QWebSocketServer("PythraVideo", QWebSocketServer.NonSecureMode)
        if self._server.listen(QHostAddress.LocalHost):
            self._port = self._server.serverPort()
            self._server.newConnection.connect(self._on_new_connection)
        else:
            print("⚠️  pythra-video-player | Failed to start QWebSocketServer.")

        self._deferred_register_callbacks()
        
        if widget.video_path:
            self._duration = self._fetch_duration(widget.video_path)
            self._start_ffmpeg(0)
            
        # Start a 250ms tick to broadcast JSON status
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._broadcast_status)
        self._status_timer.start(250)

    def _fetch_duration(self, video_path: str) -> float:
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                   '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
            output = subprocess.check_output(cmd).decode().strip()
            return float(output) if output else 0.0
        except Exception as e:
            print(f"⚠️  pythra-video-player | FFprobe duration error: {e}")
            return 0.0

    def _on_new_connection(self):
        client = self._server.nextPendingConnection()
        self._clients.append(client)
        client.disconnected.connect(lambda c=client: self._clients.remove(c) if c in self._clients else None)

    def _start_ffmpeg(self, seek_sec: float):
        self._stop_ffmpeg()
        widget = self.widget
        if not widget or not widget.video_path:
            return

        self._is_paused = False
        self._is_buffering = True  # New: synchronizes time mathematically with first frame
        self._seek_offset = seek_sec
        # _start_time deferred to first frame emission
        
        self._worker = FFmpegWorker(widget.video_path, seek_sec)
        self._worker.frame_ready.connect(self._broadcast_frame)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_worker_finished(self):
        # Native EOF or stream break triggers auto-pause
        if not self._is_paused:
            self._seek_offset = self._get_current_time()
            if self._duration > 0:
                self._seek_offset = min(self._seek_offset, self._duration)
            self._is_paused = True

    def _stop_ffmpeg(self):
        if self._worker:
            try:
                self._worker.finished.disconnect(self._on_worker_finished)
            except Exception:
                pass
            self._worker.stop()
            self._worker.wait()
            self._worker = None

    def _get_current_time(self) -> float:
        if self._is_paused or getattr(self, '_is_buffering', False):
            current = self._seek_offset
        elif self._worker and getattr(self._worker, 'is_running', False):
            current = self._seek_offset + (time.time() - getattr(self, '_start_time', time.time()))
        else:
            current = self._seek_offset

        if getattr(self, '_duration', 0.0) > 0:
            current = min(current, self._duration)
        return current

    def _broadcast_frame(self, frame_data: bytes):
        if getattr(self, '_is_buffering', False):
            self._start_time = time.time()
            self._is_buffering = False
        
        for client in self._clients:
            try:
                client.sendBinaryMessage(frame_data)
            except Exception:
                pass

    def _broadcast_status(self):
        if not self._clients: return
        status = {
            "time": self._get_current_time(),
            "duration": self._duration,
            "is_playing": not self._is_paused and self._worker is not None
        }
        status_str = json.dumps(status)
        for client in self._clients:
            try:
                client.sendTextMessage(status_str)
            except Exception:
                pass

    def _deferred_register_callbacks(self):
        from PySide6.QtCore import QTimer
        widget = self.widget
        if not widget: 
            return

        cmd_callback_name = f"_pythra_video_cmd_{widget.key.value}"
        if framework.api:
            framework.api.register_callback(cmd_callback_name, self._on_video_command)
        else:
            QTimer.singleShot(500, self._deferred_register_callbacks)

    def _on_video_command(self, cmd_type: str, value: str):
        if cmd_type == "volume":
            try: pass
            except ValueError: pass
        elif cmd_type == "seek":
            try:
                # Now seek receives exact percentage/float point from slider if needed.
                # If it's "forward"/"backward" it acts relatively.
                current = self._get_current_time()
                if value == "forward":
                    new_pos = max(0.0, current + 5.0)
                elif value == "backward":
                    new_pos = max(0.0, current - 5.0)
                else:
                    new_pos = float(value) * self._duration
                self._ffmpeg_seek(new_pos * 1000)
            except ValueError:
                pass
        elif cmd_type == "play":
            self._ffmpeg_play()
        elif cmd_type == "pause":
            self._ffmpeg_pause()

    # --- Controller Commands ---

    def _vlc_play(self):
        self._ffmpeg_play()
        
    def _vlc_pause(self):
        self._ffmpeg_pause()
        
    def _vlc_stop(self):
        self._ffmpeg_stop()
        
    def _vlc_seek(self, position_ms: int):
        self._ffmpeg_seek(position_ms)
        
    def _vlc_set_volume(self, volume: int):
        self._ffmpeg_set_volume(volume)
        
    def _vlc_set_video(self, video_path: str):
        self._ffmpeg_set_video(video_path)
        
    def _vlc_is_playing(self) -> bool:
        return self._ffmpeg_is_playing()

    # --- Internal Handlers ---

    def _ffmpeg_play(self):
        if self._is_paused:
            self._start_ffmpeg(self._seek_offset)

    def _ffmpeg_pause(self):
        if not self._is_paused:
            self._seek_offset = self._get_current_time()
            self._stop_ffmpeg()
            self._is_paused = True

    def _ffmpeg_stop(self):
        self._seek_offset = 0
        self._stop_ffmpeg()
        self._is_paused = True

    def _ffmpeg_seek(self, position_ms: int):
        # We cap seeks dynamically using known duration
        new_sec = position_ms / 1000.0
        if self._duration > 0:
            new_sec = min(self._duration, new_sec)
        self._start_ffmpeg(new_sec)

    def _ffmpeg_set_volume(self, volume: int):
        pass

    def _ffmpeg_set_video(self, video_path: str):
        if self.widget:
            self.widget.video_path = video_path
        self._duration = self._fetch_duration(video_path)
        self._start_ffmpeg(0)

    def _ffmpeg_is_playing(self) -> bool:
        return not self._is_paused and self._worker is not None

    def dispose(self):
        widget = self.widget
        if widget and widget.controller:
            widget.controller._detach()

        if widget and framework.api:
            cmd_cb = f"_pythra_video_cmd_{widget.key.value}"
            if cmd_cb in framework.api.callbacks:
                del framework.api.callbacks[cmd_cb]

        if self._status_timer:
            self._status_timer.stop()

        self._stop_ffmpeg()
        
        if self._server:
            self._server.close()
            self._server.deleteLater()
            self._server = None
        
        super().dispose()

    def didUpdateWidget(self, old_widget, new_widget):
        super().didUpdateWidget(old_widget, new_widget)
        
        # If dimensions changed, update the cached init
        if old_widget.width != new_widget.width or old_widget.height != new_widget.height:
            if self._cached_js_init:
                self._cached_js_init["options"]["width"] = new_widget.width
                self._cached_js_init["options"]["height"] = new_widget.height

    def build(self):
        widget = self.widget
        if not widget:
            return Container(width=0, height=0)

        if self._cached_js_init is None:
            cmd_callback_name = f"_pythra_video_cmd_{widget.key.value}"
            self._cached_js_init = {
                "engine": "PythraVideoPlayer",
                "instance_name": f"{widget.key.value}_PythraVideoPlayer",
                "options": {
                    "instanceId": f"{widget.key.value}_PythraVideoPlayer",
                    "cmdCallbackName": cmd_callback_name,
                    "width": widget.width,
                    "height": widget.height,
                    "port": self._port,
                    "style": widget.style.to_dict() if hasattr(widget.style, "to_dict") else {},
                },
            }

        container_key = Key(f"{widget.key.value}_container") if widget.key else None

        return Container(
            key=container_key,
            width=widget.width,
            height=widget.height,
            js_init=self._cached_js_init,
        )
