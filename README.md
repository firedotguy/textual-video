# textual-video

Textual widget for playing videos in terminal UIs. Based on [textual-image](https://github.com/lnqs/textual-image).

<!-- > [!WARNING]
> This project is freezed/archived due i have no time. Maybe will continue work in summer. -->

## Installation
```bash
pip install textual-video
```

### Dependencies
 - textual
 - textual-image
 - av
 - numpy

## Example
```python
from textual_video.player import VideoPlayer
from textual.app import App, ComposeResult

class ExampleApp(App):
    def compose(self) -> ComposeResult:
        yield VideoPlayer(r'examples\video.mp4')

if __name__ == '__main__':
    ExampleApp().run()
```

### Image types
Textual-image provides 4 ways to display image
| Member               | Description                                                                             |
| -------------------- | --------------------------------------------------------------------------------------- |
| `ImageType.SIXEL`    | Slow; Highest fidelity; requires terminal sixel support.                                |
| `ImageType.TGP`      | ? (not work in my laptop)                                                               |
| `ImageType.HALFCELL` | Fast; uses half-cell Unicode blocks.                                                    |
| `ImageType.UNICODE`  | Fastest; low fidelity, widest compatibility.                                            |


## Contributing
 - Please open issues for bugs or feature requests.
 - Create a PR against main and mention related issues.
