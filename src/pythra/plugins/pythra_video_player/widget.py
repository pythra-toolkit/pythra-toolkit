from pythra.state import StatefulWidget
from .player_state import _VideoPlayerState

class VideoPlayer(StatefulWidget):
    def __init__(self, key=None, width="100%", height="400px", auto_play=False, **kwargs):
        super().__init__(key=key, **kwargs)
        self.width = width
        self.height = height
        self.auto_play = auto_play

    def createState(self):
        return _VideoPlayerState()
