import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from app.Board   import Board
from app.Command import Command
from app.Piece   import Piece
from app.Img import Img
from app.InputHandler import InputHandler


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = pieces
        self.board = board
        self.user_input_queue = queue.Queue()
        self._start_time = time.monotonic()
        self._current_frame = self.clone_board()
        self.input_handler = InputHandler(board.W_cells, board.H_cells)
 


    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return int((time.monotonic() - self._start_time) * 1000)

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        return self.board.clone()

    def start_user_input_thread(self):
        """Start the user input thread that uses InputHandler."""
        def key_thread():
            while True:
                key_num = cv2.waitKey(1)
                if key_num == 27:
                    break

                key = self._convert_key(key_num)
                now = self.game_time_ms()

                # קביעת המשתמש על סמך המקש
                if key in self.input_handler.movement_keys[1] or key == self.input_handler.select_keys[1] or key == self.input_handler.jump_keys[1]:
                    user = 1
                elif key in self.input_handler.movement_keys[2] or key == self.input_handler.select_keys[2] or key == self.input_handler.jump_keys[2]:
                    user = 2
                else:
                    # במידה והמקש לא שייך לאף אחד
                    continue

                cmd = self.input_handler.handle_key(user, key, timestamp=now)
                if cmd:
                    self.user_input_queue.put(cmd)
               
        t = threading.Thread(target=key_thread, daemon=True)
        t.start()
        
        
    def _convert_key(self, key_num: int) -> str:
        key_map = {
            2490368: "up",      
            2621440: "down",   
            2424832: "left",    
            2555904: "right", 
            13: "enter",       
            32: "space",       
            65505: "right_shift", 
            65506: "left_shift"
        }
        return key_map.get(key_num, "")


    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        self.start_user_input_thread() # QWe2e5

        start_ms = self.game_time_ms()
        for p in self.pieces:
            p.reset(start_ms)

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win():
            now = self.game_time_ms() # monotonic time ! not computer time.

            # (1) update physics & animations
            for p in self.pieces:
                p.update(now)

            # (2) handle queued Commands from mouse thread
            while not self.user_input_queue.empty(): # QWe2e5
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            # (3) draw current position
            self._draw()
            if not self._show():           # returns False if user closed window
                break

            # (4) detect captures
            self._resolve_collisions()

        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _draw(self):
        """Draw the current game state."""
        # צור עותק של הלוח כדי לצייר עליו את הכלים
        board_copy = self.clone_board()  # Board עם img שהוא Img
        now = self.game_time_ms()
        # כל כלי מצייר את עצמו על הלוח (ה-img של הלוח)
        for piece in self.pieces:
            piece.draw_on_board(board_copy, now)
       
        self._current_frame = board_copy

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        if self._current_frame is None:
            return True  # אין מה להציג, ממשיכים

        cv2.imshow("Cong Fu Chess", self._current_frame.img.img)
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            return False  # המשתמש סגר
        return True

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        pass

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        pass

    def _announce_win(self):
        """Announce the winner."""
        pass
