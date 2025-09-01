from textual_image.widget import SixelImage, UnicodeImage, TGPImage, HalfcellImage
from .enums import ImageType

#Textual-image widget types
IMAGES_WIDGET_TYPE = SixelImage | UnicodeImage | TGPImage | HalfcellImage

#Map of render delays for image types
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