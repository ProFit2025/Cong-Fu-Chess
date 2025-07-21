import pathlib
from app.Graphics import Graphics
from app.Board import Board

class GraphicsFactory:

    def load(self,
             sprites_dir: pathlib.Path,
             cfg: dict,
             cell_size: tuple[int, int]) -> Graphics:
        """Load graphics from sprites directory with configuration."""
        
        loop = cfg.get("is_loop", True)
        fps = cfg.get("frames_per_sec", 6.0)
        return Graphics(
            sprites_folder=sprites_dir,
            cell_size=cell_size,
            loop=loop,
            fps=fps
        )