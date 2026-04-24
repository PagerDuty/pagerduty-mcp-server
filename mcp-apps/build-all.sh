#!/bin/bash
set -e

echo "🔨 Building all MCP apps..."
echo ""

echo "📦 Building Incident Command Center..."
cd incident-command-center && npm run build && cd ..
cp incident-command-center/dist/mcp-app.html ../pagerduty_mcp/incident_command_center_view.html

echo "📦 Building Service Dependency Graph..."
cd service-dependency-graph && npm run build && cd ..
cp service-dependency-graph/dist/mcp-app.html ../pagerduty_mcp/service_dependency_graph_view.html

echo "📦 Building Oncall Compensation..."
cd oncall-compensation && npm run build && cd ..
cp oncall-compensation/dist/mcp-app.html ../pagerduty_mcp/oncall_compensation_view.html

echo "📦 Building Operations Intelligence..."
cd operations-intelligence && npm run build && cd ..
cp operations-intelligence/dist/mcp-app.html ../pagerduty_mcp/operations_intelligence_view.html

echo "📦 Building Oncall Manager..."
cd oncall-manager && npm run build && cd ..
cp oncall-manager/dist/mcp-app.html ../pagerduty_mcp/oncall_manager_view.html

echo ""
echo "✅ All apps built and copied successfully!"
echo ""
echo "Next steps:"
echo "  1. cd .. && uv run pagerduty-mcp --enable-write-tools"
echo "  2. In VS Code Claude Code: 'Show me the incident command center'"
