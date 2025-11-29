#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Cleaning up old frontend files${NC}"
echo -e "${BLUE}========================================${NC}"

# Create backup directory
BACKUP_DIR="old_frontend_backup_$(date +%Y%m%d_%H%M%S)"

if [ -d "static" ] || [ -d "templates" ]; then
    echo -e "${YELLOW}Found old frontend directories (static/ and/or templates/)${NC}"
    echo -e "${BLUE}Creating backup in: $BACKUP_DIR${NC}"

    mkdir -p "$BACKUP_DIR"

    if [ -d "static" ]; then
        mv static "$BACKUP_DIR/"
        echo -e "${GREEN}✓ Moved static/ to backup${NC}"
    fi

    if [ -d "templates" ]; then
        mv templates "$BACKUP_DIR/"
        echo -e "${GREEN}✓ Moved templates/ to backup${NC}"
    fi

    echo ""
    echo -e "${GREEN}Cleanup complete!${NC}"
    echo -e "${BLUE}Old files backed up to: $BACKUP_DIR${NC}"
    echo -e "${YELLOW}You can safely delete this backup directory if you don't need it.${NC}"
else
    echo -e "${GREEN}No old frontend files found. Directory is clean!${NC}"
fi

echo -e "${BLUE}========================================${NC}"
