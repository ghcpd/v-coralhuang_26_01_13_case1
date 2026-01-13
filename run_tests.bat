@echo off
echo Running User-Agent tests...
C:/Bug_Bash/26_01_13/grok-fast/.venv/Scripts/python.exe test_simple.py
if %errorlevel% equ 0 (
    echo ✅ All tests passed!
) else (
    echo ❌ Some tests failed.
)
pause