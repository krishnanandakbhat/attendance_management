#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Attendance Management System ===${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo ""
    echo "Please run the first-time setup:"
    echo "1. Open Terminal"
    echo "2. Navigate to: $SCRIPT_DIR"
    echo "3. Run: python3.11 -m venv .venv"
    echo "4. Run: source .venv/bin/activate"
    echo "5. Run: pip install -r requirements.txt"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from template...${NC}"
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${GREEN}.env file created. Please edit it if needed.${NC}"
    else
        echo -e "${RED}Error: env.example not found!${NC}"
        read -p "Press Enter to close..."
        exit 1
    fi
fi

# Check if database exists, if not run migrations
if [ ! -f "attendance.db" ]; then
    echo -e "${YELLOW}Database not found. Running initial setup...${NC}"
    source .venv/bin/activate
    export PYTHONPATH="$SCRIPT_DIR"
    export DATABASE_URL=sqlite+aiosqlite:///./attendance.db
    alembic upgrade head
    echo -e "${GREEN}Database initialized.${NC}"
    echo ""
    echo -e "${YELLOW}You'll need to create an admin user.${NC}"
    echo "After the server starts, open Terminal and run:"
    echo "  cd $SCRIPT_DIR"
    echo "  source .venv/bin/activate"
    echo "  python scripts/create_user.py"
    echo ""
fi

# Check if server is already running
if [ -f "uvicorn.pid" ]; then
    PID=$(cat uvicorn.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Server is already running (PID: $PID)${NC}"
        echo ""
        echo "Opening browser..."
        sleep 1
        open "http://127.0.0.1:8000/auth/login"
        echo ""
        echo -e "${GREEN}Done! You can close this window.${NC}"
        read -p "Press Enter to close..."
        exit 0
    else
        rm uvicorn.pid
    fi
fi

# Activate virtual environment and start server
echo "Starting server..."
source .venv/bin/activate

# Start uvicorn in the background
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
SERVER_PID=$!

# Save PID
echo $SERVER_PID > uvicorn.pid

echo -e "${GREEN}Server started successfully!${NC}"
echo "PID: $SERVER_PID"
echo "Log file: $SCRIPT_DIR/server.log"
echo ""

# Wait a moment for server to start
echo "Waiting for server to initialize..."
sleep 3

# Check if server is actually running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${GREEN}Server is running!${NC}"
    echo ""
    echo "Opening browser..."
    open "http://127.0.0.1:8000/auth/login"
    echo ""
    echo -e "${GREEN}=== Server Started Successfully ===${NC}"
    echo "URL: http://127.0.0.1:8000/auth/login"
    echo ""
    echo "To stop the server, double-click 'Stop Server.command'"
    echo ""
    echo -e "${GREEN}You can close this window now.${NC}"
else
    echo -e "${RED}Error: Server failed to start!${NC}"
    echo "Check server.log for details:"
    tail -20 server.log
    rm -f uvicorn.pid
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Keep window open for a moment
sleep 2
