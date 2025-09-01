# textual-video

Textual widget for playing videos in terminal UIs. Based on [textual-image](https://github.com/lnqs/textual-image).

## Installation
> PyPI release soon. Now just clone repo.

### Dependencies
 - Textual
 - Textual-image
 > NOTE: use [patched fork](https://github.com/firedotguy/textual-image/tree/fix-no-screen-error) of `textual-image` to avoid `NoScreen` errors.

 - av
 - numpy

## Usage
```python
from textual_video.player import VideoPlayer
from textual.app import App, ComposeResult

class ExampleApp(App):
    def compose(self) -> ComposeResult:
        yield VideoPlayer(r'examples\video.mp4'),

if __name__ == '__main__':
    ExampleApp().run()
```
### Parameters
| Name                  |             Type | Description                                                 |
| --------------------- | ---------------- | ----------------------------------------------------------- |
| `path`                |            `str` | Path to the video file                                      |
| `image_type`          |      `ImageType` | Rendering backend (e.g. `ImageType.SIXEL`)                  |
| `speed`               |          `float` | Playback speed multiplier (1.0 = normal)                    |
| `update_strategy`     | `UpdateStrategy` | How frames are updated (`REPLACE_WIDGET` or `UPDATE_IMAGE`) |
| `fps_decrease_factor` |            `int` | Downsample FPS by this factor to reduce CPU/rendering load  |

### Enums
#### ImageType
Image rendering type
| Member               | Description                                                                             |
| -------------------- | --------------------------------------------------------------------------------------- |
| `ImageType.SIXEL`    | Highest fidelity; requires terminal sixel support; best for `SET_IMAGE`.                |
| `ImageType.TGP`      | Mid-quality option (depends on implementation).                                         |
| `ImageType.HALFCELL` | Fast; uses half-cell Unicode blocks.                                                    |
| `ImageType.UNICODE`  | Fastest; low fidelity, widest compatibility.                                            |
#### UpdateStrategy
Image updating strategy
| Member                     | Description                                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| `UpdateStrategy.REMOUNT`   | Create/mount a new widget for each frame and remove the old. Simple but slow and can flicker.   |
| `UpdateStrategy.REACTIVE`  | Update a reactive field on the player and call `refresh(recompose=True)`. Medium cost.          |
| `UpdateStrategy.SET_IMAGE` | Keep one mounted widget and call `image` setter. Supports only `ImageType.SIXEL`                |

## Contributing
 - Please open issues for bugs or feature requests.
 - Create a PR against main and mention related issues.