#!/bin/bash
# Script to load transcripts into database

echo "Loading transcripts into database..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Run the load script
python3 -m backend.load_transcripts

echo "Done!"

