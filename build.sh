#!/bin/bash

# Render Build Script for BRIC Tournament Analysis

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p /tmp/bric_data

# Copy database if exists
if [ -f database.json ]; then
    cp database.json /tmp/bric_data/
fi

if [ -f database.xlsx ]; then
    cp database.xlsx /tmp/bric_data/
fi

echo "✓ Build complete - Ready to start webhook server"
