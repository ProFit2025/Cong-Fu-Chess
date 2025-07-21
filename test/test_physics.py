import pytest
from app.Physics import (
    Physics,
    IdlePhysics,
    MovePhysics,
    JumpPhysics,
    LongRestPhysics,
    ShortRestPhysics,
)
from app.Command import Command


class DummyBoard:
    def __init__(self, cell_W_pix=50, cell_H_pix=50):
        self.cell_W_pix = cell_W_pix
        self.cell_H_pix = cell_H_pix


def test_physics_get_pos_returns_pixel_coordinates():
    board = DummyBoard()
    physics = Physics((1, 2), board)
    assert physics.get_pos() == (100.0, 50.0)


def test_idle_physics_flags():
    board = DummyBoard()
    physics = IdlePhysics((0, 0), board)
    assert physics.can_be_captured()
    assert not physics.can_capture()


def test_move_physics_reset_and_move_to_target():
    board = DummyBoard()
    physics = MovePhysics((0, 0), board, speed_m_s=1000)
    cmd = Command(timestamp=0, piece_id="P1", type="Move", params=[None, (2, 2)])
    physics.reset(cmd)
    physics.update(1000)
    assert physics.cell == (2, 2)


def test_move_physics_partial_update_makes_progress():
    board = DummyBoard()
    physics = MovePhysics((0, 0), board, speed_m_s=1.0)
    cmd = Command(timestamp=0, piece_id="P1", type="Move", params=[None, (1, 0)])
    physics.reset(cmd)
    physics.update(0)      # initialize time
    physics.update(500)    # now movement happens
    x, y = physics.get_pos()
    assert 0 < x < board.cell_W_pix


def test_move_physics_reset_with_invalid_params():
    board = DummyBoard()
    physics = MovePhysics((0, 0), board)
    cmd = Command(timestamp=0, piece_id="P1", type="Move", params=[None, 999])
    physics.reset(cmd)
    assert physics.target_cell == (0, 0)


def test_jump_physics_reset_and_update():
    board = DummyBoard()
    physics = JumpPhysics((0, 0), board)
    cmd = Command(timestamp=0, piece_id="P1", type="Jump", params=[None, (1, 1)])
    physics.reset(cmd)
    physics.update(100)
    assert physics.cell == (1, 1)


def test_long_rest_physics_flags():
    board = DummyBoard()
    physics = LongRestPhysics((0, 0), board)
    assert not physics.can_be_captured()
    assert not physics.can_capture()


def test_short_rest_physics_flags():
    board = DummyBoard()
    physics = ShortRestPhysics((0, 0), board)
    assert physics.can_be_captured()
    assert not physics.can_capture()
