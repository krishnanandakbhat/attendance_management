#!/bin/bash

# Attendance Management System - Stop Script
# This script stops the FastAPI server

cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Attendance Management System - Shutdown${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if PID file exists
if [ ! -f "uvicorn.pid" ]; then
    echo -e "${YELLOW}Warning: PID file not found.${NC}"
    echo -e "${YELLOW}Attempting to stop all uvicorn processes...${NC}"
    pkill -f "uvicorn app.main:app"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Server processes stopped${NC}"
    else
        echo -e "${RED}No running server found${NC}"
    fi
    exit 0
fi

# Read PID from file
PID=$(cat uvicorn.pid)

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo -e "${BLUE}Found server running with PID: $PID${NC}"
    echo -e "${BLUE}Stopping server...${NC}"
    
    # Try graceful shutdown first
    kill $PID
    
    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            break
        fi
        echo -e "${YELLOW}Waiting for graceful shutdown... ($i/5)${NC}"
        sleep 1
    done
    
    # Force kill if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Forcing shutdown...${NC}"
        kill -9 $PID
        sleep 1
    fi
    
    # Verify stopped
    if ! ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server stopped successfully${NC}"
        rm -f uvicorn.pid
    else
        echo -e "${RED}Error: Could not stop server${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Server not running (stale PID file)${NC}"
    rm -f uvicorn.pid
fi

# Clean up any remaining uvicorn processes
echo -e "${BLUE}Cleaning up any remaining processes...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Server shutdown complete!${NC}"
echo -e "${GREEN}To start again: Run ./start.sh${NC}"
echo -e "${GREEN}========================================${NC}"
