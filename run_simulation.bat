@echo off
echo Starting Solar System Simulation...
echo.

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo Using virtual environment: %VIRTUAL_ENV%
) else (
    echo No virtual environment detected. Consider using poetry or venv.
)

echo.
python run_simulation.py
pause
