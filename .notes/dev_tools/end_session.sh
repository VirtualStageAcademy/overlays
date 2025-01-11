#!/bin/bash
# End of Session Documentation Update
# ---------------------------------
# This script helps developers document their session changes
# and updates relevant documentation.

# Ensure virtual environment is active
if [ "$VIRTUAL_ENV" = "" ]; then
    source .venv/bin/activate
fi

# Run session finalizer
python .notes/dev_tools/end_session.py

# Print session end message
echo -e "\n👋 Development session documented!" 