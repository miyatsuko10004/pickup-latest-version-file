import pytest
from unittest.mock import patch, MagicMock
from src.main import main
import sys
import os

def test_main_dry_run(tmp_path, capsys):
    d = tmp_path / "data"
    d.mkdir()
    (d / "file.txt").write_text("content")
    (d / "file_v1.txt").write_text("content")
    
    with patch.object(sys, 'argv', ['main.py', str(d), '--dry-run']):
        main()
        
    captured = capsys.readouterr()
    assert "--- Dry Run: 以下のファイルが old/ に移動されます ---" in captured.out
    assert "file.txt" in captured.out
    assert "file_v1.txt" not in captured.out # file_v1.txt is latest (v1 > none)

def test_main_execution(tmp_path, capsys):
    d = tmp_path / "data"
    d.mkdir()
    (d / "file.txt").write_text("content")
    (d / "file_v1.txt").write_text("content")
    
    with patch.object(sys, 'argv', ['main.py', str(d)]):
        main()
        
    captured = capsys.readouterr()
    assert "ファイルを整理中..." in captured.out
    assert "完了しました" in captured.out
    
    assert (d / "file_v1.txt").exists()
    assert not (d / "file.txt").exists()
    assert (d / "old" / "file.txt").exists()

def test_main_directory_not_found(capsys):
    with patch.object(sys, 'argv', ['main.py', 'non_existent_dir']):
        main()
        
    captured = capsys.readouterr()
    assert "エラー: ディレクトリが見つかりません" in captured.out

def test_main_block():
    # This is a bit tricky to test directly without running the script.
    # But we can import the module and check if main is called when __name__ is __main__.
    # Alternatively, we can just run the script using subprocess to cover the "if __name__ == '__main__':" block.
    import subprocess
    import sys
    
    # Just run it with --help to ensure it runs
    result = subprocess.run([sys.executable, "src/main.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage:" in result.stdout

