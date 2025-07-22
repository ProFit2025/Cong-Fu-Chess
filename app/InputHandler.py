from typing import Optional, Tuple
from app.Command import Command 

class InputHandler:
    """
    Handles keyboard input for two users.
    
    For user 1:
      - Movement: "up", "down", "left", "right"
      - Selection: "enter" (first to select the soldier, second to select destination)
      - Jump: "right_shift" (or "right shift") – create Jump command using the current square
    For user 2:
      - Movement: "w", "s", "a", "d"
      - Selection: "space" (first to select the soldier, second to select destination)
      - Jump: "left_shift" (or "left shift") – create Jump command using the current square
    
    The handler enforces that a move (or jump) only מתבצעת אם יש כלי (soldier) במשבצת.
    """
    def __init__(self, board_width: int, board_height: int, piece_at_callback):
        self.board_width = board_width
        self.board_height = board_height
        # Callback שמחזיר את הכלי במשבצת (אם יש)
        self.get_piece_at = piece_at_callback
        # אתחול מצב לכל שחקן – במקום piece_id נעדכן לפני יצירת הפקודה
        self.player_states = {
            1: {"pos": (0, 0), "selected": None, "mode": "select_soldier", "piece_id": None},
            2: {"pos": (board_width - 1, board_height - 1), "selected": None, "mode": "select_soldier", "piece_id": None}
        }
        self.movement_keys = {
            1: {"left": (0, -1), "right": (0, 1), "up": (-1, 0), "down": (1, 0)},
            2: {"a": (0, -1), "d": (0, 1), "w": (-1, 0), "s": (1, 0)}
        }
        self.select_keys = {
            1: "enter",
            2: "space"
        }
        self.jump_keys = {
            1: "right shift",
            2: "shift"
        }
    
    def coord_to_notation(self, pos: Tuple[int, int]) -> str:
        """
        Convert board coordinates from (x, y) tuple to chess notation like 'a1'.
        Assumes x is column index and y is row index.
        """
        x, y = pos
        return f"{chr(x + ord('a'))}{y + 1}"
    
    def handle_key(self, user: int, key: str, timestamp: Optional[int] = None) -> Optional[Command]:
        """
        Processes a key event for the specified user.
        
        - Movement keys: update the current position if within board bounds.
        - Selection keys:
             * If in "select_soldier" mode:
                  o Check if there's a soldier (using get_piece_at) at the current position.
                  o Verify that for user 1 the piece’s id starts with "B" (black) and for user 2 with "W" (white).
                  o If valid, record the current position as selected and store the piece_id, then change mode to "select_destination".
                  o Otherwise, ignore the key.
             * If in "select_destination" mode:
                  o Complete a Move command using the recorded (source) and current (destination) positions.
                  o Reset mode to "select_soldier".
        - Jump keys:
             * At any moment if the jump key is pressed, check if there’s a soldier of the correct color
               at the current position. If so, immediately create a Jump command (its params list will contain only the current position)
               and reset the mode.
             * Otherwise, ignore the key.
        
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

        # Process selection key for Move command
        if key == self.select_keys[user]:
            if state["mode"] == "select_soldier":
                # Attempt to select a soldier at the current position.
                piece = self.get_piece_at(state["pos"])
                if piece is None:
                    # אין כלי – לא מבצעים כלום.
                    return None
                # בדיקת צבע: שחקן 1 רק חיילים שחורים (id מתחיל ב-"B"), שחקן 2 רק חיילים לבנים (id מתחיל ב-"W")
                if (user == 1 and not piece.piece_id[1] == 'B') or (user == 2 and not piece.piece_id[1] == 'W'):
                    return None
                # בחרנו כלי – שמורים את המיקום ואת המזהה הייחודי שלו, ועוברים למצב בחירת יעד.
                state["selected"] = state["pos"]
                state["piece_id"] = piece.piece_id
                state["mode"] = "select_destination"
                return None
            elif state["mode"] == "select_destination":
                # השלמת פקודת Move – מקור: state["selected"], יעד: state["pos"]
                command = Command(
                    timestamp=timestamp if timestamp is not None else 0,
                    piece_id=state["piece_id"],
                    type="Move",
                    params=[self.coord_to_notation(state["selected"]),
                            self.coord_to_notation(state["pos"])]
                )
                state["selected"] = None
                state["mode"] = "select_soldier"
                return command

        # Process jump key – regardless of current mode, execute jump if the soldier of correct color קיים.
        if key == self.jump_keys[user]:
            piece = self.get_piece_at(state["pos"])
            if piece is None:
                return None
            if (user == 1 and not piece.piece_id[1] == 'B') or (user == 2 and not piece.piece_id[1] == 'W'):
                return None
            command = Command(
                timestamp=timestamp if timestamp is not None else 0,
                piece_id=piece.piece_id,
                type="Jump",
                params=[self.coord_to_notation(state["pos"])]
            )
            state["selected"] = None
            state["mode"] = "select_soldier"
            return command
        
        # Key not handled: ignore.
        return None

    def get_state(self, user: int) -> dict:
        """
        Returns a copy of the internal state for the specified user.
        Useful for testing.
        """
        return self.player_states[user].copy()
    
    def get_cursor_position(self, user: int) -> Tuple[int, int]:
        """
        Returns the current cursor position for the specified user.
        """
        return self.player_states[user]["pos"]
