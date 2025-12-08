import pytest
import re
import os
from src.cleanup import group_and_identify_old_for_pattern, move_files_to_old

# --- Tests for group_and_identify_old_for_pattern ---

@pytest.mark.parametrize("filenames, pattern_str, expected_move, expected_processed", [
    # Scenario 1: Semantic Versioning
    (
        ["file_v1.0.0.txt", "file_v1.1.0.txt", "file_v0.9.0.txt", "other.txt"],
        r'[_-]v?(\d+\.\d+[\.\d]*)',
        ["file_v1.0.0.txt", "file_v0.9.0.txt"],
        ["file_v1.0.0.txt", "file_v1.1.0.txt", "file_v0.9.0.txt"]
    ),
    # Scenario 2: Date-based Versioning
    (
        ["report_20250101.pdf", "report_20241231.pdf", "report.pdf"],
        r'[_-](\d{8,})',
        ["report_20241231.pdf"],
        ["report_20250101.pdf", "report_20241231.pdf"]
    ),
    # Scenario 3: Simple Integer Versioning
    (
        ["data_v1.csv", "data_v10.csv", "data_v2.csv"],
        r'[_-]v?(\d+)',
        ["data_v2.csv", "data_v1.csv"],
        ["data_v1.csv", "data_v10.csv", "data_v2.csv"]
    ),
    # Scenario 4: No matches
    (
        ["file.txt", "document.pdf"],
        r'[_-]v?(\d+)',
        [],
        []
    ),
    # Scenario 5: Multiple groups, one match
    (
        ["data_v1.csv", "log_v2.txt", "data_v3.csv"],
        r'[_-]v?(\d+)',
        ["data_v1.csv"],
        ["data_v1.csv", "log_v2.txt", "data_v3.csv"]
    ),
    # Scenario 6: Files with multiple version-like numbers
    (
        ["file_2023_v1.txt", "file_2023_v2.txt", "file_2024_v1.txt"],
        r'[_-]v?(\d+)', # Matches the last number
        ["file_2023_v1.txt"], # file_2023_v2 is latest for file_2023 group
        ["file_2023_v1.txt", "file_2023_v2.txt", "file_2024_v1.txt"]
    )
])
def test_group_and_identify_old_for_pattern(filenames, pattern_str, expected_move, expected_processed):
    pattern = re.compile(pattern_str)
    files_to_move, processed_files = group_and_identify_old_for_pattern(filenames, pattern)
    
    assert sorted(files_to_move) == sorted(expected_move)
    assert sorted(processed_files) == sorted(expected_processed)

# --- Tests for move_files_to_old (still valid) ---

def test_move_old_files(tmp_path):
    # Setup
    d = tmp_path / "data"
    d.mkdir()
    
    files = {
        "file_v1.txt": "content",
        "file_v2.txt": "content" # Latest
    }
    
    for name, content in files.items():
        (d / name).write_text(content)
        
    # Action
    move_targets = ["file_v1.txt"]
    move_files_to_old(str(d), move_targets)
    
    # Verify
    assert (d / "file_v2.txt").exists()
    assert not (d / "file_v1.txt").exists()
    
    old_dir = d / "old"
    assert old_dir.exists()
    assert (old_dir / "file_v1.txt").exists()

def test_move_old_files_with_directory(tmp_path):
    # Setup
    d = tmp_path / "data"
    d.mkdir()
    (d / "file.txt").write_text("content")
    (d / "subdir").mkdir()
    
    # Action
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
    move_files_to_old(str(d), [])
    
    # Verify
    assert (d / "file.txt").exists()
    assert not (d / "old").exists()