import pytest
from src.cleanup import parse_filename, identify_old_versions_to_move

@pytest.mark.parametrize("filename, expected", [
    ("file.txt", ("file", None, ".txt")),
    ("file_v1.txt", ("file", 1, ".txt")),
    ("file_v02.txt", ("file", 2, ".txt")),
    ("report_20251114.pdf", ("report", 20251114, ".pdf")),
    ("data_v1_backup.csv", ("data_v1_backup", None, ".csv")), # Ambiguous case, treat as base? Or handle complex suffixes?
    # Based on user image: "100_標準NB用資料..._①20251114173411_...v2.pptx"
    # This is complex. Let's start simple and refine.
    # The user said "same file but different version name".
    # Let's assume the "version" is at the end of the stem.
])
def test_parse_filename_simple(filename, expected):
    assert parse_filename(filename) == expected

def test_determine_latest_simple():
    files = [
        "file.txt",
        "file_v1.txt",
        "file_v2.txt",
        "other.txt"
    ]
    # Expected: file_v2.txt is latest for "file", other.txt is latest for "other"
    # The function returns a list of filenames to MOVE (old versions).
    # file.txt has no version, so it is ignored (kept).
    # file_v2.txt is latest version, so it is kept.
    # file_v1.txt is old version, so it is moved.
    expected_move = {"file_v1.txt"}
    assert set(identify_old_versions_to_move(files)) == expected_move

def test_determine_latest_timestamp():
    files = [
        "report_20240101.pdf",
        "report_20250101.pdf",
        "report.pdf"
    ]
    # report_20250101.pdf is latest.
    # report.pdf is treated as base (no version), so it might be considered a separate group or the "base" version.
    # Based on current implementation of identify_old_versions_to_move:
    # parse_filename("report.pdf") -> ("report", None, ".pdf") -> version is None -> ignored (kept)
    # parse_filename("report_20240101.pdf") -> ("report", 20240101, ".pdf")
    # parse_filename("report_20250101.pdf") -> ("report", 20250101, ".pdf")
    # So "report.pdf" is ignored.
    # Between 20240101 and 20250101, 20250101 is latest.
    # So 20240101 should be moved.
    expected_move = {"report_20240101.pdf"}
    assert set(identify_old_versions_to_move(files)) == expected_move

from src.cleanup import move_files_to_old
import os

def test_move_old_files(tmp_path):
    # Setup
    d = tmp_path / "data"
    d.mkdir()
    
    files = {
        "file.txt": "content",
        "file_v1.txt": "content",
        "file_v2.txt": "content" # Latest
    }
    
    for name, content in files.items():
        (d / name).write_text(content)
        
    # Action
    # We want to keep file_v2.txt, move others to old/
    # move_files_to_old accepts files to MOVE.
    move_targets = ["file.txt", "file_v1.txt"]
    move_files_to_old(str(d), move_targets)
    
    # Verify
    assert (d / "file_v2.txt").exists()
    assert not (d / "file.txt").exists()
    assert not (d / "file_v1.txt").exists()
    
    old_dir = d / "old"
    assert old_dir.exists()
    assert (old_dir / "file.txt").exists()
    assert (old_dir / "file_v1.txt").exists()



def test_move_old_files_with_directory(tmp_path):
    # Setup
    d = tmp_path / "data"
    d.mkdir()
    (d / "file.txt").write_text("content")
    (d / "subdir").mkdir()
    
    # Action
    # Pass explicit list to move
    move_files_to_old(str(d), ["file.txt"])
    
    # Verify
    assert (d / "subdir").exists() # Should not be moved
    assert (d / "old" / "file.txt").exists() # Should be moved

def test_move_old_files_keep_set(tmp_path):
    # Setup
    d = tmp_path / "data"
    d.mkdir()
    (d / "file.txt").write_text("content")
    
    # Action
    # Pass empty list -> nothing moved
    move_files_to_old(str(d), [])
    
    # Verify
    assert (d / "file.txt").exists()
    assert not (d / "old").exists()

