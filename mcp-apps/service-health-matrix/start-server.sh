#!/bin/bash

# Kill any existing server on port 3003
lsof -ti:3003 | xargs kill -9 2>/dev/null

# Start the server
echo "🏥 Starting Service Health Matrix server on port 3003..."
cd "$(dirname "$0")"
node dist/main.js
