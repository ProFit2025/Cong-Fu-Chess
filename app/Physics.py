from typing import Tuple, Optional
from app.Command import Command
from app.Board import Board

def notation_to_cell(notation: str) -> Tuple[int, int]:
    """Convert chess notation like 'a1' to (col, row) tuple."""
    col = ord(notation[0]) - ord('a')
    row = int(notation[1:]) - 1
    return (col, row)

class Physics:
    """Base physics class for all piece types."""
    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 1.0):
        self.board = board
        self.cell = start_cell        # logical cell (col, row)
        self.speed_m_s = speed_m_s    # cells per second

    def _cell_to_pixel(self, cell: Tuple[int, int]) -> Tuple[float, float]:
        row, col = cell
        return float(col * self.board.cell_W_pix), float(row * self.board.cell_H_pix)

    def reset(self, cmd: Command):
        raise NotImplementedError("reset() must be implemented in subclass")

    def update(self, now_ms: int):
        raise NotImplementedError("update() must be implemented in subclass")

    def get_pos(self) -> Tuple[float, float]:
        """Pixel position for rendering."""
        if hasattr(self, "pixel_pos"):
            return self.pixel_pos
        return self._cell_to_pixel(self.cell)

    def clone(self) -> "Physics":
        new = self.__class__(self.cell, self.board, self.speed_m_s)
        for attr in ("pixel_pos", "start_pixel", "target_cell", "target_pixel",
                     "start_time", "duration_ms", "moving", "next_state_when_finished"):
            if hasattr(self, attr):
                setattr(new, attr, getattr(self, attr))
        return new

    def can_be_captured(self) -> bool:
        """Default: can be captured."""
        return True

    def can_capture(self) -> bool:
        """Default: cannot capture."""
        return False

class MovePhysics(Physics):
    """Physics for smooth linear move from src to dst."""
    def reset(self, cmd: Command):
        # cmd.params == [from_notation, to_notation]
        src = notation_to_cell(cmd.params[0])
        dst = notation_to_cell(cmd.params[1])
        self.cell = src
        self.start_pixel = self._cell_to_pixel(src)
        self.target_cell = dst
        self.target_pixel = self._cell_to_pixel(dst)
        dx = dst[0] - src[0]
        dy = dst[1] - src[1]
        cell_dist = (dx**2 + dy**2) ** 0.5
        self.duration_ms = (cell_dist / self.speed_m_s) * 1000
        self.start_time = cmd.timestamp or 0
        self.pixel_pos = self.start_pixel
        self.moving = True
        # After move completes, auto-transition to LongRest state.
        self.next_state_when_finished = "LongRest"

    def update(self, now_ms: int):
        if not getattr(self, "moving", False):
            return
        elapsed = now_ms - self.start_time
        if elapsed >= self.duration_ms:
            self.cell = self.target_cell
            self.pixel_pos = self.target_pixel
            self.moving = False
        else:
            t = elapsed / self.duration_ms
            sx, sy = self.start_pixel
            tx, ty = self.target_pixel
            self.pixel_pos = (sx + (tx - sx)*t, sy + (ty - sy)*t)

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return True

class JumpPhysics(Physics):
    """Physics for instant jump (no interpolation)."""
    def reset(self, cmd: Command):
        # cmd.params == [cell_notation]
        dest = notation_to_cell(cmd.params[0])
        self.cell = dest
        self.pixel_pos = self._cell_to_pixel(dest)
        self.moving = False
        # After jump, auto-transition to ShortRest.
        self.next_state_when_finished = "ShortRest"

    def update(self, now_ms: int):
        pass

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return False

class IdlePhysics(Physics):
    """Physics for idle state. The piece remains static."""
    def reset(self, cmd: Command):
        self.pixel_pos = self._cell_to_pixel(self.cell)
        self.moving = False
        self.next_state_when_finished = None  # Idle has no auto-transition by itself

    def update(self, now_ms: int):
        pass

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return False

class LongRestPhysics(Physics):
    """Physics for long rest state, following a move."""
    def reset(self, cmd: Command):
        self.pixel_pos = self._cell_to_pixel(self.cell)
        self.moving = False
        # Auto-transition back to Idle after long rest.
        self.next_state_when_finished = "Idle"

    def update(self, now_ms: int):
        pass

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return False

class ShortRestPhysics(Physics):
    """Physics for short rest state, following a jump."""
    def reset(self, cmd: Command):
        self.pixel_pos = self._cell_to_pixel(self.cell)
        self.moving = False
        # Auto-transition back to Idle after short rest.
        self.next_state_when_finished = "Idle"

    def update(self, now_ms: int):
        pass

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return False
