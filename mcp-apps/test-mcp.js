#!/usr/bin/env node

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const mcpServer = spawn('/Users/svillanelo/.nvm/versions/node/v22.22.0/bin/node', [
  join(__dirname, 'dist/index.js'),
  '--stdio'
], {
  env: process.env,
  stdio: ['pipe', 'pipe', 'inherit']
});

let responseBuffer = '';

mcpServer.stdout.on('data', (data) => {
  responseBuffer += data.toString();
  
  // Try to parse JSON responses
  const lines = responseBuffer.split('\n');
  responseBuffer = lines.pop() || ''; // Keep incomplete line in buffer
  
  lines.forEach(line => {
    if (line.trim()) {
      try {
        const parsed = JSON.parse(line);
        console.log('=== RESPONSE ===');
        console.log(JSON.stringify(parsed, null, 2));
        console.log('================\n');
      } catch (e) {
        console.log('Raw output:', line);
      }
    }
  });
});

// Send initialize
console.log('Sending initialize...');
mcpServer.stdin.write(JSON.stringify({
  jsonrpc: "2.0",
  id: 1,
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "test-client", version: "1.0" }
  }
}) + '\n');

// Wait a bit then call the dashboard tool
setTimeout(() => {
  console.log('Calling get-incident-dashboard...');
  mcpServer.stdin.write(JSON.stringify({
    jsonrpc: "2.0",
    id: 2,
    method: "tools/call",
    params: {
      name: "get-incident-dashboard",
      arguments: { timeRange: "24h" }
    }
  }) + '\n');
}, 1000);

// Exit after 15 seconds
setTimeout(() => {
  console.log('Timeout - exiting');
  mcpServer.kill();
  process.exit(0);
}, 15000);

mcpServer.on('exit', (code) => {
  console.log(`MCP server exited with code ${code}`);
  process.exit(code || 0);
});
