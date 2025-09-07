#!/usr/bin/env python
"""
Simple MCP Server implementation using Python and Flask with Finnhub stock API integration.
This server simulates an MCP server that can be connected to via Postman.
"""

import os
import sys
import json
import logging
import uuid
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, Response
from finnhub_api import FinnhubAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Initialize Flask app
app = Flask(__name__)

# Initialize Finnhub API client
finnhub_client = FinnhubAPI()

# Initialize OpenAI client if API key is available
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    try:
        from openai import OpenAI
        llm_client = OpenAI(api_key=openai_api_key)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {e}")
        llm_client = None
else:
    logger.warning("OpenAI API key not found. Natural language processing will be unavailable.")
    llm_client = None

# Import NLP tool helpers
from nlp_tools import tool_stock_quote, tool_company_profile, tool_company_news, tool_stock_sentiment

# Store sessions
sessions = {}

@app.route('/mcp', methods=['POST'])
def mcp_endpoint():
    """Main JSON-RPC endpoint for MCP communication."""
    try:
        content = request.json
        logger.info(f"Received request: {content}")
        
        # Check if this is a valid JSON-RPC 2.0 request
        if not isinstance(content, dict) or content.get('jsonrpc') != '2.0':
            return jsonify({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32600,
                    'message': 'Invalid Request'
                },
                'id': content.get('id')
            }), 400
            
        # Extract the request information
        method = content.get('method')
        params = content.get('params', {})
        request_id = content.get('id')
        
        # Handle different MCP methods
        if method == 'initialize':
            return handle_initialize(params, request_id)
        elif method == 'resources/list':
            return handle_resources_list(params, request_id)
        elif method == 'resources/read':
            return handle_resources_read(params, request_id)
        elif method == 'tools/list':
            return handle_tools_list(params, request_id)
        elif method == 'tools/call':
            return handle_tools_call(params, request_id)
        elif method == 'prompts/list':
            return handle_prompts_list(params, request_id)
        else:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32601,
                    'message': f'Method not found: {method}'
                },
                'id': request_id
            }), 404
            
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32603,
                'message': f'Internal error: {str(e)}'
            },
            'id': None
        }), 500

def handle_initialize(params, request_id):
    """Handle initialize request."""
    protocol_version = params.get('protocolVersion', '')
    client_capabilities = params.get('capabilities', {})
    client_info = params.get('clientInfo', {})
    
    # Create a session for this client
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'protocol_version': protocol_version,
        'client_capabilities': client_capabilities
    }
    
    logger.info(f"Client initialized with protocol version {protocol_version}")
    logger.info(f"Client capabilities: {client_capabilities}")
    
    # Return server capabilities
    return jsonify({
        'jsonrpc': '2.0',
        'result': {
            'protocolVersion': protocol_version,
            'capabilities': {
                'tools': {},
                'resources': {},
                'prompts': {}
            },
            'serverInfo': {
                'name': 'python-mcp-sample',
                'title': 'Python MCP Sample Server with Finnhub Integration',
                'version': '1.0.0'
            }
        },
        'id': request_id
    })

def handle_resources_list(params, request_id):
    """Handle resources/list request."""
    resources = [
        {
            'uri': 'sample://data/example.txt',
            'mimeType': 'text/plain',
            'title': 'Sample Text Resource',
            'description': 'This is a sample text resource provided by the MCP server.'
        },
        {
            'uri': 'sample://data/config.json',
            'mimeType': 'application/json',
            'title': 'Sample JSON Configuration',
            'description': 'This is a sample JSON configuration resource.'
        },
        {
            'uri': 'finnhub://data/stock-info.txt',
            'mimeType': 'text/plain',
            'title': 'Finnhub Stock API Information',
            'description': 'Information about the Finnhub Stock API integration.'
        }
    ]
    
    return jsonify({
        'jsonrpc': '2.0',
        'result': {
            'resources': resources
        },
        'id': request_id
    })

def handle_resources_read(params, request_id):
    """Handle resources/read request."""
    uri = params.get('uri', '')
    logger.info(f"Client requested resource: {uri}")
    
    content = None
    mime_type = None
    
    if uri == 'sample://data/example.txt':
        content = "This is sample text content from the MCP server.\nIt can be used to provide context to the model."
        mime_type = 'text/plain'
    elif uri == 'sample://data/config.json':
        content = json.dumps({
            'setting1': 'value1',
            'setting2': 'value2',
            'nested': {
                'key': 'value'
            }
        }, indent=2)
        mime_type = 'application/json'
    elif uri == 'finnhub://data/stock-info.txt':
        content = """This MCP server integrates with the Finnhub Stock API to provide real-time stock data and analysis.
        
Available stock tools:
1. stock_quote - Get real-time quotes for a stock symbol
2. company_profile - Get company information for a stock symbol
3. company_news - Get recent news articles for a company
4. stock_sentiment - Analyze sentiment and market perception about a stock

Example usage:
- Use the stock_quote tool with a symbol parameter (e.g., AAPL, MSFT, GOOG)
- Use the company_profile tool to get detailed information about a company
- Use the company_news tool to get recent news articles (optionally specify the number of days)
- Use the stock_sentiment tool to analyze market sentiment and perception about a stock

Natural Language Interface:
This server also provides a natural language endpoint at /ask that allows you to:
- Query stock prices in plain English (e.g., "What's the current price of Apple stock?")
- Get company information (e.g., "Tell me about Microsoft")
- Check recent news (e.g., "What's the latest news about Tesla?")
- Analyze market sentiment (e.g., "What's the market sentiment for Amazon stock?")
"""
        mime_type = 'text/plain'
    else:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32602,
                'message': f'Resource not found: {uri}'
            },
            'id': request_id
        }), 404
    
    return jsonify({
        'jsonrpc': '2.0',
        'result': {
            'content': content,
            'mimeType': mime_type
        },
        'id': request_id
    })

def handle_tools_list(params, request_id):
    """Handle tools/list request."""
    tools = [
        {
            'name': 'echo',
            'title': 'Echo Tool',
            'description': 'A simple tool that echoes back the input message',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'The message to echo back'
                    }
                },
                'required': ['message']
            }
        },
        {
            'name': 'calculate',
            'title': 'Simple Calculator',
            'description': 'Performs basic mathematical operations',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'operation': {
                        'type': 'string',
                        'enum': ['add', 'subtract', 'multiply', 'divide', 'sin', 'cos', 'tan'],
                        'description': 'The operation to perform'
                    },
                    'a': {
                        'type': 'number',
                        'description': 'First operand'
                    },
                    'b': {
                        'type': 'number',
                        'description': 'Second operand (not used for sin, cos, tan)'
                    }
                },
                'required': ['operation', 'a']
            }
        },
        {
            'name': 'stock_quote',
            'title': 'Stock Quote',
            'description': 'Get real-time stock quote data from Finnhub',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'symbol': {
                        'type': 'string',
                        'description': 'Stock symbol (e.g., AAPL, MSFT, GOOG)'
                    }
                },
                'required': ['symbol']
            }
        },
        {
            'name': 'company_profile',
            'title': 'Company Profile',
            'description': 'Get company profile information from Finnhub',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'symbol': {
                        'type': 'string',
                        'description': 'Stock symbol (e.g., AAPL, MSFT, GOOG)'
                    }
                },
                'required': ['symbol']
            }
        },
        {
            'name': 'company_news',
            'title': 'Company News',
            'description': 'Get recent news for a company from Finnhub',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'symbol': {
                        'type': 'string',
                        'description': 'Stock symbol (e.g., AAPL, MSFT, GOOG)'
                    },
                    'days': {
                        'type': 'integer',
                        'description': 'Number of days of news to retrieve (default: 7)'
                    }
                },
                'required': ['symbol']
            }
        },
        {
            'name': 'stock_sentiment',
            'title': 'Stock Sentiment Analysis',
            'description': 'Analyze sentiment and market perception about a stock',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'symbol': {
                        'type': 'string',
                        'description': 'Stock symbol (e.g., AAPL, MSFT, GOOG)'
                    }
                },
                'required': ['symbol']
            }
        }
    ]
    
    return jsonify({
        'jsonrpc': '2.0',
        'result': {
            'tools': tools
        },
        'id': request_id
    })

def handle_tools_call(params, request_id):
    """Handle tools/call request."""
    tool_name = params.get('name', '')
    parameters = params.get('parameters', {})
    logger.info(f"Tool call request: {tool_name} with params {parameters}")
    
    try:
        if tool_name == 'echo':
            message = parameters.get('message', '')
            result = f'Echo: {message}'
        elif tool_name == 'calculate':
            operation = parameters.get('operation')
            a = parameters.get('a')
            b = parameters.get('b', 0)  # Default to 0 for unary operations
            
            if operation == 'add':
                result = a + b
            elif operation == 'subtract':
                result = a - b
            elif operation == 'multiply':
                result = a * b
            elif operation == 'divide':
                if b == 0:
                    return jsonify({
                        'jsonrpc': '2.0',
                        'error': {
                            'code': -32602,
                            'message': 'Division by zero is not allowed'
                        },
                        'id': request_id
                    }), 400
                result = a / b
            elif operation == 'sin':
                result = math.sin(a)
            elif operation == 'cos':
                result = math.cos(a)
            elif operation == 'tan':
                result = math.tan(a)
            else:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32602,
                        'message': f'Unknown operation: {operation}'
                    },
                    'id': request_id
                }), 400
        elif tool_name == 'stock_quote':
            symbol = parameters.get('symbol')
            if not symbol:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32602,
                        'message': 'Symbol is required'
                    },
                    'id': request_id
                }), 400
                
            quote_data = finnhub_client.get_stock_quote(symbol)
            
            result = {
                'symbol': symbol,
                'current_price': quote_data.get('c'),
                'change': quote_data.get('d'),
                'percent_change': quote_data.get('dp'),
                'high_price': quote_data.get('h'),
                'low_price': quote_data.get('l'),
                'open_price': quote_data.get('o'),
                'previous_close': quote_data.get('pc'),
                'timestamp': quote_data.get('t')
            }
        elif tool_name == 'company_profile':
            symbol = parameters.get('symbol')
            if not symbol:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32602,
                        'message': 'Symbol is required'
                    },
                    'id': request_id
                }), 400
                
            profile_data = finnhub_client.get_company_profile(symbol)
            
            result = {
                'symbol': symbol,
                'name': profile_data.get('name'),
                'country': profile_data.get('country'),
                'currency': profile_data.get('currency'),
                'exchange': profile_data.get('exchange'),
                'ipo': profile_data.get('ipo'),
                'market_cap': profile_data.get('marketCapitalization'),
                'industry': profile_data.get('finnhubIndustry'),
                'website': profile_data.get('weburl'),
                'logo': profile_data.get('logo')
            }
        elif tool_name == 'company_news':
            symbol = parameters.get('symbol')
            days = parameters.get('days', 7)  # Default to 7 days
            
            if not symbol:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32602,
                        'message': 'Symbol is required'
                    },
                    'id': request_id
                }), 400
                
            # Calculate date range
            today = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            news_data = finnhub_client.get_stock_news(symbol, from_date, today)
            
            # Format and limit the response
            formatted_news = []
            for article in news_data[:10]:  # Limit to 10 articles
                formatted_news.append({
                    'headline': article.get('headline'),
                    'summary': article.get('summary'),
                    'url': article.get('url'),
                    'date': article.get('datetime'),
                    'source': article.get('source')
                })
            
            result = {
                'symbol': symbol,
                'articles': formatted_news
            }
        elif tool_name == 'stock_sentiment':
            symbol = parameters.get('symbol')
            if not symbol:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32602,
                        'message': 'Symbol is required'
                    },
                    'id': request_id
                }), 400
                
            # Use our sentiment analysis tool
            sentiment_data = tool_stock_sentiment({"symbol": symbol})
            
            result = {
                'symbol': symbol,
                'overallSentiment': sentiment_data.get('overallSentiment', 'neutral'),
                'priceSentiment': sentiment_data.get('priceSentiment', 'neutral'),
                'priceChange': sentiment_data.get('priceChange', 0),
                'newsVolume': sentiment_data.get('newsVolume', 0),
                'mediaInterest': sentiment_data.get('mediaInterest', 'low media interest'),
                'analysisDate': sentiment_data.get('analysisDate', datetime.now().strftime("%Y-%m-%d"))
            }
        else:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': f'Unknown tool: {tool_name}'
                },
                'id': request_id
            }), 404
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32603,
                'message': f'Tool execution error: {str(e)}'
            },
            'id': request_id
        }), 500
    
    return jsonify({
        'jsonrpc': '2.0',
        'result': {
            'result': result
        },
        'id': request_id
    })

def handle_prompts_list(params, request_id):
    """Handle prompts/list request."""
    prompts = [
        {
            'name': 'greeting',
            'title': 'Greeting Prompt',
            'description': 'A simple greeting prompt',
            'promptText': 'Hello! How can I assist you today?',
            'parameterSchema': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'The name of the person to greet'
                    }
                }
            }
        },
        {
            'name': 'data-analysis',
            'title': 'Data Analysis Helper',
            'description': 'A prompt to help with data analysis tasks',
            'promptText': 'I\'ll help you analyze your data. I can interpret {data_type} data and provide insights on {analysis_type}.',
            'parameterSchema': {
                'type': 'object',
                'properties': {
                    'data_type': {
                        'type': 'string',
                        'description': 'The type of data to analyze (e.g., CSV, JSON, etc.)'
                    },
                    'analysis_type': {
                        'type': 'string',
                        'description': 'The type of analysis to perform (e.g., trend analysis, statistical summary, etc.)'
                    }
                },
                'required': ['data_type', 'analysis_type']
            }
        },
        {
            'name': 'stock-analysis',
            'title': 'Stock Analysis Helper',
            'description': 'A prompt to help with stock analysis tasks',
            'promptText': 'I\'ll help you analyze {symbol} stock data. I can provide information about current price, company profile, and recent news.',
            'parameterSchema': {
                'type': 'object',
                'properties': {
                    'symbol': {
                        'type': 'string',
                        'description': 'The stock symbol to analyze (e.g., AAPL, MSFT, GOOG)'
                    }
                },
                'required': ['symbol']
            }
        }
    ]
    
    return jsonify({
        'jsonrpc': '2.0',
        'result': {
            'prompts': prompts
        },
        'id': request_id
    })

@app.route('/ask', methods=['POST'])
def handle_natural_language():
    """Handle natural language queries and convert them to tool calls"""
    if not llm_client:
        return jsonify({"error": "LLM processing is not available. Please set OPENAI_API_KEY in .env file."}), 500
    
    content_type = request.headers.get('Content-Type', '')
    if content_type.startswith('application/json'):
        query = request.json.get('query')
    else:
        query = request.data.decode('utf-8') or request.form.get('query')
    
    if not query:
        return jsonify({"error": "No query provided. Please send a 'query' parameter."}), 400
    
    # Step 1: Use LLM to understand the query
    try:
        system_prompt = """You are an AI assistant that helps convert natural language queries about stocks into structured actions.
        Available tools:
        1. stock_quote - Gets current price info for a stock symbol. Use this when the user asks about current price, stock value, or how a stock is trading.
        2. company_profile - Gets company information. Use this when the user asks about company details, what a company does, or company information.
        3. company_news - Gets recent news about a company. Use this when the user asks about news, recent events, or articles about a company.
        4. stock_sentiment - Analyzes sentiment and market perception about a stock. Use this when the user asks about sentiment, market feeling, perception, bullish/bearish outlook, or how the market views a stock.
        
        When the user asks about how the market is "feeling" about a stock or mentions "sentiment", "perception", "outlook", or "analysis", use the stock_sentiment tool.
        
        Extract the stock symbol and determine which tool to call."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        response = llm_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_stock_quote",
                        "description": "Get current stock price information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "The stock symbol (e.g., AAPL, MSFT)"
                                }
                            },
                            "required": ["symbol"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_company_profile",
                        "description": "Get company information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "The stock symbol (e.g., AAPL, MSFT)"
                                }
                            },
                            "required": ["symbol"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_company_news",
                        "description": "Get recent news about a company",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "The stock symbol (e.g., AAPL, MSFT)"
                                },
                                "daysBack": {
                                    "type": "integer",
                                    "description": "How many days of news to retrieve"
                                }
                            },
                            "required": ["symbol"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_stock_sentiment",
                        "description": "Analyze sentiment and market perception about a stock",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "The stock symbol (e.g., AAPL, MSFT)"
                                }
                            },
                            "required": ["symbol"]
                        }
                    }
                }
            ],
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # Step 2: Call the appropriate tool based on LLM's understanding
        if message.tool_calls and len(message.tool_calls) > 0:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            symbol = function_args.get('symbol', '').upper()
            
            if not symbol:
                return jsonify({"error": "Could not determine stock symbol from query"}), 400
            
            if function_name == "get_stock_quote":
                # Call the stock_quote tool
                result = tool_stock_quote({"symbol": symbol})
                
                # Format the response in natural language
                if "error" in result:
                    return jsonify({"error": result["error"]}), 400
                
                response_text = f"""
                Current information for {symbol}:
                Price: ${result['currentPrice']:.2f}
                Change: {result['change']:.2f} ({result['percentChange']:.2f}%)
                Today's Range: ${result['lowOfDay']:.2f} - ${result['highOfDay']:.2f}
                Opening Price: ${result['openPrice']:.2f}
                Previous Close: ${result['previousClose']:.2f}
                """
                
                return jsonify({
                    "query": query,
                    "response": response_text.strip(),
                    "data": result
                })
                
            elif function_name == "get_company_profile":
                # Call the company_profile tool
                result = tool_company_profile({"symbol": symbol})
                
                # Format the response in natural language
                if "error" in result:
                    return jsonify({"error": result["error"]}), 400
                
                response_text = f"""
                Company Profile for {result.get('name', symbol)}:
                Industry: {result.get('finnhubIndustry', 'N/A')}
                Market Cap: ${result.get('marketCapitalization', 0)/1000:.2f} billion
                Country: {result.get('country', 'N/A')}
                Exchange: {result.get('exchange', 'N/A')}
                IPO Date: {result.get('ipo', 'N/A')}
                Website: {result.get('weburl', 'N/A')}
                """
                
                return jsonify({
                    "query": query,
                    "response": response_text.strip(),
                    "data": result
                })
                
            elif function_name == "get_company_news":
                # Call the company_news tool
                days_back = function_args.get('daysBack', 7)
                result = tool_company_news({"symbol": symbol, "daysBack": days_back})
                
                # Format the response in natural language
                if "error" in result:
                    return jsonify({"error": result["error"]}), 400
                
                news_items = result.get('news', [])
                if not news_items:
                    response_text = f"No recent news found for {symbol} in the past {days_back} days."
                else:
                    response_text = f"Recent news for {symbol} (past {days_back} days):\n\n"
                    for i, news in enumerate(news_items[:5], 1):  # Show up to 5 news items
                        headline = news.get('headline', 'No headline')
                        source = news.get('source', 'Unknown source')
                        url = news.get('url', '#')
                        response_text += f"{i}. {headline} ({source})\n"
                
                return jsonify({
                    "query": query,
                    "response": response_text.strip(),
                    "data": {"totalNews": len(news_items), "recentNews": news_items[:5]}
                })
                
            elif function_name == "get_stock_sentiment":
                # Call the stock_sentiment tool
                result = tool_stock_sentiment({"symbol": symbol})
                
                # Format the response in natural language
                if "error" in result:
                    return jsonify({"error": result["error"]}), 400
                
                response_text = f"""
                Sentiment Analysis for {symbol}:
                Overall Market Sentiment: {result['overallSentiment']}
                Price Sentiment: {result['priceSentiment']} (Change: {result['priceChange']:.2f}%)
                Media Interest: {result['mediaInterest']} ({result['newsVolume']} recent news articles)
                Analysis Date: {result['analysisDate']}
                """
                
                return jsonify({
                    "query": query,
                    "response": response_text.strip(),
                    "data": result
                })
        
        # If no function call was made, return a generic response
        return jsonify({
            "query": query,
            "response": "I couldn't determine what stock information you're looking for. Please specify a stock symbol and what information you need (price, company info, or news)."
        })
        
    except Exception as e:
        logger.error(f"Error processing natural language query: {e}")
        return jsonify({
            "error": f"Error processing query: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("Starting MCP server with Finnhub integration on http://localhost:5000/mcp")
    app.run(debug=True)
