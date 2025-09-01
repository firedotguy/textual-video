from textual_video.player import VideoPlayer
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual_video.enums import ImageType, UpdateStrategy

class ExampleApp(App):

    def compose(self) -> ComposeResult:
        yield VideoPlayer(r'examples\video.mp4', fps_decrease_factor=10, update_strategy=UpdateStrategy.REACTIVE)

if __name__ == '__main__':
    ExampleApp().run()