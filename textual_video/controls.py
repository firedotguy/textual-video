from textual.widget import Widget
from textual.reactive import reactive
from textual.geometry import Size
from textual.widgets import Static
from .enums import TimeDisplayMode
from .utils import format_time
from .metadata import VideoMetadata
from textual import log

class PlayerControls(Widget):
    """Base PlayerControls widget."""
    metadata: VideoMetadata | None
    def __init__(self, time_display_mode: TimeDisplayMode = TimeDisplayMode.YOUTUBE, _should_refresh: bool = True) -> None:
        """Create new PlayerControls.

        Args:
            time_display_mode (TimeDisplayMode, optional): Time displaying mode. Defaults to TimeDisplayMode.YOUTUBE.
            _should_refresh (bool, optional): Should refresh widget after update frame. Set to False if you are using UpdateStrategy.REACTIVE. Defaults to True.
        """
        super().__init__()
        self.time_display_mode = time_display_mode
        self._frame = 0
        self._paused = False
        self._should_refresh = _should_refresh

        self.styles.height = 1
        self.styles.width = 'auto'

    @property
    def frame(self) -> int:
        return self._frame

    @frame.setter
    def frame(self, v: int) -> None:
        self._frame = v
        if self._should_refresh:
            self.refresh(recompose=True)

    @property
    def paused(self) -> bool:
        return self._paused

    @paused.setter
    def paused(self, v: bool) -> None:
        self._paused = v
        if self._should_refresh:
            self.refresh(recompose=True)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        assert self.metadata != None, 'metadata should be set before get content width'
        return self.metadata.size.width

    def compose(self):
        assert self.metadata != None, 'metadata should be set before compose'

        yield Static(
            ('⏸' if not self._paused else '▶') + ' '
            + format_time(self.time_display_mode, self._frame, self.metadata.fps, self.metadata.duration)
        )