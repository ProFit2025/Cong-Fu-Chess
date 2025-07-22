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
        self.counter = {}  # Added: counter per piece type

    def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
        """Build a state machine for a piece from its directory."""
        state_types = ["move", "jump", "idle", "long_rest", "short_rest"]
        states_dir = piece_dir / "states"
        init_states = {}
        
        # Create every state
        for state in state_types:
            state_dir = states_dir / state
            if not state_dir.is_dir():
                raise ValueError(f"No {state} state directory found in {states_dir}")

            cfg_path = state_dir / "config.json"
            if not cfg_path.exists():
                raise ValueError(f"No 'config.json' found in {state_dir}")

            # Load state configuration
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            # Load moves (shared for all states)
            moves_path = piece_dir / "moves.txt"
            moves = Moves(moves_path, (self.board.H_cells, self.board.W_cells))

            # Load graphics – if loading the "move" state and its sprites folder is empty, fallback to "idle"
            sprites_dir = state_dir / "sprites"
            if state == "move":
                png_files = list(sprites_dir.glob("*.png"))
                if not png_files:  # no PNG files in move state folder
                    # Fallback to idle state's sprites folder
                    fallback_dir = (states_dir / "idle") / "sprites"
                    print(f"[WARN] No sprites in {sprites_dir}; falling back to {fallback_dir} for state '{state}'.")
                    sprites_dir = fallback_dir

            graphics_cfg = cfg.get("graphics", {})
            cell_size = (self.board.cell_W_pix, self.board.cell_H_pix)
            graphics = self.graphics_factory.load(
                sprites_dir=sprites_dir,
                cfg=graphics_cfg,
                cell_size=cell_size
            )

            # Load physics
            physics_cfg = cfg.get("physics", {})
            physics_cfg['type'] = state
            start_cell = (0, 0)  # Placeholder; will be set in create_piece
            physics = self.physics_factory.create(start_cell, physics_cfg)
            init_states[state] = State(moves, graphics, physics)
        
        idle_state = init_states["idle"]
        move_state = init_states["move"]
        jump_state = init_states["jump"]
        long_rest_state = init_states["long_rest"]
        short_rest_state = init_states["short_rest"]
        
        # State transitions:
        idle_state.set_transition("Move", move_state)
        idle_state.set_transition("Jump", jump_state)
        jump_state.set_transition("ShortRest", short_rest_state)
        move_state.set_transition("LongRest", long_rest_state)
        long_rest_state.set_transition("Idle", idle_state)
        short_rest_state.set_transition("Idle", idle_state)
        return idle_state

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """Create a piece of the specified type at the given cell."""
        # Get the piece directory
        piece_dir = self.pieces_root / p_type
        if not piece_dir.is_dir():
            raise ValueError(f"Piece directory not found for type {p_type}")

        # Build the state machine (idle state)
        idle_state = self._build_state_machine(piece_dir)

        # Set starting position for physics
        idle_state.physics.cell = cell
        idle_state.physics.pixel_pos = idle_state.physics._cell_to_pixel(cell)
        idle_state.physics.target_cell = cell
        idle_state.physics.target_pixel = idle_state.physics.pixel_pos

        # Generate a unique id for the piece.
        if p_type not in self.counter:
            self.counter[p_type] = 0
        self.counter[p_type] += 1
        unique_id = f"{p_type}_{self.counter[p_type]}"

        # Create and return the piece with the unique id.
        return Piece(piece_id=unique_id, init_state=idle_state)
