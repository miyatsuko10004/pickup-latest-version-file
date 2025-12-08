@echo off
cd /d %~dp0
call uv run -m src.main %*
pause
