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
        self.command_start_time = 0

    def set_transition(self, event: str, target: "State"):
        """Define a state transition on the given event."""
        self.transitions[event] = target

    def reset(self, cmd: Command):
        """Reset the state with the new command."""
        self.current_command = cmd
        self.command_start_time = cmd.timestamp
        
        # Reset all components with the new command
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
            next_state = self.transitions[event].clone()
            next_state.physics.cell = self.physics.cell
            return next_state
        return self

    def update(self, now_ms: int) -> "State":
        """Update the state based on game time, and auto-transition if appropriate."""
        # Update physics and graphics components.
        self.physics.update(now_ms)
        self.graphics.update(now_ms)

        # Debug: Print current physics state and next state flag.
        print(f"[DEBUG] State.update: moving={getattr(self.physics, 'moving', None)}, next={self.physics.next_state_when_finished}")

        # Check if the current state's action is complete.
        if self.can_transition(now_ms):
            next_event = self.physics.next_state_when_finished
            if next_event is not None and next_event in self.transitions:
                next_state = self.transitions[next_event]
                # Optionally, use a dummy command so that next_state resets properly.
                from app.Command import Command  # ensure Command is imported
                dummy_cmd = Command(timestamp=now_ms, piece_id="", type=next_event, params=[])
                next_state.reset(dummy_cmd)
                # Debug: Indicate auto-transition.
                print(f"[DEBUG] Auto-transitioning from state to {next_event} state")
                return next_state
        return self

    def get_command(self) -> Command:
        """Return the current command (if any) for this state."""
        return self.current_command

    def __eq__(self, other):
        """Check if two states are equal."""
        if not isinstance(other, State):
            return False
        return (id(self) == id(other))  # השוואה לפי זהות האובייקט

    def __ne__(self, other):
        """Check if two states are not equal."""
        return not self.__eq__(other)
    
    def clone(self) -> "State":
        return State(
            self.moves, 
            self.graphics.clone(), 
            self.physics.clone()
        )
