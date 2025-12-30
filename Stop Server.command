#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Stopping Attendance Management System ===${NC}"
echo ""

# Check if PID file exists
if [ ! -f "uvicorn.pid" ]; then
    echo -e "${YELLOW}No PID file found. Checking for running processes...${NC}"
    
    # Try to find and kill any uvicorn processes
    if pkill -f "uvicorn app.main:app"; then
        echo -e "${GREEN}Stopped uvicorn processes.${NC}"
    else
        echo -e "${YELLOW}No running server found.${NC}"
    fi
    echo ""
    read -p "Press Enter to close..."
    exit 0
fi

# Read PID
PID=$(cat uvicorn.pid)

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo "Found server process (PID: $PID)"
    echo "Stopping server..."
    
    # Try graceful shutdown first
    kill $PID
    
    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}Server stopped gracefully.${NC}"
            rm uvicorn.pid
            echo ""
            read -p "Press Enter to close..."
            exit 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    echo -e "${YELLOW}Forcing shutdown...${NC}"
    kill -9 $PID 2>/dev/null
    
    if ! ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}Server stopped.${NC}"
    else
        echo -e "${RED}Failed to stop server. You may need to restart your computer.${NC}"
        echo ""
        read -p "Press Enter to close..."
        exit 1
    fi
else
    echo -e "${YELLOW}Server is not running (stale PID file).${NC}"
fi

# Clean up PID file
rm -f uvicorn.pid

# Also kill any stray uvicorn processes just to be sure
pkill -f "uvicorn app.main:app" 2>/dev/null

echo -e "${GREEN}=== Server Stopped ===${NC}"
echo ""
read -p "Press Enter to close..."
