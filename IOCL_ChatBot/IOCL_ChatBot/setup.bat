@echo off
echo ============================================
echo    IOCL ChatBot - Setup and Start
echo ============================================

:: Go to project root
cd /d C:\Users\hp\Downloads\IOCL_ChatBot\IOCL_ChatBot

echo.
echo [1/5] Installing all required packages...
pip install uvicorn fastapi python-dotenv langchain==0.1.20 langchain-community==0.0.38 chromadb==0.4.24 sentence-transformers pypdf requests streamlit --quiet --timeout 120
echo Packages installed!

echo.
echo [2/5] Starting RAG Service on port 8000...
start "IOCL RAG Service" cmd /k "cd /d C:\Users\hp\Downloads\IOCL_ChatBot\IOCL_ChatBot\RAG && python rag_service.py"

echo.
echo [3/5] Waiting for RAG to start...
timeout /t 8 /nobreak >nul

echo.
echo [4/5] Starting .NET Backend on port 5000...
start "IOCL Backend" cmd /k "cd /d C:\Users\hp\Downloads\IOCL_ChatBot\IOCL_ChatBot\Backend\IOCLChatBot && dotnet run"

echo.
echo [5/5] Waiting for backend to start...
timeout /t 8 /nobreak >nul

echo.
echo Starting Streamlit Frontend on port 8501...
start "IOCL Frontend" cmd /k "cd /d C:\Users\hp\Downloads\IOCL_ChatBot\IOCL_ChatBot\Frontend && python -m streamlit run app.py"

echo.
echo ============================================
echo  All 3 services are starting!
echo.
echo  Open your browser and go to:
echo  http://localhost:8501
echo ============================================
echo.
pause