class PlayerStyle:
    @staticmethod
    def container(width, height):
        return {
            "width": width,
            "height": height,
            "background-color": "#000",
            "border-radius": "8px",
            "display": "flex",
            "flex-direction": "column",
            "align-items": "center",
            "justify-content": "center",
            "overflow": "hidden",
            "position": "relative"
        }
