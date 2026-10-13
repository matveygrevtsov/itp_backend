#!/bin/bash

# Simple script to start/stop the Flask backend

case "$1" in
    start)
        echo "Starting Flask backend on port 3000..."
        
        # Kill any existing process on port 3000
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
        
        # Add user Python bin to PATH
        export PATH=$PATH:/Users/matvejgrevcov/Library/Python/3.9/bin
        
        # Run with gunicorn in background
        cd "$(dirname "$0")"
        nohup gunicorn --bind 0.0.0.0:3000 --workers 1 wsgi:app > /tmp/flask_backend.log 2>&1 &
        
        echo "Backend started! PID: $!"
        echo "Check logs: tail -f /tmp/flask_backend.log"
        echo "Test: curl http://localhost:3000/"
        ;;
    
    stop)
        echo "Stopping Flask backend..."
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
        echo "Backend stopped"
        ;;
    
    status)
        echo "Checking backend status..."
        if lsof -ti:3000 > /dev/null 2>&1; then
            echo "Backend is RUNNING on port 3000"
            echo "Processes:"
            ps aux | grep gunicorn | grep -v grep
            echo ""
            echo "Test endpoint:"
            curl -s http://localhost:3000/api/health | python3 -m json.tool
        else
            echo "Backend is NOT running on port 3000"
        fi
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    test)
        echo "Testing backend endpoints..."
        echo "1. Home endpoint:"
        curl -s http://localhost:3000/ | python3 -m json.tool
        echo ""
        echo "2. Health check:"
        curl -s http://localhost:3000/api/health | python3 -m json.tool
        echo ""
        echo "3. Test endpoint:"
        curl -s http://localhost:3000/api/test | python3 -m json.tool
        ;;
    
    logs)
        echo "Showing logs:"
        tail -100 /tmp/flask_backend.log
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|test|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the backend server"
        echo "  stop    - Stop the backend server"
        echo "  restart - Restart the backend server"
        echo "  status  - Check if backend is running"
        echo "  test    - Test all endpoints"
        echo "  logs    - Show server logs"
        exit 1
        ;;
esac