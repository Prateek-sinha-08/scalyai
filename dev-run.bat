@echo off

:: 1. Check prerequisites (python, node, docker)
where python >nul 2>&1 || (echo ERROR: Python not found & exit /b 1)
where node >nul 2>&1   || (echo ERROR: Node.js not found & exit /b 1)
where docker >nul 2>&1 || (echo ERROR: Docker not found & exit /b 1)

:: 2. Start infrastructure first (Redis & Postgres)
echo Starting Docker services...
docker compose up -d || (echo ERROR: Docker Compose failed & exit /b 1)

:: 3. Setup Python venv + install deps if needed
if not exist "server\.venv\Scripts\activate" (
    echo Creating Python virtual environment...
    cd /d server && python -m venv .venv && cd ..
)
echo Installing Python dependencies...
cd /d server && .venv\Scripts\pip install -e . && cd ..

:: 4. Install frontend deps if needed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd /d frontend && npm install && cd ..
)

:: 5. Check .env files
if not exist "server\.env" (echo WARNING: server\.env is missing!)
if not exist "frontend\.env" (echo WARNING: frontend\.env is missing!)

:: 6. Wait for Docker services to be healthy (optional but nice)
timeout /t 3 /nobreak >nul

:: 7. Now launch everything
start "Frontend" cmd /k "cd /d frontend && npm run dev"
start "Backend"  cmd /k "cd /d server\src && ..\.venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
start "TaskIQ Worker" cmd /k "cd /d server\src && ..\.venv\Scripts\activate && taskiq worker config.taskiq:broker --reload"