@echo off
python -m pytest -q
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
python scripts\run_stats.py
