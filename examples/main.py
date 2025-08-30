from textual_video.player import VideoPlayer
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual_video.enums import ImageType

class ExampleApp(App):

    def compose(self) -> ComposeResult:
        yield Horizontal(
            VideoPlayer(r'examples\video.mp4', image_type=ImageType.SIXEL, speed=2),
        )

if __name__ == '__main__':
    ExampleApp().run()