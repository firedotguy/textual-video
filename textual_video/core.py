from subprocess import run
from json import loads
from tempfile import TemporaryDirectory
from pathlib import Path
from PIL import Image

from .metadata import VideoMetadata
from .enums import ImageType
from .utils import image_type_to_widget, IMAGES_WIDGET_TYPE


def _frame_to_pil(frame_path: str) -> Image.Image:
    """Load frame from file as PIL.Image (RGB)."""
    return Image.open(frame_path).convert("RGB")


def frames_from_video_ffmpeg(
    video_path: str | Path,
    resize: tuple[int, int] | None = None
) -> list[Image.Image]:
    """
    Read frames from video using ffmpeg and return list of PIL.Image.

    Args:
      video_path: path to video file
      resize: resize each frame
    """
    video_path = str(video_path)

    with TemporaryDirectory() as tmpdir:
        output_pattern = str(Path(tmpdir) / "frame_%06d.png")

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-start_number", "0",
            output_pattern,
            "-y",
            "-hide_banner",
            "-loglevel", "error"
        ]

        run(cmd, check=True, capture_output=True)

        result: list[Image.Image] = []
        frame_files = sorted(Path(tmpdir).glob("frame_*.png"))

        for frame_file in frame_files:
            pil = _frame_to_pil(str(frame_file))
            if resize:
                pil = pil.resize(resize, Image.Resampling.LANCZOS)
            result.append(pil)

        return result


def pil_list_to_widgets(pil_list: list[Image.Image], type: ImageType, **kwargs) -> list[IMAGES_WIDGET_TYPE]:
    """Convert list of PIL.Images into list of Image instances."""
    images: list = []
    for pil in pil_list:
        img = image_type_to_widget(type)(pil, **kwargs)
        images.append(img)
    return images


def get_video_metadata(video_path: str | Path) -> VideoMetadata:
    """Get video metadata using ffprobe.

    Args:
        video_path (str | Path): Video path.

    Returns:
        VideoMetadata: Metadata
    """
    video_path = str(video_path)

    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ]

    result = run(cmd, capture_output=True, text=True, check=True)
    data = loads(result.stdout)

    video_stream = None
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            video_stream = stream
            break

    if not video_stream:
        raise ValueError(f"No video stream found in {video_path}")

    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))

    r_frame_rate = video_stream.get("r_frame_rate", "0/1")
    if "/" in r_frame_rate:
        num, den = map(int, r_frame_rate.split("/"))
        fps = num / den if den > 0 else 0.0
    else:
        fps = float(r_frame_rate)

    format_info = data.get("format", {})
    duration = float(format_info.get("duration", 0) or 0)

    frame_count = int(video_stream.get("nb_frames", 0) or 0)

    if frame_count == 0 and duration > 0 and fps > 0:
        frame_count = int(duration * fps)

    return VideoMetadata(fps, duration, frame_count, width, height)


def video_to_widgets(
    video_path: str | Path,
    type: ImageType = ImageType.SIXEL,
    resize: tuple[int, int] | None = None,
    **kwargs
) -> list[IMAGES_WIDGET_TYPE]:
    """Convert video to image widgets using ffmpeg.

    Args:
        video_path (str | Path): Video path
        type (ImageType, optional): Image rendering type. Defaults to ImageType.SIXEL.
        resize (tuple[int, int] | None, optional): Resizing. Defaults to None.
        kwargs (dict | None, optional): Keyword arguments for Image widgets. Defaults to None.

    Returns:
        list[IMAGES_WIDGET_TYPE]: Image widgets
    """
    pil_frames = frames_from_video_ffmpeg(
        video_path,
        resize=resize,
    )
    return pil_list_to_widgets(pil_frames, type, **kwargs)
