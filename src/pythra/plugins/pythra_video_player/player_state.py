from pythra.state import Key, State
from pythra.widgets import Container
from .style import PlayerStyle


class _VideoPlayerState(State):
    def initState(self):
        super().initState()

    def build(self):
        return Container(
            key=Key(f"{self.widget.get_unique_id()}_container"),
            style=PlayerStyle.container(self.widget.width, self.widget.height),
            js_init={
                "engine": "PythraVideoPlayer",
                "auto_play": self.widget.auto_play,
                "instanceId": self.widget.get_unique_id(),
            },
        )
