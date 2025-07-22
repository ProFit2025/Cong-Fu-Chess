import inspect
import pathlib
import queue, threading, time, cv2, math
import numpy as np
from typing import List, Dict, Tuple, Optional
from app.Board   import Board
from app.Command import Command
from app.Piece   import Piece
from app.Img import Img
from app.InputHandler import InputHandler
import keyboard


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces and board."""
        self.pieces = pieces
        # Build a dictionary for quick lookup by unique piece_id
        self.pieces_by_id = {p.piece_id: p for p in pieces}
        self.board = board
        self.user_input_queue = queue.Queue()
        self._start_time = time.monotonic()
        self._current_frame = self.clone_board()
        # Pass get_piece_at callback to InputHandler
        self.input_handler = InputHandler(board.W_cells, board.H_cells, self.get_piece_at)


    def get_piece_at(self, pos: Tuple[int, int]) -> Optional[Piece]:
        """Return the piece at the given board cell, or None if empty."""
        for p in self.pieces:
            if p.current_state.physics.cell == pos:
                print("@@@@@@@@@@@piece: ", p.piece_id, pos)
                return p
        return None

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
        """Start the user input thread that uses the keyboard library for input."""
        def key_thread():
            while True:
                event = keyboard.read_event() 
                if event.event_type != "down":
                    continue
                key = event.name 
                if key == "esc":
                    break
                now = self.game_time_ms()
                if key in self.input_handler.movement_keys[1] or key == self.input_handler.select_keys[1] or key == self.input_handler.jump_keys[1]:
                    user = 1
                elif key in self.input_handler.movement_keys[2] or key == self.input_handler.select_keys[2] or key == self.input_handler.jump_keys[2]:
                    user = 2
                else:
                    continue

                cmd = self.input_handler.handle_key(user, key, timestamp=now)
                print("==========", self.input_handler.get_state(user), "========")
                
                if cmd:
                    print(cmd)
                    self.user_input_queue.put(cmd)

        threading.Thread(target=key_thread, daemon=True).start()
        

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
        board_copy = self.clone_board()  
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


    def _process_input(self, cmd: Command):
        """
        Process an input command by finding the unique piece (based on piece_id)
        and invoking its on_command() handler with the current game time.
        """
        now_ms = self.game_time_ms()
        piece = self.pieces_by_id.get(cmd.piece_id)
        if piece:
            piece.on_command(cmd, now_ms)
            

    # ─── capture resolution ────────────────────────────────────────────────          
    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        captured = set()
        # השווה כל זוג ייחודי של כלים
        for i in range(len(self.pieces)):
            for j in range(i + 1, len(self.pieces)):
                p1, p2 = self.pieces[i], self.pieces[j]
                # אם שני הכלים נמצאים באותה משבצת
                if p1.current_state.physics.cell == p2.current_state.physics.cell:
                    p1_can_capture = p1.current_state.physics.can_capture()
                    p1_can_be_captured = p1.current_state.physics.can_be_captured()
                    p2_can_capture = p2.current_state.physics.can_capture()
                    p2_can_be_captured = p2.current_state.physics.can_be_captured()

                    # מצב בו רק p1 יכול לתוקף
                    if p1_can_capture and p2_can_be_captured and not (p2_can_capture):
                        captured.add(p2)
                    # מצב בו רק p2 יכול לתוקף
                    elif p2_can_capture and p1_can_be_captured and not (p1_can_capture):
                        captured.add(p1)
                    # מצב בו שני הכלים יכולים לתוקף ולהיאכל
                    elif p1_can_capture and p1_can_be_captured and p2_can_capture and p2_can_be_captured:
                        # הכלי שהעדכון האחרון שלו מוקדם יותר "נצח"
                        if p1.current_state.last_update < p2.current_state.last_update:
                            captured.add(p2)
                        else:
                            captured.add(p1)
        # הסרת הכלים שנלכדו מרשימת הכלים ומה-dictionary
        for p in captured:
            if p in self.pieces:
                self.pieces.remove(p)
                self.pieces_by_id.pop(p.piece_id, None)

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended, which occurs if one of the kings is missing."""
        has_black_king = any(p.piece_id.startswith("KB") for p in self.pieces)
        has_white_king = any(p.piece_id.startswith("KW") for p in self.pieces)
        # Game continues only if both kings are still present.
        return not (has_black_king and has_white_king)

    def _announce_win(self):
        """Announce the winner based on which king remains."""
        has_black_king = any(p.piece_id.startswith("KB") for p in self.pieces)
        has_white_king = any(p.piece_id.startswith("KW") for p in self.pieces)
        if has_black_king and not has_white_king:
            print("Game Over! Black wins!")
        elif has_white_king and not has_black_king:
            print("Game Over! White wins!")
        else:
            print("Game Over! No clear winner.")