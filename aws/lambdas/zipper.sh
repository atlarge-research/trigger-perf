#!/bin/bash

dir_path="$(dirname "$(realpath "$0")")"

cd "$dir_path" || exit

for file in *.py; do
    zip_file_name="${file%.py}.zip"
    zip -r "$zip_file_name" "$file"
done

echo "Zip files created!"