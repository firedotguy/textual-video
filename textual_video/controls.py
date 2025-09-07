from textual.containers import Horizontal
from textual.geometry import Size
from textual.widgets import Static
from .enums import TimeDisplayMode
from .utils import format_time
from .metadata import VideoMetadata

class PlayerControls(Horizontal):
    """Base PlayerControls widget."""
    metadata: VideoMetadata | None

    def __init__(self, time_display_mode: TimeDisplayMode = TimeDisplayMode.YOUTUBE, _should_refresh: bool = True) -> None:
        """Cretae new PlayerControls.

        Args:
            time_display_mode (TimeDisplayMode, optional): Time displaying mode. Defaults to TimeDisplayMode.YOUTUBE.
            _should_refresh (bool, optional): Should refresh widget after update frame. Set to False if you are using UpdateStrategy.REACTIVE. Defaults to True.
        """
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

    def get_content_width(self, container: Size, viewport: Size) -> int:
        assert self.metadata != None, 'provide metadata before get content width'
        return self.metadata.size.width

    def compose(self):
        assert self.metadata != None, 'metadata should be set before compose'
        yield Static(format_time(self.time_display_mode, self._frame, self.metadata.fps, self.metadata.duration))