from textual_video.player import VideoPlayer
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual_video.enums import ImageType, UpdateStrategy
from textual import log

class ExampleApp(App):

    def compose(self) -> ComposeResult:
        player = VideoPlayer(
            r'examples\video.mp4',
            image_type=ImageType.SIXEL,
            update_strategy=UpdateStrategy.REACTIVE,
            fps_decrease_factor=2
        )
        yield player

if __name__ == '__main__':
    ExampleApp().run()