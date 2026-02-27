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

# Find a compatible stable Python version (3.10-3.13)
PYTHON_BIN=""
for ver in python3.13 python3.12 python3.11 python3.10 python3; do
    cmd=$(command -v $ver 2>/dev/null)
    [ -z "$cmd" ] && continue
    # Skip 3.14 due to dependency incompatibilities
    if [[ ! $($cmd --version 2>&1) =~ "3.14" ]]; then
        PYTHON_BIN=$cmd
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}Error: Stable Python version (3.10-3.13) not found. Found: $(python3 --version)${NC}"
    exit 1
fi

# Backend setup
cd "$PROJECT_ROOT/backend" || { echo -e "${RED}Error: backend directory not found${NC}"; exit 1; }

[ -f .env ] || { echo -e "${RED}Error: .env file missing in backend${NC}"; exit 1; }

echo -e "${GREEN}[1/4] Preparing virtual environment...${NC}"
# Recreate venv if missing or if it's using the incompatible 3.14 version
if [ ! -d "venv" ] || [[ $(./venv/bin/python --version 2>&1) =~ "3.14" ]]; then
    [ -d "venv" ] && rm -rf venv
    $PYTHON_BIN -m venv venv
fi
source venv/bin/activate

pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install Python dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}[2/4] Starting Flask backend (port 5001)...${NC}"
python app.py &
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
