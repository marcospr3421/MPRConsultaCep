@echo off
REM MPRConsultaCep Web Application Deployment Script for Windows

echo MPRConsultaCep Web Application Deployment
echo ==========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not available
    echo Please ensure Docker Desktop is running and try again
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Creating .env from template...
    copy ".env.template" ".env"
    echo.
    echo Please edit .env file with your Azure credentials before continuing
    echo Press any key to open .env file in notepad...
    pause >nul
    notepad .env
    echo.
    echo After configuring .env, press any key to continue...
    pause >nul
)

echo Building and starting the application...
docker compose up -d --build

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Application started successfully!
    echo.
    echo Application is running at:
    echo - http://localhost:8080
    echo.
    echo To view logs: docker compose logs -f
    echo To stop: docker compose down
    echo To rebuild: docker compose up -d --build
) else (
    echo.
    echo ERROR: Failed to start application
    echo Check the logs with: docker compose logs
)

echo.
pause
