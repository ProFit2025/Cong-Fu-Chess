import pathlib
from app.Graphics import Graphics
from app.Board import Board
import numpy as np

class GraphicsFactory:

    def load(self,
             sprites_dir: pathlib.Path,
             cfg: dict,
             cell_size: tuple[int, int]) -> Graphics:
        """Load graphics from sprites directory with configuration."""
        
        loop = cfg.get("is_loop", True)
        fps = cfg.get("frames_per_sec", 6.0)
        gfx = Graphics(
            sprites_folder=sprites_dir,
            cell_size=cell_size,
            loop=loop,
            fps=fps
        )
        # Ensure that all frames have valid dimensions and valid channel count.
        valid_frames = [
            frm for frm in gfx.frames 
            if frm.img is not None 
            and frm.img.size > 0 
            and len(frm.img.shape) == 3 
            and frm.img.shape[2] > 0
        ]
        if not valid_frames:
            raise ValueError(f"No valid sprite frames found in {sprites_dir}")
        gfx.frames = valid_frames
        gfx.img = gfx.frames[0]
        return gfx