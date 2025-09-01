from textual.containers import Horizontal
from textual.geometry import Size
from textual.widgets import Static
from .enums import TimeDisplayMode
from .utils import format_time
from .metadata import VideoMetadata

class PlayerControls(Horizontal):
    metadata: VideoMetadata | None

    def __init__(self, time_display_mode: TimeDisplayMode = TimeDisplayMode.YOUTUBE, _should_refresh: bool = True) -> None:
        super().__init__()
        self.time_display_mode = time_display_mode
        self._frame = 0
        self._should_refresh = _should_refresh

        self.styles.height = 1
        self.styles.width = 'auto'

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, v: int):
        self._frame = v
        if self._should_refresh:
            self.refresh(recompose=True)

    def get_content_width(self, _: Size, __: Size) -> int:
        assert self.metadata != None, 'provide metadata before get content width'
        return self.metadata.size.width

    def compose(self):
        assert self.metadata != None, 'metadata should be set before compose'
        yield Static(format_time(self.time_display_mode, self._frame, self.metadata.fps, self.metadata.duration))