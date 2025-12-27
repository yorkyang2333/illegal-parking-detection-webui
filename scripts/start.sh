#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Vehicle Parking Violation Detection${NC}"
echo -e "${BLUE}  Starting Application...${NC}"
echo -e "${BLUE}========================================${NC}"

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js not installed${NC}"
    echo -e "${RED}Please install Node.js from https://nodejs.org${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not installed${NC}"
    echo -e "${RED}Please install Python 3 from https://python.org${NC}"
    exit 1
fi

# Backend setup
cd "$PROJECT_ROOT/backend" || { echo -e "${RED}Error: backend directory not found${NC}"; exit 1; }

if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found in backend directory${NC}"
    echo -e "${RED}Please create a .env file with your DASHSCOPE_API_KEY${NC}"
    exit 1
fi

echo -e "${GREEN}[1/4] Installing Python dependencies...${NC}"
pip3 install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install Python dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}[2/4] Starting Flask backend (port 5001)...${NC}"
python3 app.py &
BACKEND_PID=$!
sleep 2
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Backend running (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Failed to start backend${NC}"
    exit 1
fi

# Frontend setup
cd "$PROJECT_ROOT/frontend" || { echo -e "${RED}Error: frontend directory not found${NC}"; kill $BACKEND_PID 2>/dev/null; exit 1; }

echo -e "${GREEN}[3/4] Installing Node.js dependencies...${NC}"
npm install > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install Node.js dependencies${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}[4/4] Starting Vite dev server (port 3000)...${NC}"
npm run dev &
FRONTEND_PID=$!
sleep 3
if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Frontend running (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Failed to start frontend${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Application started successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}Backend:  http://localhost:5001${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all servers${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${BLUE}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait
