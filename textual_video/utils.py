from textual_image.widget import SixelImage, UnicodeImage, TGPImage, HalfcellImage
from textual import log
from .enums import ImageType, TimeDisplayMode

# Textual-image widget types
IMAGES_WIDGET_TYPE = SixelImage | UnicodeImage | TGPImage | HalfcellImage

# Map of render delays for image types (values for Windows PowerShell, can vary in different terminals)
RENDER_DELAY = {
    ImageType.SIXEL: 0.0373,
    ImageType.HALFCELL: 0.01065,
    ImageType.UNICODE: 0.00116,
    ImageType.TGP: 0.00288
}

def textual_to_pil_sizes(width: int, height: int) -> tuple[int, int]:
    """Convert textual sizes to PIL sizes"""
    return width * 10, height * 20

def pil_to_textual_sizes(width: int, height: int) -> tuple[int, int]:
    """Convert PIL sizes to textual sizes"""
    return width // 10, height // 20

def image_type_to_widget(type: ImageType) -> type[IMAGES_WIDGET_TYPE]:
    """Get image widget from its type"""
    match type:
        case ImageType.SIXEL: return SixelImage
        case ImageType.UNICODE: return UnicodeImage
        case ImageType.TGP: return TGPImage
        case ImageType.HALFCELL: return HalfcellImage

def get_render_delay(type: ImageType) -> float:
    """Get render delay for given image type"""
    return RENDER_DELAY[type]

def _pad_left(data: float | int | str) -> str:
    if isinstance(data, (int, float)):
        data = str(int(round(data)))
    else:
        data = str(data)
    return data.zfill(2)

def format_time(mode: TimeDisplayMode, frame: int, fps: float, duration: float) -> str:
    match mode:
        case TimeDisplayMode.HIDDEN:
            return ''
        case TimeDisplayMode.FRAME_INDEX:
            return f'{frame}/{round(duration * fps)}'
        case TimeDisplayMode.SECONDS:
            return f'{frame // fps}/{round(duration)}'
        case TimeDisplayMode.MILLISECONDS:
            return f'{round(frame / fps * 60)}/{round(duration * 60)}'
        case TimeDisplayMode.YOUTUBE:
            seconds = frame / fps
            if seconds < 60:
                left = f'0:{_pad_left(seconds)}'
            elif seconds < 3600:
                left = f'{seconds // 60}:{_pad_left(seconds % 60)}'
            else:
                left = f'{seconds // 3600}:{_pad_left(seconds // 60)}:{_pad_left(seconds % 60)}'

            if duration < 60:
                right = f'0:{_pad_left(duration)}'
            elif duration < 3600:
                right = f'{duration // 60}:{_pad_left(duration % 60)}'
            else:
                right = f'{duration // 3600}:{_pad_left(duration // 60)}:{_pad_left(duration % 60)}'

            return f'{left}/{right}'