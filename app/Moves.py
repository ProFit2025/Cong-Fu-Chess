# Moves.py  – drop-in replacement
import pathlib
from typing import List, Tuple
import re

class Moves:
    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """Initialize moves with rules from text file and board dimensions."""
        self.dims = dims
        self.moves_list = self.read(txt_path)

    def read(self, txt_path: pathlib.Path) -> List[Tuple[int, int]]:
        """Read moves from text file. Each line: 'dx,dy'."""
        moves = []
        with open(txt_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                parts = re.split(r'[,:]', line)
                print(parts)
                if len(parts) >= 2:
                    try:
                        dx = int(parts[0])
                        dy = int(parts[1])
                        moves.append((dx, dy))
                    except ValueError:
                        continue  # skip invalid lines
        return moves

    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Get all possible moves from a given position, filtered by board boundaries."""
        H, W = self.dims
        valid_moves = []
        for dr, dc in self.moves_list:
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W:
                valid_moves.append((nr, nc))
        return valid_moves
    