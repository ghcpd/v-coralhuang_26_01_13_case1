@echo off
REM Run unit tests (Windows)
python -m unittest discover -v tests
if ERRORLEVEL 1 (
  echo Some tests failed.
  exit /b 1
)

echo.
echo Dataset statistics (summary):
python -c "from utils import load; from fake import UserAgent; data = load(); print(f'UA count: {len(data)}'); ua = UserAgent(); samples = [ua.random for _ in range(1000)]; unique = len(set(samples)); print(f'Generated 1000 samples — unique: {unique}, repetition_rate: {(1000-unique)/1000:.3f}')"

echo.
echo To update the dataset from Intoli run:
echo   python data/update_from_intoli.py
exit /b 0
