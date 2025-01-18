#!/bin/zsh
ROOT_DIR=''
ENTRYPOINT=$ROOT_DIR/...
VENV_PATH=$ROOT_DIR/...

# Execute in root directory
cd $ROOT_DIR

# Activate the virtual environment
. $VENV_PATH

# Execute the script
python $ENTRYPOINT