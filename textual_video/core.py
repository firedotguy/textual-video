from pathlib import Path
from PIL import Image
import av

from .metadata import VideoMetadata
from .enums import ImageType
from .utils import image_type_to_widget, IMAGES_WIDGET_TYPE

def _frame_to_pil(frame) -> Image.Image:
    """Convert PyAV VideoFrame -> PIL.Image (RGB)."""
    arr = frame.to_ndarray(format="rgb24")  # H, W, 3 (RGB)
    return Image.fromarray(arr)


def frames_from_video_pyav(
    video_path: str | Path,
    resize: tuple[int, int] | None = None,
    start_sec: float = 0.0,
) -> list[Image.Image]:
    """
    Read frames from video using PyAV and return list of PIL.Image.

    Args:
      video_path: path to video file
      resize: optional (width, height) to resize each frame (PIL)
      start_sec: skip frames before this second (best-effort)

    Notes:
      - Sampling by target_fps is implemented by skipping frames according to
        source average rate (stream.average_rate). It's an approximation.
    """
    container = av.open(str(video_path))
    try:
        vs = container.streams.video[0]

        src_fps = float(vs.average_rate) if vs.average_rate is not None else 15
        start_frame_idx = int(start_sec * src_fps) if (start_sec and src_fps) else 0

        result: list[Image.Image] = []
        decoded_idx = 0  # index of decoded frames for the stream

        for frame in container.decode(0):
            decoded_idx += 1
            if decoded_idx < start_frame_idx:
                continue

            pil = _frame_to_pil(frame)
            if resize:
                pil = pil.resize(resize, Image.Resampling.LANCZOS)
            result.append(pil)

        return result
    finally:
        container.close()


def pil_list_to_widgets(pil_list: list[Image.Image], type: ImageType, kwargs: dict = {}) -> list[IMAGES_WIDGET_TYPE]:
    """Convert list of PIL.Images into list of Image instances."""
    images: list = []
    for pil in pil_list:
        img = image_type_to_widget(type)(pil, **kwargs)
        images.append(img)
    return images


def get_video_metadata(video_path: str | Path) -> VideoMetadata:
    """Get video metedata.

    Args:
        video_path (str | Path): Video path.

    Returns:
        VideoMetadata: Metadata
    """
    container = av.open(str(video_path))
    try:
        vs = container.streams.video[0]

        # Duration in seconds (may be 0 if not available)
        duration = float((vs.duration or 0) * (vs.time_base or 0)) if vs.time_base is not None else 0.0
        frame_count = int(vs.frames or 0)

        # Prefer stream.average_rate; fall back to frame_count / duration when possible.
        if vs.average_rate:
            fps = float(vs.average_rate)
        elif duration > 0 and frame_count > 0:
            fps = frame_count / duration
        else:
            fps = 0.0

        return VideoMetadata(fps, duration, frame_count, vs.width, vs.height)
    finally:
        container.close()


def video_to_widgets(
    video_path: str | Path,
    type: ImageType = ImageType.SIXEL,
    resize: tuple[int, int] | None = None,
    start_sec: float = 0.0,
    kwargs: dict = {},
) -> list[IMAGES_WIDGET_TYPE]:
    """Convert video to image widgets.

    Args:
        video_path (str | Path): Video path
        type (ImageType, optional): Image rendering type. Defaults to ImageType.SIXEL.
        resize (tuple[int, int] | None, optional): Resizing. Defaults to None.
        start_sec (float, optional): Start. Defaults to 0.0.
        kwargs (dict | None, optional): Keyword arguments for Image widgets. Defaults to None.

    Returns:
        list[IMAGES_WIDGET_TYPE]: Image widgets
    """
    pil_frames = frames_from_video_pyav(
        video_path,
        resize=resize,
        start_sec=start_sec,
    )
    return pil_list_to_widgets(pil_frames, type, kwargs=kwargs)
