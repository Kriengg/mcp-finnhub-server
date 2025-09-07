"""
Helper functions for the natural language processing endpoint.
These functions simplify calling the various MCP tools.
"""

import logging
from datetime import datetime, timedelta
from finnhub_api import FinnhubAPI

logger = logging.getLogger("mcp-server")
finnhub_client = FinnhubAPI()

def tool_stock_quote(params):
    """Get a stock quote in a simplified format"""
    symbol = params.get('symbol')
    if not symbol:
        return {"error": "Symbol is required"}
    
    try:
        quote_data = finnhub_client.get_stock_quote(symbol)
        
        return {
            "symbol": symbol,
            "currentPrice": quote_data.get('c'),
            "change": quote_data.get('d'),
            "percentChange": quote_data.get('dp'),
            "highOfDay": quote_data.get('h'),
            "lowOfDay": quote_data.get('l'),
            "openPrice": quote_data.get('o'),
            "previousClose": quote_data.get('pc'),
            "timestamp": quote_data.get('t')
        }
    except Exception as e:
        logger.error(f"Error getting stock quote for {symbol}: {e}")
        return {"error": f"Failed to get stock quote: {str(e)}"}

def tool_company_profile(params):
    """Get company profile information in a simplified format"""
    symbol = params.get('symbol')
    if not symbol:
        return {"error": "Symbol is required"}
    
    try:
        profile_data = finnhub_client.get_company_profile(symbol)
        return profile_data
    except Exception as e:
        logger.error(f"Error getting company profile for {symbol}: {e}")
        return {"error": f"Failed to get company profile: {str(e)}"}

def tool_company_news(params):
    """Get company news in a simplified format"""
    symbol = params.get('symbol')
    days_back = params.get('daysBack', 7)  # Default to 7 days
    
    if not symbol:
        return {"error": "Symbol is required"}
    
    try:
        # Calculate date range
        today = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        news_data = finnhub_client.get_stock_news(symbol, from_date, today)
        
        # Format and limit the response
        formatted_news = []
        for article in news_data[:10]:  # Limit to 10 articles
            formatted_news.append({
                "headline": article.get("headline"),
                "summary": article.get("summary"),
                "url": article.get("url"),
                "date": article.get("datetime"),
                "source": article.get("source")
            })
        
        return {
            "symbol": symbol,
            "news": formatted_news
        }
    except Exception as e:
        logger.error(f"Error getting company news for {symbol}: {e}")
        return {"error": f"Failed to get company news: {str(e)}"}

def tool_stock_sentiment(params):
    """Analyze sentiment about a company based on recent news and stock performance"""
    symbol = params.get('symbol')
    
    if not symbol:
        return {"error": "Symbol is required"}
    
    try:
        # Get stock quote data
        quote_data = tool_stock_quote({"symbol": symbol})
        if "error" in quote_data:
            return quote_data
            
        # Get recent news
        news_data = tool_company_news({"symbol": symbol, "daysBack": 7})
        if "error" in news_data:
            return news_data
            
        # Calculate simple sentiment metrics
        
        # 1. Price performance sentiment
        price_change_percent = quote_data.get("percentChange", 0)
        if price_change_percent > 2:
            price_sentiment = "very positive"
            price_score = 2
        elif price_change_percent > 0.5:
            price_sentiment = "positive"
            price_score = 1
        elif price_change_percent > -0.5:
            price_sentiment = "neutral"
            price_score = 0
        elif price_change_percent > -2:
            price_sentiment = "negative"
            price_score = -1
        else:
            price_sentiment = "very negative"
            price_score = -2
            
        # 2. News volume sentiment (more news often indicates more interest)
        news_count = len(news_data.get("news", []))
        if news_count > 8:
            news_volume_sentiment = "high media interest"
        elif news_count > 4:
            news_volume_sentiment = "moderate media interest"
        else:
            news_volume_sentiment = "low media interest"
            
        # 3. Generate simple overall sentiment
        sentiment_mapping = {
            2: "very bullish",
            1: "bullish",
            0: "neutral",
            -1: "bearish",
            -2: "very bearish"
        }
        
        overall_sentiment = sentiment_mapping.get(price_score, "neutral")
        
        return {
            "symbol": symbol,
            "overallSentiment": overall_sentiment,
            "priceSentiment": price_sentiment,
            "priceChange": price_change_percent,
            "newsVolume": news_count,
            "mediaInterest": news_volume_sentiment,
            "analysisDate": datetime.now().strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment for {symbol}: {e}")
        return {"error": f"Failed to analyze sentiment: {str(e)}"}
