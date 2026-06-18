#!/bin/bash

# Determine directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

NO_CUT_ARG=""
CONFIG_ARG=""
EXPORT_CONFIG_FLAG=""
EXPORT_VAL_ARG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-cut|--no_cut|no_cut)
            NO_CUT_ARG="--no-cut"
            shift
            ;;
        --export-config|--export_config)
            EXPORT_CONFIG_FLAG="1"
            if [[ -n "$2" && "$2" != -* ]]; then
                EXPORT_VAL_ARG="$2"
                shift 2
            else
                shift
            fi
            ;;
        --config)
            CONFIG_ARG="$2"
            shift 2
            ;;
        *)
            CONFIG_ARG="$1"
            shift
            ;;
    esac
done

if [ -n "$EXPORT_CONFIG_FLAG" ]; then
    echo "Exporting guitar model configuration..."
    CMD_ARGS=""
    if [ -n "$CONFIG_ARG" ]; then
        CMD_ARGS="--config $CONFIG_ARG"
    fi
    if [ -n "$EXPORT_VAL_ARG" ]; then
        CMD_ARGS="$CMD_ARGS --export-config $EXPORT_VAL_ARG"
    else
        CMD_ARGS="$CMD_ARGS --export-config"
    fi
    python "$SCRIPT_DIR/configure_guitar.py" $CMD_ARGS
    exit 0
fi

if [ -n "$CONFIG_ARG" ]; then
    echo "Generating guitar model for config: $CONFIG_ARG..."
    python "$SCRIPT_DIR/configure_guitar.py" --config "$CONFIG_ARG" --generate
    
    if [ -n "$NO_CUT_ARG" ]; then
        echo "Running setup_scene.py with --no-cut and --config $CONFIG_ARG..."
        blender --background --python "$SCRIPT_DIR/setup_scene.py" -- --no-cut --config "$CONFIG_ARG"
    else
        echo "Running setup_scene.py with --config $CONFIG_ARG..."
        blender --background --python "$SCRIPT_DIR/setup_scene.py" -- --config "$CONFIG_ARG"
    fi
else
    if [ -n "$NO_CUT_ARG" ]; then
        echo "Running setup_scene.py with --no-cut..."
        blender --background --python "$SCRIPT_DIR/setup_scene.py" -- --no-cut
    else
        echo "Running setup_scene.py..."
        blender --background --python "$SCRIPT_DIR/setup_scene.py"
    fi
fi


