from enum import Enum

class ImageType(Enum):
    """Image rendering type
     - sixel (slow)
     - TGP (mid)
     - halfcell (fast)
     - unicode (fastest)
    """
    SIXEL = 'Sixel'
    TGP = 'TGP'
    HALFCELL = 'Halfcell'
    UNICODE = 'Unicode'

class UpdateStrategy(Enum):
    """Update image startegy
     - remount: remove_children + mount - slow
     - reactive: update reactive field + refresh with recomposing - mid
     - set_image use textual-image image setter - mid (NOTE: supports only SIXEL ImageType)
    """
    REMOUNT = 'remount'
    REACTIVE = 'reactive'
    SET_IMAGE = 'set_image'