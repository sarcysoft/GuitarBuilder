#!/bin/bash

# Determine directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default to false
NO_CUT_ARG=""

# Check arguments passed to this script
for arg in "$@"; do
    if [ "$arg" == "--no-cut" ] || [ "$arg" == "--no_cut" ] || [ "$arg" == "no_cut" ]; then
        NO_CUT_ARG="--no-cut"
    fi
done

if [ -n "$NO_CUT_ARG" ]; then
    echo "Running setup_scene.py with --no-cut (no cuts, exporting full body)..."
    blender --background --python "$SCRIPT_DIR/setup_scene.py" -- --no-cut
else
    echo "Running setup_scene.py (performing cuts and exporting all parts)..."
    blender --background --python "$SCRIPT_DIR/setup_scene.py"
fi
