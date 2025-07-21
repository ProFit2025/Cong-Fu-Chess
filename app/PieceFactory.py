import pathlib
from typing import Tuple
import json
from app.Board import Board
from app.GraphicsFactory import GraphicsFactory
from app.Moves import Moves
from app.PhysicsFactory import PhysicsFactory
from app.Piece import Piece
from app.State import State


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        """Initialize piece factory with board and 
        generates the library of piece templates from the pieces directory."""
        self.board = board
        self.pieces_root = pathlib.Path(pieces_root)
        self.graphics_factory = GraphicsFactory()
        self.physics_factory = PhysicsFactory(board)

    def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
        """Build a state machine for a piece from its directory."""
        states_dir = piece_dir / "states"

        # Load the "idle" state configuration
        idle_state_dir = states_dir / "idle"
        if not idle_state_dir.is_dir():
            raise ValueError(f"No 'idle' state directory found in {states_dir}")

        cfg_path = idle_state_dir / "config.json"
        if not cfg_path.exists():
            raise ValueError(f"No 'config.json' found in {idle_state_dir}")

        # Load state configuration
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        # Load moves
        moves_path = piece_dir / "moves.txt"
        moves = Moves(moves_path, (self.board.H_cells, self.board.W_cells))

        # Load graphics
        sprites_dir = idle_state_dir / "sprites"
        graphics_cfg = cfg.get("graphics", {})
        cell_size = (self.board.cell_W_pix, self.board.cell_H_pix)
        graphics = self.graphics_factory.load(
            sprites_dir=sprites_dir,
            cfg=graphics_cfg,
            cell_size=cell_size
        )

        # Load physics
        physics_cfg = cfg.get("physics", {})
        start_cell = (0, 0)  # Placeholder, will be set in create_piece
        physics = self.physics_factory.create(start_cell, physics_cfg)

        # Create and return the "idle" state
        return State(moves, graphics, physics)

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """Create a piece of the specified type at the given cell."""
        # Get the piece directory
        piece_dir = self.pieces_root / p_type
        if not piece_dir.is_dir():
            raise ValueError(f"Piece directory not found for type {p_type}")

        # Build the state machine (idle state)
        idle_state = self._build_state_machine(piece_dir)

        # Update physics starting position
        idle_state.physics.cell = cell
        idle_state.physics.pixel_pos = idle_state.physics._cell_to_pixel(cell)
        idle_state.physics.target_cell = cell
        idle_state.physics.target_pixel = idle_state.physics.pixel_pos

        # Create and return the piece
        return Piece(piece_id=p_type, init_state=idle_state)
