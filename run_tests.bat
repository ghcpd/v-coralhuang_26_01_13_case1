@echo off
REM Generate (or download) the Intoli-based dataset and run tests.
python scripts\generate_browsers_jsonl.py || (
  echo Data generation failed
  exit /b 1
)
python -m pytest -q
if %ERRORLEVEL% EQU 0 (
  echo.
  echo ✅ All tests passed
) else (
  echo.
  echo ❌ Some tests failed
)
exit /b %ERRORLEVEL%