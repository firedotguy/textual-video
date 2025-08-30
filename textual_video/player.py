from pathlib import Path

from textual.app import ComposeResult
from textual.events import Mount
from textual.geometry import Size
from textual.widget import Widget
from textual.containers import Container
from textual.widgets import Static
from textual_image.widget import SixelImage
from textual import log
from textual.reactive import reactive

from .core import get_video_metadata, video_to_sixel
from .utils import textual_to_pil_sizes, pil_to_textual_sizes
from .enums import ImageType, UpdateStrategy


class VideoPlayer(Widget):
    frame = reactive(None)
    def __init__(
        self,
        path: str | Path,
        image_type: ImageType = ImageType.SIXEL,
        speed: float = 1,
        update_strategy: UpdateStrategy = UpdateStrategy.REACTIVE,
        fps_decrease_factor: int = 1
    ):
        super().__init__()
        self.video_path = path
        self.current_frame_index = 0
        self.image_type = image_type
        self.speed = speed
        self.update_strategy = update_strategy
        self.fps_descrease_factor = fps_decrease_factor
        self.metadata = get_video_metadata(self.video_path)

        self.styles.width, self.styles.height = pil_to_textual_sizes(self.metadata.size.width, self.metadata.size.height)

    def on_mount(self, event: Mount) -> None:
        self.metadata.fps = 1
        self.frames = video_to_sixel(self.video_path, type=self.image_type)
        if self.fps_descrease_factor > 1:
            self.frames = self.metadata.decrease_fps(self.fps_descrease_factor, self.frames) or []

        self.set_interval(self.metadata.delay_between_frames / self.speed, self.update_frame_index)
        self._replace_frame_widget(0)

    def update_frame_index(self):
        if self.metadata.frame_count > self.current_frame_index + 1:
            self.current_frame_index += 1
            self._replace_frame_widget(self.current_frame_index)

    def _replace_frame_widget(self, idx: int) -> None:
        if self.update_strategy == UpdateStrategy.REACTIVE:
            self.frame = self.frames[idx]
            self.refresh(recompose=True)
        elif self.update_strategy == UpdateStrategy.REMOUNT:
            container = self.query_one(Container)
            container.remove_children()
            container.mount(self.frames[idx])
        else:
            image = self.query_one(SixelImage)
            image.image = self.frames[idx].image

    def compose(self) -> ComposeResult:
        if self.update_strategy == UpdateStrategy.REACTIVE:
            yield Container(self.frame or Static('loading'))
        elif self.update_strategy == UpdateStrategy.REMOUNT:
            yield Container()
        else:
            yield SixelImage()
