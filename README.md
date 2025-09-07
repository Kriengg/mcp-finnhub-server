# Python MCP Server with Finnhub Stock API Integration

This project demonstrates a Model Context Protocol (MCP) server implementation using Python and Flask. It provides standard MCP capabilities along with Finnhub Stock API integration for real-time financial data.

## Features

- Provides sample resources (text and JSON)
- Implements basic tools (echo and calculator with trigonometric functions)
- Stock API tools:
  - `stock_quote` - Get real-time stock quotes
  - `company_profile` - Get company information
  - `company_news` - Get recent news articles for a company
- Offers example prompts
- Uses JSON-RPC 2.0 over HTTP for communication

## Prerequisites

- Python 3.8+
- MCP-compatible client (like Postman)
- Finnhub API key (get one at https://finnhub.io/)

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/MacOS
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Finnhub API key:
   ```
   FINNHUB_API_KEY=your_api_key_here
   ```

## Running the Server

To run the server manually:

```
python server.py
```

The server will be available at http://localhost:5000/mcp

## Connecting with Postman

1. Open Postman Desktop
2. Create a new request:
   - Set the request method to POST
   - Set the URL to http://localhost:5000/mcp
   - Set the Content-Type header to application/json

3. Send an initialize request:
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

4. Once initialized, you can make requests to explore and use the server:

   List available tools:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 2,
     "method": "tools/list",
     "params": {}
   }
   ```

   Call a tool:
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

   Get a stock quote:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 4,
     "method": "tools/call",
     "params": {
       "name": "stock_quote",
       "parameters": {
         "symbol": "AAPL"
       }
     }
   }
   ```

   Get company profile:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 5,
     "method": "tools/call",
     "params": {
       "name": "company_profile",
       "parameters": {
         "symbol": "MSFT"
       }
     }
   }
   ```

   List available resources:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 4,
     "method": "resources/list",
     "params": {}
   }
   ```

   Read a resource:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 5,
     "method": "resources/read",
     "params": {
       "uri": "sample://data/example.txt"
     }
   }
   ```

   List available prompts:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 6,
     "method": "prompts/list",
     "params": {}
   }
   ```

## Understanding the Code

- `server.py` - Main server implementation that handles MCP requests using Flask
- `.vscode/mcp.json` - Configuration for VS Code MCP client integration

## Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Specification](https://modelcontextprotocol.io/specification/latest)
