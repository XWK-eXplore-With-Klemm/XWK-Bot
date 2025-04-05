#!/bin/bash

# Script to generate OTA file list and upload files to server
# Usage: ./ota/ota.sh

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Generate file list first
echo "Generating project file list with file sizes and md5 hashes..."
"$SCRIPT_DIR/generate_filelist.sh"
echo

# Upload files to server
echo "Uploading files to server..."
rsync -e "ssh -p 222" -avz --delete micropython/ xwk@bigfish.ull.at:/home/xwk/public_html/projects/xwk-bot/micropython/
echo

# Upload filelist.json
echo "Uploading filelist.json..."
rsync -avz -e "ssh -p 222" "$SCRIPT_DIR/filelist.json" xwk@bigfish.ull.at:/home/xwk/public_html/projects/xwk-bot/
echo

echo "OTA update files uploaded successfully!" 
echo 