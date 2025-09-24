from pathlib import Path
from time import time
from typing import Callable, Any

from textual.app import ComposeResult
from textual.events import Mount
from textual.widget import Widget
from textual.containers import Container
from textual.widgets import Static
from textual_image.widget import SixelImage
from textual.binding import Binding
from textual.reactive import reactive
from textual import log

from .core import get_video_metadata, video_to_widgets
from .utils import textual_to_pil_sizes, pil_to_textual_sizes, image_type_to_widget, get_render_delay
from .enums import ImageType, UpdateStrategy
from .controls import PlayerControls


class VideoPlayer(Widget):
    """Base VideoPlayer widget."""
    frame = reactive(None)
    paused = reactive(False)
    BINDINGS = [Binding('space', 'toggle_pause')]
    can_focus = True

    def __init__(
        self,
        path: str | Path,
        controls: PlayerControls = PlayerControls(),
        image_type: ImageType = ImageType.SIXEL,
        speed: float = 1,
        on_update: Callable[[int], Any] = lambda frame: None,
        update_strategy: UpdateStrategy = UpdateStrategy.REACTIVE,
        render_delay: float | None = None,
        fps_decrease_factor: int = 1
    ):
        """Create new VideoPlayer.

        Args:
            path (str | Path): Path to video.
            controls (PlayerControls, optional): Player controls. Defaults to PlayerControls().
            image_type (ImageType, optional): Image rendering type. Defaults to ImageType.SIXEL.
            speed (float, optional): Video speed. Defaults to 1.
            on_update (_type_, optional): Video update callback. Defaults to None.
            update_strategy (UpdateStrategy, optional): Image update strategy. Defaults to UpdateStrategy.REACTIVE.
            render_delay (float | None, optional): Average time to render an image. Defaults to None.
            fps_decrease_factor (int, optional): FPS decreasing factor. Defaults to 1.
        """
        super().__init__()
        path = Path(path)
        assert path.exists(), f'Video {path} is not exists.'
        assert render_delay == None or render_delay >= 0, 'Render delay should be greater than 0.'

        self.video_path = path
        self.controls = controls
        if update_strategy == UpdateStrategy.REACTIVE: self.controls._should_refresh = False
        self.current_frame_index = 0
        self.image_type = image_type
        self.speed = speed
        self.on_frame_update = on_update
        self.update_strategy = update_strategy
        self.fps_descrease_factor = fps_decrease_factor
        self.render_delay = render_delay or get_render_delay(image_type)

        self.metadata = get_video_metadata(self.video_path)
        self.controls.metadata = self.metadata
        self._start = time()
        self.paused = False

        self.styles.width = pil_to_textual_sizes(self.metadata.size.width, self.metadata.size.height)[0]
        self.styles.height = pil_to_textual_sizes(self.metadata.size.width, self.metadata.size.height)[1] + 1 # space for controls

    def on_mount(self, event: Mount) -> None:
        self.frames = video_to_widgets(self.video_path, type=self.image_type)
        if self.fps_descrease_factor > 1:
            self.frames = self.metadata.decrease_fps(self.fps_descrease_factor, self.frames) or []

        assert self.metadata.delay_between_frames / self.speed - self.render_delay > 0, \
            f'Render delay should be less than {self.metadata.delay_between_frames / self.speed}.'
        self.timer = self.set_interval(self.metadata.delay_between_frames / self.speed - self.render_delay, self._update_frame_index)
        self._replace_frame_widget(0)

    def _update_frame_index(self):
        if self.metadata.frame_count > self.current_frame_index + 1:
            self.current_frame_index += 1
            self.controls.frame = self.current_frame_index
            self._replace_frame_widget(self.current_frame_index)
        else:
            self.pause()

    def _refresh_image(self) -> Container | None:
        if self.update_strategy == UpdateStrategy.REACTIVE:
            self.refresh(recompose=True)
        elif self.update_strategy == UpdateStrategy.REMOUNT:
            container = self.query_one(Container)
            container.remove_children()
            return container

    def _replace_frame_widget(self, idx: int) -> None:
        self.on_frame_update(self.current_frame_index)
        container = self._refresh_image()
        if self.update_strategy == UpdateStrategy.REACTIVE:
            self.frame = self.frames[idx]
        elif self.update_strategy == UpdateStrategy.REMOUNT:
            assert container is not None
            container.mount(self.frames[idx])
        else:
            image = self.query_one(SixelImage)
            image.image = self.frames[idx].image

    def play(self) -> None:
        """Play/resume video."""
        if self.current_frame_index == self.metadata.frame_count - 1:
            self.current_frame_index = 0 # start from the beginning
        self.timer.resume()
        self.controls.paused = False
        self.paused = False
        self._refresh_image()

    def pause(self) -> None:
        """Pause/stop video."""
        self.timer.pause()
        self.controls.paused = True
        self.paused = True
        self._refresh_image()

    def action_toggle_pause(self) -> None:
        if self.paused: self.play()
        else: self.pause()

    def compose(self) -> ComposeResult:
        if self.update_strategy == UpdateStrategy.REACTIVE:
            yield Container(self.frame or Static('loading'))
        elif self.update_strategy == UpdateStrategy.REMOUNT:
            yield Container()
        else:
            yield image_type_to_widget(self.image_type)()
        yield self.controls
