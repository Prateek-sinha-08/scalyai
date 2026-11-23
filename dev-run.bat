@echo off
setlocal EnableExtensions

:: Always run from the folder that contains this script (repo root)
cd /d "%~dp0"

:: 1. Check prerequisites (python, node, docker)
where python >nul 2>&1 || (echo ERROR: Python not found & exit /b 1)
where node >nul 2>&1   || (echo ERROR: Node.js not found & exit /b 1)
where docker >nul 2>&1 || (echo ERROR: Docker not found & exit /b 1)

:: 2. Start infrastructure first (Redis & Postgres)
echo Starting Docker services...
docker compose up -d || (echo ERROR: Docker Compose failed & exit /b 1)

set "SERVER_DIR=%~dp0server"
set "FRONTEND_DIR=%~dp0frontend"
set "VENV_PY=%SERVER_DIR%\.venv\Scripts\python.exe"

:: 3. Setup Python venv + install deps if needed
if not exist "%VENV_PY%" (
    echo Creating Python virtual environment...
    pushd "%SERVER_DIR%"
    python -m venv .venv || (echo ERROR: venv creation failed & popd & exit /b 1)
    call .venv\Scripts\python.exe -m ensurepip --upgrade >nul 2>&1
    popd
)

if not exist "%VENV_PY%" (
    echo ERROR: Virtual env missing at %SERVER_DIR%\.venv
    exit /b 1
)

echo Installing Python dependencies...
pushd "%SERVER_DIR%"
"%VENV_PY%" -m pip --version >nul 2>&1 || "%VENV_PY%" -m ensurepip --upgrade
"%VENV_PY%" -m pip install -e .
if errorlevel 1 (
    echo ERROR: pip install failed
    popd
    exit /b 1
)
popd

:: 4. Install frontend deps if needed
if not exist "%FRONTEND_DIR%\node_modules" (
    echo Installing frontend dependencies...
    pushd "%FRONTEND_DIR%"
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        popd
        exit /b 1
    )
    popd
)

:: 5. Check .env files
if not exist "%SERVER_DIR%\.env" (echo WARNING: server\.env is missing!)
if not exist "%FRONTEND_DIR%\.env" (echo WARNING: frontend\.env is missing!)

:: 6. Brief pause for Docker
timeout /t 3 /nobreak >nul

:: 7. Launch dev processes (paths anchored to repo root)
start "Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"
start "Backend" cmd /k "cd /d "%SERVER_DIR%\src" && call "%SERVER_DIR%\.venv\Scripts\activate.bat" && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
start "TaskIQ Worker" cmd /k "cd /d "%SERVER_DIR%\src" && call "%SERVER_DIR%\.venv\Scripts\activate.bat" && taskiq worker config.taskiq:broker --reload"

echo Done. Frontend, API, and worker windows should be open.
endlocal