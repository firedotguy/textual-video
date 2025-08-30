from textual.geometry import Size

class VideoMetadata:
    """Video metadata class"""
    def __init__(self, fps: float, duration: float, frame_count: int, width: int, height: int):
        self.fps = fps
        self.duration = duration
        self.frame_count = frame_count
        self.size = Size(width, height)
        self.aspect_ratio = width / height
        self.delay_between_frames = 1 / fps

    def decrease_fps(self, factor: int, frames: list | None) -> list | None:
        self.fps /= factor
        self.delay_between_frames = 1 / self.fps
        if frames != None:
            frames = [frames[i] for i in range(0, len(frames), factor)]
            self.frame_count = len(frames)
            return frames