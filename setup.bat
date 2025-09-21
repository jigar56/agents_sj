@echo off
REM Multi-Agent Launch Orchestrator Setup Script for Windows

echo 🚀 Setting up Multi-Agent Launch Orchestrator...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    exit /b 1
)

echo ✅ Python and Node.js are installed

REM Backend setup
echo 📦 Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo ✅ Backend dependencies installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    copy .env.example .env
    echo 📝 Created .env file. Please add your API keys.
)

cd ..

REM Frontend setup
echo 📦 Setting up frontend...
cd frontend

REM Install dependencies
npm install
echo ✅ Frontend dependencies installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    copy .env.example .env
    echo 📝 Created .env file for frontend.
)

cd ..

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Add your OpenAI API key to backend\.env
echo 2. Start the backend: cd backend ^&^& venv\Scripts\activate ^&^& python -m app.main
echo 3. Start the frontend: cd frontend ^&^& npm start
echo 4. Open http://localhost:3000 in your browser
echo.
echo For Docker deployment: docker-compose up --build
