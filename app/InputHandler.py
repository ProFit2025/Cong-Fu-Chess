from typing import Optional
from Command import Command  # Importing the Command dataclass

class InputHandler:
    """
    Handles keyboard input for two users.
    
    For user 1:
      - Movement: "up", "down", "left", "right"
      - Selection: "enter" (first to select the soldier, second to select destination)
      - Jump: "right_shift" (only allowed after soldier selection)
    
    For user 2:
      - Movement: "w" (up), "s" (down), "a" (left), "d" (right)
      - Selection: "space" (first to select the soldier, second to select destination)
      - Jump: "left_shift" (only allowed after soldier selection)
    
    The handler enforces that a move cannot place the soldier outside the board boundaries.
    """
    def __init__(self, board_width: int, board_height: int):
        self.board_width = board_width
        self.board_height = board_height
        self.player_states = {
            1: {"pos": (0, 0), "selected": None, "mode": "select_soldier"},
            2: {"pos": (board_width - 1, board_height - 1), "selected": None, "mode": "select_soldier"}
        }
        self.movement_keys = {
            1: {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)},
            2: {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
        }
        self.select_keys = {
            1: "enter",
            2: "space"
        }
        self.jump_keys = {
            1: "right_shift",
            2: "left_shift"
        }
    
    def handle_key(self, user: int, key: str, timestamp: Optional[int] = None) -> Optional[Command]:
        """
        Processes a key event for the specified user.
        
        For movement keys: it updates the current position if within board bounds.
        For selection keys: on first press, it records the current position (mode="select_destination").
                            on second press, it returns a move command and resets mode.
        For jump keys: if pressed during the destination selection, it returns a jump command
                      and resets mode. Otherwise, it is ignored.
        
        :param user: 1 or 2
        :param key: the key pressed (e.g., "up", "enter", etc.)
        :param timestamp: optional timestamp for the command (default 0)
        :return: A Command instance if a full command is completed, else None.
        """
        state = self.player_states[user]
        
        # Process movement keys
        if key in self.movement_keys[user]:
            dx, dy = self.movement_keys[user][key]
            new_x = state["pos"][0] + dx
            new_y = state["pos"][1] + dy
            if 0 <= new_x < self.board_width and 0 <= new_y < self.board_height:
                state["pos"] = (new_x, new_y)
            return None
        
        # Process selection key
        if key == self.select_keys[user]:
            if state["mode"] == "select_soldier":
                # Record soldier selection position
                state["selected"] = state["pos"]
                state["mode"] = "select_destination"
                return None
            elif state["mode"] == "select_destination":
                # Complete move command
                command = Command(
                    timestamp=timestamp if timestamp is not None else 0,
                    piece_id=f"P{user}",
                    type="Move",
                    params=[state["selected"], state["pos"]]
                )
                state["selected"] = None
                state["mode"] = "select_soldier"
                return command
        
        # Process jump key
        if key == self.jump_keys[user]:
            if state["mode"] == "select_destination":
                command = Command(
                    timestamp=timestamp if timestamp is not None else 0,
                    piece_id=f"P{user}",
                    type="Jump",
                    params=[state["selected"], state["pos"]]
                )
                state["selected"] = None
                state["mode"] = "select_soldier"
                return command
        # Key not handled or in an invalid state: ignore
        return None

    def get_state(self, user: int) -> dict:
        """
        Returns a copy of the internal state for the specified user.
        Useful for testing.
        """
        return self.player_states[user].copy()