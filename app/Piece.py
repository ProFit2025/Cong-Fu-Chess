from app.Board import Board
from app.Command import Command
from app.State import State


class Piece:
    def __init__(self, piece_id: str, init_state: State):
        """Initialize a piece with an ID and initial state."""
        self.piece_id = piece_id
        self.current_state = init_state
        self.start_time = 0

    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        
        # Get the next state based on the command
        next_state = self.current_state.get_state_after_command(cmd, now_ms)
        
        # Update to the new state if it's different
        if next_state != self.current_state:
            self.current_state = next_state
        
        # Reset the current state with the new command
        self.current_state.reset(cmd)

    def reset(self, start_ms: int):
        """Reset the piece to its idle state."""
        self.start_time = start_ms
        idle_cmd = Command(timestamp=start_ms, piece_id=self.piece_id, type="Idle", params=[])
        self.current_state.reset(idle_cmd)

    def update(self, now_ms: int):
        """Update the piece state based on the current time."""
        self.current_state = self.current_state.update(now_ms)

    def draw_on_board(self, board: Board, now_ms: int):
        """Draw the piece on the board."""
        # Get the current image and position
        img = self.current_state.graphics.get_img()
        pos_x, pos_y = self.current_state.physics.get_pos()
        
        # Draw on the board
        img.draw_on(board.img, int(pos_x), int(pos_y))
        