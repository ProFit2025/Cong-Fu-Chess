from app.Board import Board
from app.Physics import Physics

class PhysicsFactory:      # very light for now
    def __init__(self, board: Board): 
        """Initialize physics factory with board."""
        self.board = board

    def create(self, start_cell, cfg) -> Physics:
        """Create a physics object with the given configuration."""
        speed = cfg.get("speed_m_per_sec", 1.0)
        return Physics(start_cell, self.board, speed_m_s=speed)
  
    