from app.Moves import Moves
from app.Graphics import Graphics
from app.Physics import Physics
from typing import Dict, Optional
from app.Command import Command
from app.Physics import notation_to_cell  # ensure this is imported


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
        If no transition is defined or the requested move is illegal, return self.
        """
        event = cmd.type
        # For Move commands, check if the move is legal using is_move_legal.
        if event == "Move":
            # cmd.params[1] holds the destination in chess notation.
            dest = notation_to_cell(cmd.params[1])
            
            if not self.is_move_legal(dest):
                # Illegal move: do not change state.
                print(f"[DEBUG] Move to {dest} is illegal. Staying in current state.")
                return self
        if event in self.transitions:
            next_state = self.transitions[event].clone()
            # Update position in the cloned state's physics to the current state's position.
            next_state.physics.cell = self.physics.cell
            return next_state
        return self

    def update(self, now_ms: int) -> "State":
        """Update the state based on game time, and auto-transition if appropriate."""
        # Update physics and graphics components.
        self.physics.update(now_ms)
        self.graphics.update(now_ms)
        
        # Determine if this state has completed its action.
        # When loop is False, we consider the state complete if the last frame is shown.
        # Otherwise (if loop is True) we allow for a minimal delay.
        state_complete = False
        if not self.physics.moving:
            if not self.graphics.loop:
                if self.graphics.current_frame_idx == len(self.graphics.frames) - 1:
                    state_complete = True
            else:
                state_complete = True  # allow auto-transition in looping states after delay

        if state_complete:
            next_event = self.physics.next_state_when_finished
            if next_event is not None:
                min_delay = 300  # milliseconds minimal delay before transition
                if now_ms - self.command_start_time < min_delay:
                    return self
                # If expected transition is missing, fall back to Idle.
                if next_event not in self.transitions:
                    next_event = "Idle"
                next_state = self.transitions.get(next_event)
                if next_state is not None:
                    dummy_cmd = Command(timestamp=now_ms, piece_id="", type=next_event, params=[])
                    next_state.reset(dummy_cmd)
                    # Update next state's physics so that its position reflects the current state's position.
                    next_state.physics.cell = self.physics.cell
                    next_state.physics.pixel_pos = self.physics.get_pos()
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
        new_state = State(
            self.moves, 
            self.graphics.clone(), 
            self.physics.clone()
        )
        new_state.transitions = self.transitions.copy()  
        new_state.current_command = self.current_command
        new_state.command_start_time = self.command_start_time
        return new_state

    def is_move_legal(self, dest: tuple) -> bool:
        """
        Check if a move to the destination cell is legal for the current piece,
        according to the Moves object for this state.
        dest: (col, row) tuple
        Returns True if the move is legal, False otherwise.
        """
        if not hasattr(self, 'moves') or self.moves is None:
            return False
        pos_x, pos_y = self.physics.cell
        
        possible_moves = self.moves.get_moves(pos_x, pos_y)
        print("dest ===========" , dest, "position======", (pos_x, pos_y))
        print(possible_moves)
        return dest in possible_moves