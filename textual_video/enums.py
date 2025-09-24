from enum import Enum

class ImageType(Enum):
    """Image rendering type.
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
    """Update image startegy.
     - remount: remove_children + mount - slow
     - reactive: update reactive field + refresh with recomposing - mid
     - set_image use textual-image image setter - mid (NOTE: supports only SIXEL ImageType)
    """
    REMOUNT = 'remount'
    REACTIVE = 'reactive'
    SET_IMAGE = 'set_image'

class TimeDisplayMode(Enum):
    """Time displaying mode.
     - youtube: youtube-like displaying (0:03/1:41:03)
     - seconds: display seconds (3/6060)
     - milliseconds: display milliseconds (180/363600), may wrong because frame update slower than millisecond
     - frame_index: display frame_index (81/163120)
     - hidden: do not display time
    """
    YOUTUBE = 'youtube'
    SECONDS = 'seconds'
    MILLISECONDS = 'milliseconds'
    FRAME_INDEX = 'frame-index'
    HIDDEN = 'hidden'

class IconType(Enum):
    """Player controls icon type.
    """
    NERD = 'nerd'
    ASCII = 'ascii'
    EMOJI = 'emoji'
    UNICODE = 'unicode'