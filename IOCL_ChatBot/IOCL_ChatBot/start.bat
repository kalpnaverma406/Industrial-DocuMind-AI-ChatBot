@echo off
echo ======================================
echo    IOCL PolicyBot - Starting Up
echo ======================================

:: Check .NET
where dotnet >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: .NET SDK not found.
    echo Download from: https://dotnet.microsoft.com/download
    pause
    exit /b 1
)

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
python -m pip install -r Frontend\requirements.txt -q

echo.
echo Building .NET Backend...
dotnet build Backend\IOCLChatBot\IOCLChatBot.csproj -c Debug --nologo -q

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Backend build failed!
    pause
    exit /b 1
)

echo.
echo Starting .NET Backend on http://localhost:5000 ...
start "IOCL Backend" cmd /k "dotnet run --project Backend\IOCLChatBot\IOCLChatBot.csproj --no-build"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting Streamlit Frontend on http://localhost:8501 ...
start "IOCL Frontend" cmd /k "python -m streamlit run Frontend\app.py --server.port 8501"

echo.
echo ======================================
echo  IOCL PolicyBot is starting!
echo   Frontend: http://localhost:8501
echo   Backend:  http://localhost:5000
echo   API Docs: http://localhost:5000/swagger
echo ======================================
echo.
echo Both services opened in separate windows.
pause
