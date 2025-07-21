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
        """Set a transition from this state to another state on an event."""
        self.transitions[event] = target

    def reset(self, cmd: Command):
        """Reset the state with a new command."""
        self.current_command = cmd
        self.physics.reset(cmd)
        self.graphics.reset(cmd)

    def can_transition(self, now_ms: int) -> bool:
        """Check if the state can transition."""
        # Example: Check if the physics has completed its action
        return False

    def get_state_after_command(self, cmd: Command, now_ms: int) -> "State":
        """Get the next state after processing a command."""
        event = cmd.type  # Use the command type as the event
        if event in self.transitions:
            return self.transitions[event]
        return self  # Stay in the current state if no transition is defined

    def update(self, now_ms: int) -> "State":
        """Update the state based on current time."""
        self.physics.update(now_ms)
        self.graphics.update(now_ms)

        # Check if a transition is possible
        if self.can_transition(now_ms):
            next_state_name = self.physics.next_state_when_finished
            if next_state_name in self.transitions:
                return self.transitions[next_state_name]

        return self  # Stay in the current state if no transition occurs

    def get_command(self) -> Command:
        """Get the current command for this state."""
        return self.current_command