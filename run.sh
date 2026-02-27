#!/bin/bash
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting Illegal Parking Detection Web UI${NC}"
echo -e "${BLUE}========================================${NC}"

# Check and prompt for .env file if it doesn't exist
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    echo -e "${RED}First time setup: GEMINI_API_KEY is required.${NC}"
    echo -e "You can get it from: https://aistudio.google.com/app/apikey"
    read -r -p "Please enter your GEMINI_API_KEY (Google AI Studio): " API_KEY
    if [ -n "$API_KEY" ]; then
        echo "GEMINI_API_KEY=$API_KEY" > "$SCRIPT_DIR/backend/.env"
        echo -e "${GREEN}API key saved to backend/.env!${NC}"
    else
        echo -e "${RED}API key is required to start the application. Exiting...${NC}"
        exit 1
    fi
fi

# Make the internal script executable just in case
chmod +x "$SCRIPT_DIR/scripts/start.sh"

# Attempt to automatically open the browser once started
(sleep 8 && { xdg-open "http://localhost:3000" || open "http://localhost:3000"; } 2>/dev/null) &

# Run the actual startup script
bash "$SCRIPT_DIR/scripts/start.sh"
