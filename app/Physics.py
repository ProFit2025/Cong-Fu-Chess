from typing import Tuple, Optional
from app.Command import Command
from app.Board import Board


class Physics:
    """Base physics class for all piece types."""

    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 1.0):
        self.board = board
        self.cell = start_cell
        self.speed_m_s = speed_m_s

    def _cell_to_pixel(self, cell: Tuple[int, int]) -> Tuple[float, float]:
        """Convert board cell (row, col) to pixel coordinates."""
        row, col = cell
        x = col * self.board.cell_W_pix
        y = row * self.board.cell_H_pix
        return float(x), float(y)

    def reset(self, cmd: Command):
        """Reset must be implemented by subclasses."""
        raise NotImplementedError("reset() must be implemented in a subclass.")

    def update(self, now_ms: int):
        """Update must be implemented by subclasses."""
        raise NotImplementedError("update() must be implemented in a subclass.")

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return True

    def get_pos(self) -> Tuple[float, float]:
        """Return current pixel position."""
        return self._cell_to_pixel(self.cell)


class IdlePhysics(Physics):
    """Physics for a piece that does not move."""

    def reset(self, cmd: Command):
        # אין תנועה – רק מאפסים את מצב התנועה
        self.cell = self.cell

    def update(self, now_ms: int):
        # אין עדכון בתנועה למצב "מנוחה"
        pass

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return False


class MovePhysics(Physics):
    """Physics for pieces moving smoothly between cells."""

    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 1.0):
        super().__init__(start_cell, board, speed_m_s)
        self.pixel_pos = self._cell_to_pixel(start_cell)
        self.target_cell = start_cell
        self.target_pixel = self.pixel_pos
        self.moving = False
        self.last_update_ms: Optional[int] = None
        self.next_state_when_finished = "Idle"

    def _parse_target(self, cmd: Command):
        """Extract target cell from command parameters."""
        if hasattr(cmd, "params") and len(cmd.params) >= 2:
            to = cmd.params[1]
            if isinstance(to, tuple):
                return to
            elif isinstance(to, str) and len(to) == 2:
                col = ord(to[0].lower()) - ord('a')
                row = int(to[1]) - 1
                return (row, col)
        return self.cell

    def reset(self, cmd: Command):
        self.target_cell = self._parse_target(cmd)
        self.target_pixel = self._cell_to_pixel(self.target_cell)
        self.moving = (self.cell != self.target_cell)
        self.last_update_ms = None

    def update(self, now_ms: int):
        if not self.moving:
            return

        if self.last_update_ms is None:
            elapsed = 0.016  # initial small step (16ms)
        else:
            elapsed = (now_ms - self.last_update_ms) / 1000.0

        self.last_update_ms = now_ms

        x, y = self.pixel_pos
        tx, ty = self.target_pixel
        dx, dy = tx - x, ty - y
        dist = (dx**2 + dy**2)**0.5

        if dist == 0:
            self.cell = self.target_cell
            self.pixel_pos = self.target_pixel
            self.moving = False
            return

        cell_diag = (self.board.cell_W_pix**2 + self.board.cell_H_pix**2)**0.5
        speed_pix_s = self.speed_m_s * cell_diag
        move_dist = min(dist, speed_pix_s * elapsed)

        if move_dist >= dist:
            self.pixel_pos = self.target_pixel
            self.cell = self.target_cell
            self.moving = False
        else:
            self.pixel_pos = (x + dx * (move_dist / dist), y + dy * (move_dist / dist))

    def get_pos(self) -> Tuple[float, float]:
        return self.pixel_pos


class JumpPhysics(Physics):
    """Physics for pieces that instantly jump to a target cell."""

    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 1.0):
        super().__init__(start_cell, board, speed_m_s)
        self.target_cell = start_cell
        self.target_pixel = self._cell_to_pixel(start_cell)
        self.moving = False
        self.next_state_when_finished = "Idle"

    def _parse_target(self, cmd: Command):
        if hasattr(cmd, "params") and len(cmd.params) >= 2:
            to = cmd.params[1]
            if isinstance(to, tuple):
                return to
            elif isinstance(to, str) and len(to) == 2:
                col = ord(to[0].lower()) - ord('a')
                row = int(to[1]) - 1
                return (row, col)
        return self.cell

    def reset(self, cmd: Command):
        self.target_cell = self._parse_target(cmd)
        self.target_pixel = self._cell_to_pixel(self.target_cell)
        self.moving = (self.cell != self.target_cell)

    def update(self, now_ms: int):
        if self.moving:
            self.cell = self.target_cell
            self.moving = False

    def get_pos(self) -> Tuple[float, float]:
        return self._cell_to_pixel(self.cell)


class LongRestPhysics(Physics):
    """Physics for invulnerable pieces."""

    def reset(self, cmd: Command):
        # אין תנועה – המצב נשאר קבוע
        pass

    def update(self, now_ms: int):
        pass

    def can_be_captured(self) -> bool:
        return False

    def can_capture(self) -> bool:
        return False


class ShortRestPhysics(Physics):
    """Physics for pieces that are vulnerable but do not capture."""

    def reset(self, cmd: Command):
        # אין תנועה – פשוט מאפסים
        pass

    def update(self, now_ms: int):
        pass

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return False
