#!/bin/bash

echo "Testing Docker setup for Flask Backend"
echo "======================================"

# Test 1: Check if Dockerfile exists
echo "1. Checking Dockerfile..."
if [ -f "Dockerfile" ]; then
    echo "   ✓ Dockerfile exists"
else
    echo "   ✗ Dockerfile missing"
    exit 1
fi

# Test 2: Check if docker-compose.yml exists
echo "2. Checking docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    echo "   ✓ docker-compose.yml exists"
else
    echo "   ✗ docker-compose.yml missing"
    exit —1
fi

# Test 3: Check if requirements.txt exists
echo "3. Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "   ✓ requirements.txt exists"
    echo "   Dependencies:"
    cat requirements.txt
else
    echo "   ✗ requirements.txt missing"
    exit 1
fi

# Test 4: Check if app.py exists
echo "4. Checking app.py..."
if [ -f "app.py" ]; then
    echo "   ✓ app.py exists"
else
    echo "   ✗ app.py missing"
    exit 1
fi

# Test 5: Validate Dockerfile syntax
echo "5. Validating Dockerfile syntax..."
if grep -q "FROM python:" Dockerfile; then
    echo "   ✓ Dockerfile uses Python base image"
else
    echo "   ✗ Dockerfile doesn't use Python base image"
fi

if grep -q "EXPOSE 3000" Dockerfile; then
    echo "   ✓ Dockerfile exposes port 3000"
else
    echo "   ✗ Dockerfile doesn't expose port 3000"
fi

if grep -q "gunicorn" Dockerfile; then
    echo "   ✓ Dockerfile uses gunicorn"
else
    echo "   ✗ Dockerfile doesn't use gunicorn"
fi

# Test 6: Check docker-manage.sh
echo "6. Checking docker-manage.sh..."
if [ -f "docker-manage.sh" ]; then
    echo "   ✓ docker-manage.sh exists"
    chmod +x docker-manage.sh
    echo "   Script is executable"
else
    echo "   ✗ docker-manage.sh missing"
fi

# Test 7: Check README for Docker instructions
echo "7. Checking README.md for Docker instructions..."
if grep -q "Docker" README.md; then
    echo "   ✓ README.md mentions Docker"
else
    echo "   ✗ README.md doesn't mention Docker"
fi

echo ""
echo "======================================"
echo "Docker setup validation complete!"
echo ""
echo "Next steps:"
echo "1. Run './docker-manage.sh build' to build Docker image"
echo "2. Run './docker-manage.sh up' to start with docker-compose"
echo "3. Run './docker-manage.sh test' to test endpoints"
echo ""
echo "Or use simple commands:"
echo "  docker-compose up -d"
echo "  curl http://localhost:3000/"