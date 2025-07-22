import pytest
from app.InputHandler import InputHandler

class MockPiece:
    """Mock piece class for testing"""
    def __init__(self, piece_id):
        self.piece_id = piece_id

def create_mock_board():
    """Create a mock board with pieces for testing"""
    board = {}
    # Black pieces for user 1
    board[(0, 0)] = MockPiece("PBa1")  # Black pawn at a1
    board[(1, 0)] = MockPiece("RBb1")  # Black rook at b1
    board[(2, 2)] = MockPiece("NBc3")  # Black knight at c3
    
    # White pieces for user 2
    board[(7, 7)] = MockPiece("PWh8")  # White pawn at h8
    board[(6, 7)] = MockPiece("RWg8")  # White rook at g8
    board[(5, 5)] = MockPiece("NWf6")  # White knight at f6
    
    return board

def piece_at_callback_factory(board):
    """Factory function to create piece_at callback"""
    def piece_at_callback(pos):
        return board.get(pos, None)
    return piece_at_callback

def test_user1_movement_within_bounds():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    
    # Act: move "right" then "down"
    handler.handle_key(1, "right")
    handler.handle_key(1, "down")
    state = handler.get_state(1)
    
    # Assert: position should be updated to (1, 1)
    assert state["pos"] == (1, 1)

def test_user2_movement_at_board_edge():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # User 2 starts at (7, 7) for an 8x8 board.
    
    # Act: attempt to move "s" (down) and "d" (right) which would exceed boundaries
    handler.handle_key(2, "s")
    handler.handle_key(2, "d")
    state = handler.get_state(2)
    
    # Assert: position remains unchanged at (7, 7)
    assert state["pos"] == (7, 7)

def test_user1_move_command():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # User 1 starting at (0,0) where there's a black pawn
    
    # Act:
    # First press of "enter" records the soldier location.
    handler.handle_key(1, "enter")
    # Move down to (1,0) - with current directions, (0,0) -> (1,0) converts to "a1" -> "b1"
    handler.handle_key(1, "down")
    # Second press of "enter" completes the move command with timestamp=100
    command = handler.handle_key(1, "enter", timestamp=100)
    
    # Assert:
    assert command is not None
    assert command.piece_id == "PBa1"
    assert command.type == "Move"
    assert command.timestamp == 100
    # Updated expected parameters to reflect the current movement directions.
    assert command.params == ["a1", "b1"]  # Chess notation format: from a1 to b1

def test_user2_move_command():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # User 2 starts at (7,7) where there's a white pawn
    
    # Act:
    # First press of "space" records the soldier location
    handler.handle_key(2, "space")
    # Move up to (6,7) - "w" decrements the row (first coordinate)
    handler.handle_key(2, "w")
    # Second press of "space" completes the move command
    command = handler.handle_key(2, "space", timestamp=150)
    
    # Assert:
    assert command is not None
    assert command.piece_id == "PWh8"
    assert command.type == "Move"
    assert command.timestamp == 150
    assert command.params == ["h8", "g8"]  # Chess notation format: from h8 to g8

def test_user1_jump_command():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # Move to position (2,2) where there's a black knight
    handler.handle_key(1, "down")   # (1,0)
    handler.handle_key(1, "down")   # (2,0)
    handler.handle_key(1, "right")  # (2,1)
    handler.handle_key(1, "right")  # (2,2)
    
    # Act: Press jump key ("right shift") to create jump command
    command = handler.handle_key(1, "right shift", timestamp=200)
    
    # Assert:
    assert command is not None
    assert command.piece_id == "NBc3"
    assert command.type == "Jump"
    assert command.timestamp == 200
    assert command.params == ["c3"]

def test_user2_jump_command():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # Move to position (5,5) where there's a white knight
    handler.handle_key(2, "w")  # (6,7)
    handler.handle_key(2, "w")  # (5,7)
    handler.handle_key(2, "a")  # (5,6)
    handler.handle_key(2, "a")  # (5,5)
    
    # Act: Press jump key ("shift") to create jump command
    command = handler.handle_key(2, "shift", timestamp=250)
    
    # Assert:
    assert command is not None
    assert command.piece_id == "NWf6"
    assert command.type == "Jump"
    assert command.timestamp == 250
    assert command.params == ["f6"]

def test_invalid_selection_no_piece():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # Move to empty position
    handler.handle_key(1, "down")   # (1,0) - has a piece but let's move away
    handler.handle_key(1, "right")  # (1,1) - empty position
    
    # Act: Try to select at empty position
    command = handler.handle_key(1, "enter")
    
    # Assert: No command should be produced
    assert command is None
    state = handler.get_state(1)
    assert state["mode"] == "select_soldier"
    assert state["selected"] is None

def test_invalid_selection_wrong_color():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # Move user 1 to position with white piece
    for _ in range(7):
        handler.handle_key(1, "down")   # Move to (7,0)
    for _ in range(7):
        handler.handle_key(1, "right")  # Move to (7,7) where white pawn is
    
    # Act: User 1 tries to select white piece
    command = handler.handle_key(1, "enter")
    
    # Assert: No command should be produced
    assert command is None
    state = handler.get_state(1)
    assert state["mode"] == "select_soldier"
    assert state["selected"] is None

def test_invalid_jump_no_piece():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # Move to empty position
    handler.handle_key(1, "down")   # (1,0) - has a piece
    handler.handle_key(1, "right")  # (1,1) - empty position
    
    # Act: Try to jump from empty position
    command = handler.handle_key(1, "right shift", timestamp=300)
    
    # Assert: No command should be produced
    assert command is None
    state = handler.get_state(1)
    assert state["mode"] == "select_soldier"

def test_invalid_jump_wrong_color():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # Move user 1 to position with white piece
    for _ in range(7):
        handler.handle_key(1, "down")   # Move to (7,0)
    for _ in range(7):
        handler.handle_key(1, "right")  # Move to (7,7) where white pawn is
    
    # Act: User 1 tries to jump with white piece
    command = handler.handle_key(1, "right shift", timestamp=350)
    
    # Assert: No command should be produced
    assert command is None

def test_invalid_movement_out_of_bounds():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    # User 1 starts at (0,0)
    
    # Act: try to move "up" and "left", which should be ignored.
    handler.handle_key(1, "up")
    handler.handle_key(1, "left")
    state = handler.get_state(1)
    
    # Assert: position remains at (0,0)
    assert state["pos"] == (0, 0)

def test_jump_resets_selection_mode():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    
    # Put user in select_destination mode
    handler.handle_key(1, "enter")  # Select piece at (0,0)
    state = handler.get_state(1)
    assert state["mode"] == "select_destination"
    
    # Act: Press jump key
    command = handler.handle_key(1, "right shift", timestamp=400)
    
    # Assert: Jump command created and mode reset
    assert command is not None
    assert command.type == "Jump"
    state = handler.get_state(1)
    assert state["mode"] == "select_soldier"
    assert state["selected"] is None

def test_coord_to_notation():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    
    # Test coordinate conversion
    assert handler.coord_to_notation((0, 0)) == "a1"
    assert handler.coord_to_notation((7, 7)) == "h8"
    assert handler.coord_to_notation((3, 4)) == "d5"

def test_get_cursor_position():
    # Arrange
    board = create_mock_board()
    handler = InputHandler(8, 8, piece_at_callback_factory(board))
    
    # Test initial positions
    assert handler.get_cursor_position(1) == (0, 0)
    assert handler.get_cursor_position(2) == (7, 7)
    
    # Move and test
    handler.handle_key(1, "right")
    handler.handle_key(1, "down")
    assert handler.get_cursor_position(1) == (1, 1)