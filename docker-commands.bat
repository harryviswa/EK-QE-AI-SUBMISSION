@echo off
REM NexQA.ai Docker Commands Helper (Windows)
REM Usage: docker-commands.bat [command]

setlocal enabledelayedexpansion

if "%1"=="" (
    echo.
    echo NexQA.ai Docker Commands
    echo =======================
    echo.
    echo Usage: docker-commands.bat [command]
    echo.
    echo Commands:
    echo   start       - Start all services in background
    echo   stop        - Stop all services
    echo   restart     - Restart all services
    echo   logs        - View logs from all services
    echo   status      - Show status of all services
    echo   models      - List Ollama models
    echo   pull-model  - Pull a new Ollama model (usage: docker-commands.bat pull-model llama3.2:3b^)
    echo   clean       - Remove all containers and volumes (WARNING: deletes data!^)
    echo   rebuild     - Rebuild images without cache
    echo   prod        - Start production services
    echo   health      - Check health of services
    echo.
    exit /b 0
)

if "%1"=="start" (
    echo Starting services...
    docker compose up -d
    echo.
    echo Services started!
    echo Frontend: http://localhost:3000
    echo Backend: http://localhost:5000/api/health
    echo Ollama: http://localhost:11434/api/tags
    exit /b 0
)

if "%1"=="stop" (
    echo Stopping services...
    docker compose down
    echo Services stopped
    exit /b 0
)

if "%1"=="restart" (
    echo Restarting services...
    docker compose restart
    echo Services restarted
    exit /b 0
)

if "%1"=="logs" (
    docker compose logs -f
    exit /b 0
)

if "%1"=="status" (
    echo Service Status:
    docker compose ps
    exit /b 0
)

if "%1"=="models" (
    echo Ollama models:
    docker compose exec ollama ollama list
    exit /b 0
)

if "%1"=="pull-model" (
    if "%2"=="" (
        echo Usage: docker-commands.bat pull-model ^<model_name^>
        echo Examples:
        echo   docker-commands.bat pull-model llama3.2:3b
        echo   docker-commands.bat pull-model mistral:7b
    ) else (
        echo Pulling model: %2
        docker compose exec ollama ollama pull %2
        echo Model pulled
    )
    exit /b 0
)

if "%1"=="clean" (
    echo.
    echo WARNING: This will delete all data (documents, models, vector database^)!
    echo.
    set /p confirm="Are you sure? Type 'yes' to confirm: "
    if /i "!confirm!"=="yes" (
        echo Removing containers and volumes...
        docker compose down -v
        docker volume prune -f
        echo Cleaned
    ) else (
        echo Cancelled
    )
    exit /b 0
)

if "%1"=="rebuild" (
    echo Rebuilding images...
    docker compose build --no-cache
    echo Images rebuilt
    echo Run 'docker-commands.bat start' to start services
    exit /b 0
)

if "%1"=="prod" (
    echo Starting production services...
    docker compose -f docker-compose.prod.yaml up -d
    echo.
    echo Production services started!
    echo Frontend: http://localhost:3000
    echo Backend: http://localhost:5000/api/health
    exit /b 0
)

if "%1"=="health" (
    echo Checking service health...
    echo.
    echo Backend:
    docker compose exec backend curl http://localhost:5000/api/health
    echo.
    echo Ollama:
    docker compose exec ollama curl http://localhost:11434/api/tags
    exit /b 0
)

echo Unknown command: %1
docker-commands.bat
