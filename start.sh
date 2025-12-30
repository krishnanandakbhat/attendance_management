#!/bin/bash

# Attendance Management System - Startup Script
# This script starts the FastAPI server and opens the login page

cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Attendance Management System - Startup${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found.${NC}"
    echo "Please create it first with: python3.11 -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found.${NC}"
    echo "Please create .env file from env.example"
    exit 1
fi

# Check if database exists
if [ ! -f "attendance.db" ]; then
    echo -e "${BLUE}Database not found. Running migrations...${NC}"
    alembic upgrade head
fi

# Save PID to file for later stopping
echo -e "${GREEN}Starting server...${NC}"
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
echo $! > uvicorn.pid

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ps -p $(cat uvicorn.pid) > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server started successfully!${NC}"
    echo -e "${GREEN}✓ PID: $(cat uvicorn.pid)${NC}"
    echo -e "${GREEN}✓ Server running at: http://127.0.0.1:8000${NC}"
    echo -e "${GREEN}✓ Logs available in: server.log${NC}"
    
    # Open browser to login page
    echo -e "${BLUE}Opening login page in browser...${NC}"
    sleep 1
    
    if command -v open &> /dev/null; then
        # macOS
        open http://127.0.0.1:8000/auth/login
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open http://127.0.0.1:8000/auth/login
    else
        echo -e "${BLUE}Please open http://127.0.0.1:8000/auth/login in your browser${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Server is running!${NC}"
    echo -e "${GREEN}To stop: Run ./stop.sh${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}Error: Server failed to start${NC}"
    echo -e "${RED}Check server.log for details${NC}"
    exit 1
fi
