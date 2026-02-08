#!/bin/bash
# NexQA.ai Docker Commands Reference

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}NexQA.ai Docker Commands${NC}\n"

# Function to show usage
show_usage() {
    echo "Usage: ./docker-commands.sh [command]"
    echo
    echo "Commands:"
    echo "  start       - Start all services in background"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  logs        - View logs from all services"
    echo "  logs-backend - View backend logs"
    echo "  logs-frontend - View frontend logs"
    echo "  logs-ollama - View Ollama logs"
    echo "  status      - Show status of all services"
    echo "  shell-backend - Open shell in backend container"
    echo "  shell-frontend - Open shell in frontend container"
    echo "  shell-ollama - Open shell in Ollama container"
    echo "  models      - List Ollama models"
    echo "  pull-model  - Pull a new Ollama model"
    echo "  clean       - Remove all containers and volumes (⚠️ deletes data!)"
    echo "  rebuild     - Rebuild images without cache"
    echo "  prod        - Start production services"
    echo
}

# Parse commands
case "$1" in
    start)
        echo -e "${GREEN}Starting services...${NC}"
        docker compose up -d
        echo -e "${GREEN}✓ Services started!${NC}"
        echo "Frontend: http://localhost:3000"
        echo "Backend: http://localhost:5000/api/health"
        echo "Ollama: http://localhost:11434/api/tags"
        ;;
    
    stop)
        echo -e "${YELLOW}Stopping services...${NC}"
        docker compose down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting services...${NC}"
        docker compose restart
        echo -e "${GREEN}✓ Services restarted${NC}"
        ;;
    
    logs)
        docker compose logs -f
        ;;
    
    logs-backend)
        docker compose logs -f backend
        ;;
    
    logs-frontend)
        docker compose logs -f frontend
        ;;
    
    logs-ollama)
        docker compose logs -f ollama
        ;;
    
    status)
        echo -e "${BLUE}Service Status:${NC}"
        docker compose ps
        ;;
    
    shell-backend)
        echo -e "${BLUE}Opening shell in backend...${NC}"
        docker compose exec backend /bin/bash
        ;;
    
    shell-frontend)
        echo -e "${BLUE}Opening shell in frontend...${NC}"
        docker compose exec frontend /bin/sh
        ;;
    
    shell-ollama)
        echo -e "${BLUE}Opening shell in Ollama...${NC}"
        docker compose exec ollama /bin/bash
        ;;
    
    models)
        echo -e "${BLUE}Ollama models:${NC}"
        docker compose exec ollama ollama list
        ;;
    
    pull-model)
        if [ -z "$2" ]; then
            echo "Usage: ./docker-commands.sh pull-model <model_name>"
            echo "Examples:"
            echo "  ./docker-commands.sh pull-model llama3.2:3b"
            echo "  ./docker-commands.sh pull-model mistral:7b"
            echo "  ./docker-commands.sh pull-model nomic-embed-text:latest"
        else
            echo -e "${YELLOW}Pulling model: $2${NC}"
            docker compose exec ollama ollama pull "$2"
            echo -e "${GREEN}✓ Model pulled${NC}"
        fi
        ;;
    
    clean)
        echo -e "${YELLOW}⚠️  WARNING: This will delete all data!${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "Removing containers and volumes..."
            docker compose down -v
            docker volume prune -f
            echo -e "${GREEN}✓ Cleaned${NC}"
        else
            echo "Cancelled"
        fi
        ;;
    
    rebuild)
        echo -e "${YELLOW}Rebuilding images...${NC}"
        docker compose build --no-cache
        echo -e "${GREEN}✓ Images rebuilt${NC}"
        echo "Run './docker-commands.sh start' to start services"
        ;;
    
    prod)
        echo -e "${GREEN}Starting production services...${NC}"
        docker compose -f docker-compose.prod.yaml up -d
        echo -e "${GREEN}✓ Production services started!${NC}"
        echo "Frontend: http://localhost:3000"
        echo "Backend: http://localhost:5000/api/health"
        ;;
    
    *)
        show_usage
        ;;

esac
