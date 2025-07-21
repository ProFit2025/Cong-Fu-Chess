import pathlib
import tempfile
import os
from app.Moves import Moves

def create_moves_file(lines):
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
    tmp.write('\n'.join(lines))
    tmp.close()
    return pathlib.Path(tmp.name)

def test_read_moves_valid_file_returns_correct_moves():
    """בודק שקובץ חוקי נקרא נכון ומחזיר את כל התנועות התקינות."""
    # Arrange
    lines = ["1,0", "-1,0", "0,1", "0,-1"]
    path = create_moves_file(lines)
    dims = (8, 8)
    # Act
    moves = Moves(path, dims)
    # Assert
    assert moves.moves_list == [(1,0), (-1,0), (0,1), (0,-1)]
    os.unlink(path)

def test_read_moves_skips_invalid_lines():
    """בודק ששורות לא חוקיות (טקסט או פורמט שגוי) לא נכנסות לרשימת התנועות."""
    # Arrange
    lines = ["1,0", "bad,line", "2,2", "3"]
    path = create_moves_file(lines)
    dims = (8, 8)
    # Act
    moves = Moves(path, dims)
    # Assert
    assert moves.moves_list == [(1,0), (2,2)]
    os.unlink(path)

def test_get_moves_filters_out_of_bounds_moves():
    """בודק שהתנועות שמחזירה get_moves לא חורגות מגבולות הלוח."""
    # Arrange
    lines = ["1,0", "-1,0", "0,1", "0,-1"]
    path = create_moves_file(lines)
    dims = (2, 2)
    moves = Moves(path, dims)
    # Act
    result = moves.get_moves(0, 0)
    # Assert
    # Only (1,0) and (0,1) are in bounds from (0,0) on 2x2 board
    assert set(result) == {(1,0), (0,1)}
    os.unlink(path)

def test_get_moves_empty_moves_list_returns_empty():
    """בודק שכשאין תנועות בקובץ, get_moves מחזירה רשימה ריקה."""
    # Arrange
    lines = []
    path = create_moves_file(lines)
    dims = (8, 8)
    moves = Moves(path, dims)
    # Act
    result = moves.get_moves(4, 4)
    # Assert
    assert result == []
    os.unlink(path)

def test_get_moves_with_negative_start_position():
    """בודק שקריאה ל-get_moves עם מיקום שלילי מחזירה רשימה ריקה (אין תנועות חוקיות)."""
    # Arrange
    lines = ["1,0", "0,1"]
    path = create_moves_file(lines)
    dims = (8, 8)
    moves = Moves(path, dims)
    # Act
    result = moves.get_moves(-1, -1)
    # Assert
    # All moves will be out of bounds
    assert result == []
    os.unlink(path)

def test_read_moves_skips_comments_and_empty_lines():
    """בודק ששורות ריקות ותגובות (//) לא נכנסות לרשימת התנועות."""
    # Arrange
    lines = ["// comment", "", "1,0", "0,1"]
    path = create_moves_file(lines)
    dims = (8, 8)
    moves = Moves(path, dims)
    # Assert
    assert moves.moves_list == [(1,0), (0,1)]
    os.unlink(path)