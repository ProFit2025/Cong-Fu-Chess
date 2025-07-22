from app.Moves import Moves
from app.Graphics import Graphics
from app.Physics import Physics
from typing import Dict, Optional
from app.Command import Command


class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        """Initialize state with moves, graphics, and physics components."""
        self.moves = moves
        self.graphics = graphics
        self.physics = physics
        self.transitions: Dict[str, State] = {}
        self.current_command: Optional[Command] = None

    def set_transition(self, event: str, target: "State"):
        """Define a state transition on the given event."""
        self.transitions[event] = target

    def reset(self, cmd: Command):
        """Reset the state with the new command."""
        self.current_command = cmd
        self.physics.reset(cmd)
        self.graphics.reset(cmd)

    def can_transition(self, now_ms: int) -> bool:
        """Return True if the physics is no longer moving (i.e. action complete)."""
        if hasattr(self.physics, 'moving'):
            return not self.physics.moving
        return True

    def get_state_after_command(self, cmd: Command, now_ms: int) -> "State":
        """
        Return the next state based on the event (command type). 
        If no transition is defined, return self.
        """
        event = cmd.type
        if event in self.transitions:
            return self.transitions[event]
        return self

    def update(self, now_ms: int) -> "State":
        """Update the state based on game time, and transition if appropriate."""
        self.physics.update(now_ms)
        self.graphics.update(now_ms)
        if self.can_transition(now_ms):
            if hasattr(self.physics, 'next_state_when_finished'):
                next_event = self.physics.next_state_when_finished
                if next_event in self.transitions:
                    return self.transitions[next_event]
        return self

    def get_command(self) -> Command:
        """Return the current command (if any) for this state."""
        return self.current_command