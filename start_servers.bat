@echo off
echo Starting Multi-Agent Launch Orchestrator...
echo.

echo [1/3] Setting up backend...
cd backend
call venv\Scripts\activate
echo Starting backend server on http://localhost:8000
start "Backend Server" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] Setting up frontend...
cd ..\frontend
echo Starting frontend server on http://localhost:3000
start "Frontend Server" cmd /k "npm start"

echo [3/3] Setup complete!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
