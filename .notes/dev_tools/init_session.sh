#!/bin/bash
# Development Session Initialization
# --------------------------------
# This script initializes a new development session with proper
# environment setup and documentation validation.

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Initializing development session...${NC}\n"

# Ensure we're in the project root
if [ ! -f ".cursorrules" ]; then
    echo -e "${YELLOW}⚠️  Must be run from project root!${NC}"
    exit 1
fi

# Ensure virtual environment is active
if [ "$VIRTUAL_ENV" = "" ]; then
    echo -e "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Run session initializer
python .notes/dev_tools/session_init.py

# Print session start message
echo -e "\n${GREEN}✨ Development session initialized!${NC}"
echo -e "   - Cursor rules loaded"
echo -e "   - Virtual environment activated"
echo -e "   - Documentation validated"
