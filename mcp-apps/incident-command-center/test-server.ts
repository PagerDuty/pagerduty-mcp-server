/**
 * Development test server for MCP App
 * Run with: npx tsx test-server.ts
 */

import * as http from 'http';
import * as fs from 'fs';
import * as path from 'path';

const PORT = 3030;

const mimeTypes: Record<string, string> = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
};

const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);

  // Serve the test HTML
  if (req.url === '/' || req.url === '/test') {
    const filePath = path.join(__dirname, 'test-mcp-app.html');
    fs.readFile(filePath, (err, content) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading test page');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(content);
    });
    return;
  }

  // Serve the built app
  if (req.url === '/mcp-app.html') {
    const filePath = path.join(__dirname, 'dist', 'mcp-app.html');
    fs.readFile(filePath, (err, content) => {
      if (err) {
        res.writeHead(404);
        res.end('Build not found. Run: npm run build');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(content);
    });
    return;
  }

  // Serve static files from dist
  const filePath = path.join(__dirname, 'dist', req.url || '');
  const extname = path.extname(filePath);
  const contentType = mimeTypes[extname] || 'text/plain';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404);
      res.end('File not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  });
});

server.listen(PORT, () => {
  console.log(`🚀 Test server running at http://localhost:${PORT}`);
  console.log(`📱 Open http://localhost:${PORT}/test to test the MCP app`);
  console.log('');
  console.log('Quick workflow:');
  console.log('  1. Make changes to src/');
  console.log('  2. Run: npm run build');
  console.log('  3. Refresh browser');
  console.log('');
});
