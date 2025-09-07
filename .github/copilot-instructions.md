# MCP Server Python Project

This project implements a Model Context Protocol (MCP) server using Python, which can be connected to from Postman or other MCP clients. It includes Finnhub stock API integration and a natural language interface.

## References
- Python SDK Documentation: https://github.com/modelcontextprotocol/python-sdk
- MCP Specification: https://modelcontextprotocol.io/
- Finnhub API: https://finnhub.io/docs/api

## Project Structure
- `server.py`: Main server implementation with MCP endpoints and natural language interface
- `finnhub_api.py`: Client for Finnhub Stock API
- `nlp_tools.py`: Helper functions for natural language processing and stock data tools
- `.vscode/mcp.json`: MCP server configuration for VS Code
- `requirements.txt`: Python dependencies

## Features
- Standard MCP JSON-RPC 2.0 interface
- Stock data tools (quotes, company profiles, news, sentiment analysis)
- Natural language endpoint for querying stock data using plain English
- LLM-powered query understanding and processing
