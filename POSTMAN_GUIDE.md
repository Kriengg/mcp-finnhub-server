# MCP Server with Postman Guide

## Overview

In this workspace, we've created a Python-based Model Context Protocol (MCP) server that can be accessed via Postman. This implementation simulates a real MCP server using Flask to handle JSON-RPC 2.0 requests over HTTP, and also includes a natural language interface and Finnhub stock API integration.

## Components

1. **server.py**: A Flask-based MCP server that provides:
   - Tool functionality (echo, calculator, stock data tools)
   - Resources (text and JSON examples)
   - Prompts (greeting and data analysis templates)
   - Natural language interface for stock queries

2. **finnhub_api.py**: Client for the Finnhub Stock API
   - Real-time stock quotes
   - Company profiles
   - News articles

3. **nlp_tools.py**: Helper functions for natural language processing
   - Simplified API for stock data
   - Sentiment analysis for stocks

4. **requirements.txt**: Dependencies for the project
   - Flask for the HTTP server
   - Requests for HTTP communication
   - OpenAI for natural language processing

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

   Get a stock quote:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 5,
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
     "id": 6,
     "method": "tools/call",
     "params": {
       "name": "company_profile",
       "parameters": {
         "symbol": "MSFT"
       }
     }
   }
   ```

   Get company news:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 7,
     "method": "tools/call",
     "params": {
       "name": "company_news",
       "parameters": {
         "symbol": "TSLA",
         "days": 7
       }
     }
   }
   ```
   
   Analyze stock sentiment:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 8,
     "method": "tools/call",
     "params": {
       "name": "stock_sentiment",
       "parameters": {
         "symbol": "AAPL"
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

## Using the Natural Language Interface

This server also provides a natural language endpoint that allows you to query stock information using plain English instead of structured JSON-RPC requests.

1. **Set up Postman**:
   - Create a new POST request to http://localhost:5000/ask
   - Set Content-Type header to application/json

2. **Send a natural language query**:
   ```json
   {
     "query": "What's the current stock price for AAPL?"
   }
   ```

   Other examples:
   ```json
   {
     "query": "Tell me about Microsoft as a company"
   }
   ```

   ```json
   {
     "query": "What's the latest news for Tesla?"
   }
   ```

   ```json
   {
     "query": "What's the market sentiment for Amazon stock?"
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
