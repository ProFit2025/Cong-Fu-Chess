import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from app.Board   import Board
from app.Command import Command
from app.Piece   import Piece
from app.Img import Img


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
        """Start the user input thread for mouse handling."""
        def mouse_thread():
            while True:
                event = cv2.waitKey(1)
                if event == 27:  
                    break
                
                now = self.game_time_ms()
                
                cmd = Command(
                    timestamp=now,
                    piece_id='P1',
                    type = 'Move',
                    params = ['b2', 'b5']
                )
                self.user_input_queue.put(cmd)
                time.sleep(0.01)
        t = threading.Thread(target=mouse_thread, daemon=True)
        t.start()
        
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
