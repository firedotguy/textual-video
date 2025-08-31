from textual_video.player import VideoPlayer
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual_video.enums import ImageType, UpdateStrategy
from textual.widgets import Static

class ExampleApp(App):

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(
                Static('reactive'),
                VideoPlayer(r'examples\video.mp4', image_type=ImageType.HALFCELL, speed=2, update_strategy=UpdateStrategy.REACTIVE),
            ),
            Vertical(
                Static('remount'),
                VideoPlayer(r'examples\video.mp4', image_type=ImageType.HALFCELL, speed=2, update_strategy=UpdateStrategy.REMOUNT),
            ),
            Vertical(
                Static('set image'),
                VideoPlayer(r'examples\video.mp4', image_type=ImageType.HALFCELL, speed=2, update_strategy=UpdateStrategy.SET_IMAGE),
            ),
        )

if __name__ == '__main__':
    ExampleApp().run()