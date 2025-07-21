import pytest
from app.InputHandler import InputHandler

def test_user1_movement_within_bounds():
    # Arrange
    handler = InputHandler(8, 8)
    
    # Act: move "right" then "down"
    handler.handle_key(1, "right")
    handler.handle_key(1, "down")
    state = handler.get_state(1)
    
    # Assert: position should be updated to (1, 1)
    assert state["pos"] == (1, 1)

def test_user2_movement_at_board_edge():
    # Arrange
    handler = InputHandler(8, 8)
    # User 2 starts at (7, 7) for an 8x8 board.
    
    # Act: attempt to move "s" (down) and "d" (right) which would exceed boundaries
    handler.handle_key(2, "s")
    handler.handle_key(2, "d")
    state = handler.get_state(2)
    
    # Assert: position remains unchanged at (7, 7)
    assert state["pos"] == (7, 7)

def test_user1_move_command():
    # Arrange
    handler = InputHandler(8, 8)
    # User 1 starting at (0,0)
    
    # Act:
    # First press of "enter" records the soldier location.
    handler.handle_key(1, "enter")
    # Move right to (1,0)
    handler.handle_key(1, "right")
    # Second press of "enter" completes the move command with timestamp=100
    command = handler.handle_key(1, "enter", timestamp=100)
    
    # Assert:
    assert command is not None
    assert command.piece_id == "P1"
    assert command.type == "Move"
    assert command.timestamp == 100
    assert command.params == [(0, 0), (1, 0)]

def test_user2_jump_command():
    # Arrange
    handler = InputHandler(8, 8)
    # User 2 starts at (7,7). First move left to (6,7) for clarity.
    handler.handle_key(2, "a")
    
    # Act:
    # Press selection key ("space") to record soldier at (6,7)
    handler.handle_key(2, "space")
    # Move up to (6,6)
    handler.handle_key(2, "w")
    # Press jump key ("left_shift") to complete jump command with timestamp=200
    command = handler.handle_key(2, "left_shift", timestamp=200)
    
    # Assert:
    assert command is not None
    assert command.piece_id == "P2"
    assert command.type == "Jump"
    assert command.timestamp == 200
    assert command.params == [(6, 7), (6, 6)]

def test_invalid_jump_without_selection():
    # Arrange
    handler = InputHandler(8, 8)
    
    # Act: User 1 presses jump key ("right_shift") without selecting a soldier first.
    command = handler.handle_key(1, "right_shift", timestamp=300)
    
    # Assert: No command should be produced and state remains in "select_soldier" mode.
    assert command is None
    state = handler.get_state(1)
    assert state["mode"] == "select_soldier"

def test_invalid_movement_out_of_bounds():
    # Arrange
    handler = InputHandler(8, 8)
    # User 1 starts at (0,0)
    
    # Act: try to move "up" and "left", which should be ignored.
    handler.handle_key(1, "up")
    handler.handle_key(1, "left")
    state = handler.get_state(1)
    
    # Assert: position remains at (0,0)
    assert state["pos"] == (0, 0)