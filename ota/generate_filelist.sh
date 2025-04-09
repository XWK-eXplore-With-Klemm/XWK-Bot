#!/bin/bash

# Script to generate a JSON file list with file sizes and MD5 hashes for OTA update
# Usage: ./ota/generate_filelist.sh

# Files to exclude from OTA update
BLACKLIST=(
    "config.ini"                # Don't overwrite user WiFi credentials
    "config_proto_white.ini"    # Only for prototype
    ".cursorrules"              # Cursor rules
    "pymakr.conf"               # Pymakr config

    # Example programs which the users should write themself:
    "linefollower.py"
    "uss_bot.py"
    "uss_write.py"
)

# Create file list in JSON format
echo '{' > ota/filelist.json
echo '    "files": {' >> ota/filelist.json

# Find all files in micropython directory
find micropython -type f | while read file; do
    # Check if file is blacklisted
    skip=false
    for pattern in "${BLACKLIST[@]}"; do
        if [[ "$file" == *"$pattern" ]]; then
            skip=true
            break
        fi
    done
    if [ "$skip" = true ]; then
        continue
    fi
    
    # Get file size
    size=$(stat -c %s "$file")
    
    # Get MD5 hash
    hash=$(md5sum "$file" | cut -d' ' -f1)
    
    # Get relative path
    rel_path=${file#micropython/}
    
    # Add to JSON
    echo "        \"$rel_path\": {" >> ota/filelist.json
    echo "            \"size\": $size," >> ota/filelist.json
    echo "            \"hash\": \"$hash\"" >> ota/filelist.json
    echo "        }," >> ota/filelist.json
done

# Remove last comma and close JSON
sed -i '$ s/,$//' ota/filelist.json
echo '    }' >> ota/filelist.json
echo '}' >> ota/filelist.json

echo "File list generated: ota/filelist.json" 