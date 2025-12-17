#!/bin/bash

set -e

SELF=skaha-carta

TS=$(date)
echo "$TS $SELF START"

if [ "$#" -ne 3 ]; then
    echo "Usage: skaha-carta <root> <folder> <session url>"
    exit 2
fi

ROOT=$1
FOLDER=$2
URL_PREFIX=$3
COMMAND="carta --no_browser --top_level_folder=${ROOT} --enable_scripting --port=6901 --idle_timeout=100000 --debug_no_auth --http_url_prefix=${URL_PREFIX} ${FOLDER}"
echo "root: $ROOT"
echo "folder: $FOLDER"
echo "url_prefix: $URL_PREFIX"
echo "command: ${COMMAND}"
echo "Add --verbosity=5 to the command for more output"
echo ""
eval "${COMMAND}"

# A bit over a day timeout. Disable token authentication.
