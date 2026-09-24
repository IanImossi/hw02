@echo off
REM Sets up the HW2 Python environment: uses the existing .venv (creates it if missing),
REM installs requirements.txt, then runs the verify script.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -m venv .venv || python -m venv .venv
)

echo Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo *** Install failed - see errors above. ***
    pause
    exit /b 1
)

echo Registering Jupyter kernel...
".venv\Scripts\python.exe" -m ipykernel install --user --name hw2 --display-name "Python (HW2)"

echo.
echo Verifying...
if exist "verify_setup.py" (
    ".venv\Scripts\python.exe" verify_setup.py
) else (
    ".venv\Scripts\python.exe" "verify_setup (2).py"
)

echo.
pause
