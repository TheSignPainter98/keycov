#!/usr/bin/bash

# Fail on error
set -e

# Parse arguments
version=v0.0.1
for arg in $@; do
	if [[ $arg =~ -V(.+) ]] || [[ "$arg" =~ --version=(.+) ]]; then
		version=${BASH_REMATCH[1]}
	fi
done

# Clean the directory
[[ -f requirements.txt ]] && rm requirements.txt
[[ -f src/version.py ]] && rm src/version.py
[[ -f keycov.zip ]] && rm keycov.zip
rm -rf $(find . -name '__pycache__' -type d)

# Generate the requirements.txt file
pipreqs --force --print >requirements.txt 2>/dev/null

# Generate the version number
sed "s/VERSION/$version/g" < src/version.py.in > src/version.py

# Zip everything up
zip -q -MM keycov.zip keycov.py requirements.txt README.md LICENSE $(find src -type f) $(find keebs/ -type f) $(find kits/ -type f) $(find themes/ -type f)
