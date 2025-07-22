from app.Board import Board
from app.Physics import IdlePhysics, MovePhysics, JumpPhysics, LongRestPhysics, ShortRestPhysics, Physics

class PhysicsFactory:
    def __init__(self, board: Board): 
        """Initialize physics factory with board."""
        self.board = board

    def create(self, start_cell, cfg) -> "Physics":
        """Create a physics object based on configuration."""
        speed = cfg.get("speed_m_per_sec", 1.0)
        p_type = cfg.get("type", "idle").lower()
        if p_type == "move":
            return MovePhysics(start_cell, self.board, speed_m_s=speed)
        elif p_type == "jump":
            return JumpPhysics(start_cell, self.board, speed_m_s=speed)
        elif p_type == "longrest":
            return LongRestPhysics(start_cell, self.board, speed_m_s=speed)
        elif p_type == "shortrest":
            return ShortRestPhysics(start_cell, self.board, speed_m_s=speed)
        else:
            # ברירת מחדל - IdlePhysics
            return IdlePhysics(start_cell, self.board, speed_m_s=speed)

