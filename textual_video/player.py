from pathlib import Path
from typing import Callable, Any

from textual.app import ComposeResult
from textual.color import Color
from textual.events import Mount
from textual.message import Message
from textual.widget import Widget
from textual.containers import Container, Horizontal
from textual.widgets import Static
from textual.binding import Binding
from textual.reactive import reactive
from textual_canvas import Canvas

from .core import get_video_metadata, video_to_widgets
from .utils import (
    pil_to_textual_sizes,
    get_render_delay,
    format_time,
    icon_type_to_text,
)
from .enums import ImageType, TimeDisplayMode, IconType


class PauseButton(Static):
    """Play/pause button"""
    class Pressed(Message):
        """Button pressed message"""
        pass

    class Entered(Message):
        """Mouse entered button message"""
        pass

    class Leaved(Message):
        """Mouse leaved button message"""
        pass

    def __init__(self, content: str):
        """Create new pause button

        Args:
            content (str): content
        """
        super().__init__(content, id='pause_button', classes='controls__pause_button')
        self.styles.height = 1
        self.styles.max_height = 1
        self.styles.width = 3
        self._temp_pause = False

    def on_click(self) -> None:
        self._temp_pause = False
        self.post_message(self.Pressed())

    def on_enter(self) -> None:
        self._temp_pause = True
        self.post_message(self.Entered())

    def on_leave(self) -> None:
        if self._temp_pause:
            self.post_message(self.Leaved())
            self._temp_pause = False


class VideoPlayer(Widget):
    """Base VideoPlayer widget with embedded controls."""

    frame = reactive(None)
    paused = reactive(False)
    BINDINGS = [Binding('space', 'toggle_pause')]
    can_focus = True

    DEFAULT_CSS = '''
    Image {
        width: 100%;
        height: 100%;
    }
    Canvas {
        width: 100%;
        height: 1;
        background: transparent;
    }
    .player__frame {
        width: 100%;
    }
    .player__controls {
        height: 1;
        width: 100%;
    }
    '''

    def __init__(
        self,
        path: str | Path,
        time_display_mode: TimeDisplayMode = TimeDisplayMode.YOUTUBE,
        pause_icon_type: IconType = IconType.UNICODE,
        image_type: ImageType = ImageType.SIXEL,
        speed: float = 1,
        on_update: Callable[[int], Any] = lambda frame: None,
        render_delay: float | None = None,
        fps_decrease_factor: int = 1,
    ):
        """Create new VideoPlayer.

        Args:
            path (str | Path): Path to video.
            time_display_mode (TimeDisplayMode, optional): How to format the control time. Defaults to TimeDisplayMode.YOUTUBE.
            pause_icon_type (IconType, optional): Icon type for the toggle button. Defaults to IconType.UNICODE.
            image_type (ImageType, optional): Image rendering type. Defaults to ImageType.SIXEL.
            speed (float, optional): Video speed. Defaults to 1.
            on_update (callable, optional): Video update callback. Defaults to None.
            render_delay (float | None, optional): Average time to render an image. Defaults to None.
            fps_decrease_factor (int, optional): FPS decreasing factor. Defaults to 1.
        """
        super().__init__()
        path = Path(path)
        assert path.exists(), f'Video {path} is not exists.'
        assert render_delay is None or render_delay >= 0, 'Render delay should be greater than 0.'

        self.video_path = path
        self.current_frame_index = 0
        self.frames = []
        self.image_type = image_type
        self.speed = speed
        self.on_frame_update = on_update
        self.fps_decrease_factor = fps_decrease_factor
        self.render_delay = render_delay or get_render_delay(image_type)
        self.time_display_mode = time_display_mode
        self.pause_icon_type = pause_icon_type
        self._pause_button: PauseButton | None = None
        self._time_display: Static | None = None

        self.metadata = get_video_metadata(self.video_path)
        self.paused = False
        self._fake_paused = False

        frame_width, frame_height = pil_to_textual_sizes(self.metadata.size.width, self.metadata.size.height)
        self.styles.width = frame_width
        self._frame_height = frame_height
        self.styles.height = frame_height + 2

    def on_mount(self, event: Mount) -> None:
        self.frames = video_to_widgets(self.video_path, type=self.image_type)
        if self.fps_decrease_factor > 1:
            self.frames = self.metadata.decrease_fps(self.fps_decrease_factor, self.frames) or []

        assert self.metadata.delay_between_frames / self.speed - self.render_delay > 0, (
            f'Render delay should be less than {self.metadata.delay_between_frames / self.speed}.'
        )
        self.timer = self.set_interval(
            self.metadata.delay_between_frames / self.speed - self.render_delay,
            self._update_frame_index
        )
        self._pause_button = self.query_one('#pause_button', PauseButton)
        self._time_display = self.query_one('#time_display', Static)
        self._update_controls()
        self._replace_frame_widget(0)


    def _update_frame_index(self):
        if self.metadata.frame_count > self.current_frame_index + 1:
            self.current_frame_index += 1
            self._replace_frame_widget(self.current_frame_index)
        else:
            self.pause()

    def _refresh_image(self) -> Container | None:
        self.refresh(recompose=True)

    def _replace_frame_widget(self, idx: int) -> None:
        self._refresh_image()
        self.on_frame_update(self.current_frame_index)
        self.frame = self.frames[idx]
        self._update_controls()

    def _update_controls(self) -> None:
        if not self.metadata:
            return
        if self._pause_button:
            self._pause_button.content = icon_type_to_text(self.pause_icon_type, self.paused)
            self._pause_button.refresh()

        if self._time_display:
            self._time_display.update(
                format_time(
                    self.time_display_mode,
                    self.current_frame_index,
                    self.metadata.fps,
                    self.metadata.duration
                )
            )

    def play(self) -> None:
        """Play/resume video"""
        if self.current_frame_index == self.metadata.frame_count - 1:
            self.current_frame_index = 0 # start from the beginning
        self.timer.resume()
        self.paused = False
        self._refresh_image()
        self._update_controls()

    def pause(self) -> None:
        """Pause video"""
        self.timer.pause()
        self.paused = True
        self._refresh_image()
        self._update_controls()

    def action_toggle_pause(self) -> None:
        """Toggle pause"""
        self._fake_paused = False
        if self.paused:
            self.play()
        else:
            self.pause()

    def _fake_pause(self) -> None:
        """Fake pause - only stop timer, keep UI showing play state"""
        self.timer.pause()
        self._fake_paused = True

    def _fake_resume(self) -> None:
        """Resume from fake pause"""
        if self._fake_paused:
            self.timer.resume()
            self._fake_paused = False

    def on_pause_button_pressed(self, event: PauseButton.Pressed) -> None:
        self.action_toggle_pause()
        event.stop()

    def on_pause_button_entered(self, event: PauseButton.Entered) -> None:
        if not self.paused:
            self._fake_pause()
        event.stop()

    def on_pause_button_leaved(self, event: PauseButton.Leaved) -> None:
        if self._fake_paused:
            self._fake_resume()
        event.stop()



    def compose(self) -> ComposeResult:
        frame_height = self._frame_height

        frame_container = Container(self.frame or Static('loading'), classes='player__frame')
        frame_container.styles.height = frame_height
        yield frame_container
        canvas = Canvas(self.size.width, 2)
        canvas.draw_line(0, 0, self.size.width * self.current_frame_index // len(self.frames or [0]), 0, Color.parse('red'))
        yield canvas


        with Horizontal(classes='player__controls'):
            yield PauseButton(icon_type_to_text(self.pause_icon_type, self.paused))

            yield Static(
                format_time(
                    self.time_display_mode,
                    self.current_frame_index,
                    self.metadata.fps,
                    self.metadata.duration,
                ),
                classes='controls__time',
                id='time_display'
            )
