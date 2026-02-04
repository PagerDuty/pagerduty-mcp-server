#!/bin/bash

# Start all three MCP Apps in tmux session

SESSION_NAME="mcp-apps"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
  echo "❌ tmux is not installed"
  echo "Install with: brew install tmux"
  echo ""
  echo "Or start apps manually in separate terminals:"
  echo "  Terminal 1: cd incident-command-center && npm start"
  echo "  Terminal 2: cd oncall-schedule-visualizer && npm start"
  echo "  Terminal 3: cd service-health-matrix && npm start"
  exit 1
fi

# Kill existing session if it exists
tmux has-session -t $SESSION_NAME 2>/dev/null && tmux kill-session -t $SESSION_NAME

echo "🚀 Starting all MCP Apps in tmux session: $SESSION_NAME"
echo ""

# Create new session and first window for Incident Command Center
tmux new-session -d -s $SESSION_NAME -n "incident-cc"
tmux send-keys -t $SESSION_NAME:0 "cd incident-command-center && npm start" C-m

# Create window for On-Call Visualizer
tmux new-window -t $SESSION_NAME -n "oncall-viz"
tmux send-keys -t $SESSION_NAME:1 "cd oncall-schedule-visualizer && npm start" C-m

# Create window for Service Health Matrix
tmux new-window -t $SESSION_NAME -n "service-health"
tmux send-keys -t $SESSION_NAME:2 "cd service-health-matrix && npm start" C-m

# Select first window
tmux select-window -t $SESSION_NAME:0

echo "✅ All apps starting..."
echo ""
echo "Apps will be available at:"
echo "  🚨 Incident Command Center:     http://localhost:3001/mcp"
echo "  📅 On-Call Visualizer:          http://localhost:3002/mcp"
echo "  🏥 Service Health Matrix:       http://localhost:3003/mcp"
echo ""
echo "To attach to tmux session:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "To switch between windows in tmux:"
echo "  Ctrl+B then 0, 1, or 2"
echo ""
echo "To detach from tmux:"
echo "  Ctrl+B then D"
echo ""
echo "To kill all apps:"
echo "  tmux kill-session -t $SESSION_NAME"
echo ""

# Attach to session
tmux attach -t $SESSION_NAME
