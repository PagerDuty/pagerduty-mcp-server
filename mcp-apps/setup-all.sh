#!/bin/bash

# Setup script for all three MCP Apps

set -e

echo "🚀 Setting up PagerDuty MCP Apps..."
echo ""

APPS=("incident-command-center" "oncall-schedule-visualizer" "service-health-matrix")
PORTS=("3001" "3002" "3003")

# Install dependencies
echo "📦 Installing dependencies..."
for app in "${APPS[@]}"; do
  echo "  Installing $app..."
  (cd "$app" && npm install > /dev/null 2>&1)
done

echo "✅ Dependencies installed"
echo ""

# Build apps
echo "🔨 Building apps..."
for app in "${APPS[@]}"; do
  echo "  Building $app..."
  (cd "$app" && npm run build > /dev/null 2>&1)
done

echo "✅ All apps built successfully"
echo ""

# Summary
echo "🎉 Setup complete!"
echo ""
echo "Apps ready:"
for i in "${!APPS[@]}"; do
  echo "  ${APPS[$i]}: http://localhost:${PORTS[$i]}/mcp"
done

echo ""
echo "To start all apps:"
echo ""
echo "# Terminal 1:"
echo "cd incident-command-center && npm start"
echo ""
echo "# Terminal 2:"
echo "cd oncall-schedule-visualizer && npm start"
echo ""
echo "# Terminal 3:"
echo "cd service-health-matrix && npm start"
echo ""
echo "Or use the start-all.sh script (requires tmux)"
