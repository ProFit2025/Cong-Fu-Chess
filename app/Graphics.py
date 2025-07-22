import pathlib
from typing import Optional
from app.Img import Img
from app.Command import Command

class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 cell_size: tuple[int, int],
                 loop: bool = True,
                 fps: float = 6.0):
        """Initialize graphics with sprites folder, cell size, loop flag, and FPS."""
        self.sprites_folder = sprites_folder
        self.cell_size = cell_size
        self.loop = loop
        self.fps = fps
        self.frames = self._load_frames()
        self.current_frame_idx = 0
        self.last_update_ms = 0
        self.img: Optional[Img] = self.frames[0] if self.frames else None

    def _load_frames(self):
        """Load sprite frames from the folder, sorted alphabetically."""
        frames = []
        if not self.sprites_folder.exists():
            return frames
        for file in sorted(self.sprites_folder.glob("*.png")):
            img = Img().read(file, (self.cell_size[0], self.cell_size[1]))
            frames.append(img)
        return frames

    def copy(self):
        """Create a shallow copy of the Graphics object."""
        new_gfx = Graphics(self.sprites_folder, self.cell_size, self.loop, self.fps)
        new_gfx.frames = self.frames
        new_gfx.current_frame_idx = self.current_frame_idx
        new_gfx.last_update_ms = self.last_update_ms
        new_gfx.img = self.img
        return new_gfx

    def reset(self, cmd: Command):
        """Reset the animation (e.g. on state change)."""
        self.current_frame_idx = 0
        self.last_update_ms = 0
        if self.frames:
            self.img = self.frames[0]

    def update(self, now_ms: int):
        """Advance the animation frame based on game time."""
        if not self.frames or self.fps <= 0:
            return
        if self.last_update_ms == 0:
            self.last_update_ms = now_ms
            return
        elapsed = now_ms - self.last_update_ms
        frame_time = int(1000 / self.fps)
        if elapsed >= frame_time:
            self.current_frame_idx += 1
            if self.current_frame_idx >= len(self.frames):
                self.current_frame_idx = 0 if self.loop else len(self.frames) - 1
            self.img = self.frames[self.current_frame_idx]
            self.last_update_ms = now_ms

    def get_img(self) -> Img:
        """Return the current frame image."""
        return self.img
