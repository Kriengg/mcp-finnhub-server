# MCP Server with Postman Guide

## Overview

In this workspace, we've created a Python-based Model Context Protocol (MCP) server that can be accessed via Postman. This implementation simulates a real MCP server using Flask to handle JSON-RPC 2.0 requests over HTTP.

## Components

1. **server.py**: A Flask-based MCP server that provides:
   - Tool functionality (echo and calculator)
   - Resources (text and JSON examples)
   - Prompts (greeting and data analysis templates)

2. **requirements.txt**: Dependencies for the project
   - Flask for the HTTP server
   - Requests for HTTP communication

## How to Use with Postman

1. **Start the server**:
   - Run the task "Run MCP Server" in VS Code
   - The server will be available at http://localhost:5000/mcp

2. **Set up Postman**:
   - Open Postman Desktop
   - Create a new POST request to http://localhost:5000/mcp
   - Set Content-Type header to application/json

3. **Initialize the connection**:
   Send this request body:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "initialize",
     "params": {
       "protocolVersion": "2025-06-18",
       "capabilities": {
         "elicitation": {},
         "sampling": {}
       },
       "clientInfo": {
         "name": "postman-client",
         "version": "1.0.0"
       }
     }
   }
   ```

4. **Explore available tools**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 2,
     "method": "tools/list",
     "params": {}
   }
   ```

5. **Use a tool**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 3,
     "method": "tools/call",
     "params": {
       "name": "echo",
       "parameters": {
         "message": "Hello, MCP!"
       }
     }
   }
   ```

   Or try the calculator:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 4,
     "method": "tools/call",
     "params": {
       "name": "calculate",
       "parameters": {
         "operation": "add",
         "a": 5,
         "b": 3
       }
     }
   }
   ```

6. **Explore resources**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 5,
     "method": "resources/list",
     "params": {}
   }
   ```

7. **Read a resource**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 6,
     "method": "resources/read",
     "params": {
       "uri": "sample://data/example.txt"
     }
   }
   ```

## Limitations and Next Steps

- This is a simulated MCP server for demonstration purposes
- For a production-ready MCP server, consider:
  - Using the official MCP SDKs when they become available
  - Implementing proper authentication and security
  - Adding more robust error handling and validation

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/latest)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
