from textual_image.widget import SixelImage, UnicodeImage, TGPImage, HalfcellImage
from .enums import ImageType

IMAGES_WIDGET_TYPE = SixelImage | UnicodeImage | TGPImage | HalfcellImage

def textual_to_pil_sizes(width: int, height: int) -> tuple[int, int]:
    return width * 10, height * 20

def pil_to_textual_sizes(width: int, height: int) -> tuple[int, int]:
    return width // 10, height // 20

def image_type_to_widget(type: ImageType) -> type[IMAGES_WIDGET_TYPE]:
    match type:
        case ImageType.SIXEL: return SixelImage
        case ImageType.UNICODE: return UnicodeImage
        case ImageType.TGP: return TGPImage
        case ImageType.HALFCELL: return HalfcellImage