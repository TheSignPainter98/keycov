#!/usr/bin/bash

set -e

# Clean the directory
[[ -f requirements.txt ]] && rm requirements.txt
[[ -f keycov.zip ]] && rm keycov.zip
rm -rf $(find . -name '__pycache__' -type d)

# Generate the requirements.txt file
pipreqs --force --print >requirements.txt 2>/dev/null

# Zip everything up
zip -q -MM keycov.zip keycov.py requirements.txt README.md LICENSE $(find src -type f) $(find keebs/ -type f) $(find kits/ -type f) $(find themes/ -type f)
