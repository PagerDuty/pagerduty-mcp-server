#!/bin/bash
set -e

echo "🔨 Building all MCP apps..."
echo ""

# Build each app
echo "📦 Building Incident Command Center..."
cd incident-command-center && npm run build && cd ..

echo "📦 Building On-Call Schedule Visualizer..."
cd oncall-schedule-visualizer && npm run build && cd ..

echo "📦 Building Service Health Matrix..."
cd service-health-matrix && npm run build && cd ..

echo "📦 Building Service Dependency Graph..."
cd service-dependency-graph && npm run build && cd ..

echo "📦 Building Oncall Compensation..."
cd oncall-compensation && npm run build && cd ..

# Copy to Python package
echo ""
echo "📋 Copying HTML to Python package..."
cp incident-command-center/dist/mcp-app.html ../pagerduty_mcp/incident_command_center_view.html
cp oncall-schedule-visualizer/dist/mcp-app.html ../pagerduty_mcp/oncall_schedule_visualizer_view.html
cp service-health-matrix/dist/mcp-app.html ../pagerduty_mcp/service_health_matrix_view.html
cp service-dependency-graph/dist/mcp-app.html ../pagerduty_mcp/service_dependency_graph_view.html
cp oncall-compensation/dist/mcp-app.html ../pagerduty_mcp/oncall_compensation_view.html

echo ""
echo "✅ All apps built and copied successfully!"
echo ""
echo "Next steps:"
echo "  1. cd .. && uv run pagerduty-mcp --enable-write-tools"
echo "  2. In VS Code Claude Code: 'Show me the incident command center'"
