from dataclasses import dataclass
from app.Img import Img
import cv2
from typing import Tuple

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    cell_H_m: int
    cell_W_m: int
    W_cells: int
    H_cells: int
    img: Img

    # convenience, not required by dataclass
    def clone(self) -> "Board":
        """Clone the board with a copy of the image."""
        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            cell_H_m = self.cell_H_m,
            cell_W_m = self.cell_W_m,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=self.img.clone()  
        )
    
    def draw_cursor(self, pos: Tuple[int, int], color: Tuple[int, int, int], thickness: int = 3):
        """
        Draw a colored rectangle around a cell to show cursor position.
        
        Args:
            pos: (x, y) cell coordinates
            color: (B, G, R) color tuple for OpenCV
            thickness: thickness of the rectangle border
        """
        x, y = pos
        if not (0 <= x < self.W_cells and 0 <= y < self.H_cells):
            return  # Position is out of bounds
            
        # Calculate pixel coordinates
        pixel_x = x * self.cell_W_pix
        pixel_y = y * self.cell_H_pix
        # Draw rectangle around the cell
        cv2.rectangle(
            self.img.img,
            (pixel_y, pixel_x),
            (pixel_y + self.cell_W_pix, pixel_x + self.cell_H_pix),
            color,
            thickness
        )