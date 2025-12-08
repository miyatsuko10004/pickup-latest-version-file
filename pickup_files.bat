@echo off
cd /d %~dp0
call uv run src/main.py %*
pause
