#!/bin/bash

# Docker management script for Flask backend

case "$1" in
    build)
        echo "Building Docker image..."
        docker build -t flask-backend .
        ;;
    
    run)
        echo "Running Flask backend in Docker container..."
        docker run -d --name flask-backend -p 3000:3000 flask-backend
        echo "Container started. Check logs with: ./docker-manage.sh logs"
        ;;
    
    up)
        echo "Starting Flask backend with docker-compose..."
        docker-compose up -d
        echo "Services started. Check logs with: ./docker-manage.sh logs"
        ;;
    
    down)
        echo "Stopping Flask backend with docker-compose..."
        docker-compose down
        ;;
    
    stop)
        echo "Stopping Docker container..."
        docker stop flask-backend 2>/dev/null || true
        docker rm flask-backend 2>/dev/null || true
        ;;
    
    logs)
        echo "Showing Docker logs..."
        if docker ps | grep -q flask-backend; then
            docker logs -f flask-backend
        else
            docker-compose logs -f
        fi
        ;;
    
    status)
        echo "Checking Docker container status..."
        if docker ps | grep -q flask-backend; then
            echo "Container is RUNNING"
            echo ""
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        elif docker ps -a | grep -q flask-backend; then
            echo "Container exists but is STOPPED"
            docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep flask-backend
        else
            echo "No container found"
        fi
        ;;
    
    exec)
        echo "Opening shell in Docker container..."
        docker exec -it flask-backend /bin/bash
        ;;
    
    test)
        echo "Testing Docker endpoints..."
        echo "1. Home endpoint:"
        curl -s http://localhost:3000/ | python3 -m json.tool
        echo ""
        echo "2. Health check:"
        curl -s http://localhost:3000/api/health | python3 -m json.tool
        echo ""
        echo "3. Test endpoint:"
        curl -s http://localhost:3000/api/test | python3 -m json.tool
        ;;
    
    clean)
        echo "Cleaning up Docker resources..."
        docker stop flask-backend 2>/dev/null || true
        docker rm flask-backend 2>/dev/null || true
        docker rmi flask-backend 2>/dev/null || true
        docker-compose down --rmi all 2>/dev/null || true
        echo "Cleanup completed"
        ;;
    
    help|*)
        echo "Docker Management Script for Flask Backend"
        echo "Usage: $0 {build|run|up|down|stop|logs|status|exec|test|clean|help}"
        echo ""
        echo "Commands:"
        echo "  build   - Build Docker image"
        echo "  run     - Run standalone Docker container"
        echo "  up      - Start with docker-compose (recommended)"
        echo "  down    - Stop with docker-compose"
        echo "  stop    - Stop standalone Docker container"
        echo "  logs    - Show container logs"
        echo "  status  - Check container status"
        echo "  exec    - Open shell in container"
        echo "  test    - Test all endpoints"
        echo "  clean   - Remove all Docker resources"
        echo "  help    - Show this help message"
        exit 1
        ;;
esac