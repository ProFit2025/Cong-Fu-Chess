import tempfile
import pathlib
import shutil
import time
from app.Graphics import Graphics

class DummyImg:
    """Dummy Img class for testing."""
    def __init__(self, name=None):
        self.name = name
    def read(self, path, size):
        return DummyImg(str(path))
    def __eq__(self, other):
        return isinstance(other, DummyImg) and self.name == other.name
    
def create_dummy_png(path):
    # יוצר קובץ PNG ריק (לא באמת תמונה, רק בשביל הבדיקה)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")

def test_load_frames_from_folder_returns_all_frames(monkeypatch):
    """בודק שגרפיקה נטענת עם כל הקבצים מהתיקיה (לפי סדר שמות)."""
    # Arrange
    tmpdir = tempfile.mkdtemp()
    p1 = pathlib.Path(tmpdir) / "a.png"
    p2 = pathlib.Path(tmpdir) / "b.png"
    create_dummy_png(p1)
    create_dummy_png(p2)
    # מחליף את Img ב-DummyImg
    monkeypatch.setattr("app.Graphics.Img", DummyImg)
    # Act
    gfx = Graphics(pathlib.Path(tmpdir), (32, 32))
    # Assert
    assert len(gfx.frames) == 2
    assert gfx.frames[0].name.endswith("a.png")
    assert gfx.frames[1].name.endswith("b.png")
    shutil.rmtree(tmpdir)

def test_no_frames_when_folder_empty(monkeypatch):
    """בודק שכשאין קבצים בתיקיה, frames ריק."""
    # Arrange
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr("app.Graphics.Img", DummyImg)
    # Act
    gfx = Graphics(pathlib.Path(tmpdir), (32, 32))
    # Assert
    assert gfx.frames == []
    assert gfx.img is None
    shutil.rmtree(tmpdir)

def test_update_does_not_crash_on_no_frames(monkeypatch):
    """בודק ש-update לא זורק חריגה כשאין frames."""
    # Arrange
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr("app.Graphics.Img", DummyImg)
    gfx = Graphics(pathlib.Path(tmpdir), (32, 32))
    # Act + Assert
    try:
        gfx.update(1000)
    except Exception:
        assert False, "update should not raise when no frames"
    shutil.rmtree(tmpdir)

def test_animation_loops_when_loop_true(monkeypatch):
    """בודק שהאנימציה חוזרת להתחלה אם loop=True."""
    # Arrange
    tmpdir = tempfile.mkdtemp()
    p1 = pathlib.Path(tmpdir) / "a.png"
    p2 = pathlib.Path(tmpdir) / "b.png"
    create_dummy_png(p1)
    create_dummy_png(p2)
    monkeypatch.setattr("app.Graphics.Img", DummyImg)
    gfx = Graphics(pathlib.Path(tmpdir), (32, 32), loop=True, fps=1)
    # Act
    gfx.last_update_ms = 0
    gfx.update(1000)  # first frame
    gfx.update(2000)  # second frame
    gfx.update(3000)  # should loop to first
    # Assert
    assert gfx.current_frame_idx == 0
    shutil.rmtree(tmpdir)

def test_animation_stops_on_last_frame_when_loop_false(monkeypatch):
    """בודק שהאנימציה נעצרת על הפריים האחרון אם loop=False."""
    # Arrange
    tmpdir = tempfile.mkdtemp()
    p1 = pathlib.Path(tmpdir) / "a.png"
    p2 = pathlib.Path(tmpdir) / "b.png"
    create_dummy_png(p1)
    create_dummy_png(p2)
    monkeypatch.setattr("app.Graphics.Img", DummyImg)
    gfx = Graphics(pathlib.Path(tmpdir), (32, 32), loop=False, fps=1)
    # Act
    gfx.last_update_ms = 0
    gfx.update(1000)  # first frame
    gfx.update(2000)  # second frame
    gfx.update(3000)  # should stay on last
    # Assert
    assert gfx.current_frame_idx == 1
    shutil.rmtree(tmpdir)

def test_reset_sets_first_frame(monkeypatch):
    """בודק ש-reset מחזיר את האנימציה לפריים הראשון."""
    # Arrange
    tmpdir = tempfile.mkdtemp()
    p1 = pathlib.Path(tmpdir) / "a.png"
    p2 = pathlib.Path(tmpdir) / "b.png"
    create_dummy_png(p1)
    create_dummy_png(p2)
    monkeypatch.setattr("app.Graphics.Img", DummyImg)
    gfx = Graphics(pathlib.Path(tmpdir), (32, 32))
    gfx.current_frame_idx = 1
    # Act
    gfx.reset(None)
    # Assert
    assert gfx.current_frame_idx == 0
    assert gfx.img == gfx.frames[0]
    shutil.rmtree(tmpdir)