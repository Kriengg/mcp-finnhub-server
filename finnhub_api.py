import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FinnhubAPI:
    """
    A client for the Finnhub Stock API
    """
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            raise ValueError("FINNHUB_API_KEY environment variable is not set")
    
    def _make_request(self, endpoint, params=None):
        """
        Make a request to the Finnhub API
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters. Defaults to None.
            
        Returns:
            dict: API response
        """
        if params is None:
            params = {}
        
        # Add API key to parameters
        params["token"] = self.api_key
        
        # Make request
        response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
        
        # Check if request was successful
        if response.status_code != 200:
            error_message = f"API request failed with status code {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_message += f": {error_data['error']}"
            except:
                pass
            raise Exception(error_message)
        
        return response.json()
    
    def get_stock_quote(self, symbol):
        """
        Get real-time quote data for a stock
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Quote data including current price, change, etc.
        """
        return self._make_request("/quote", {"symbol": symbol})
    
    def get_company_profile(self, symbol):
        """
        Get general information about a company
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Company profile data
        """
        return self._make_request("/stock/profile2", {"symbol": symbol})
    
    def get_stock_news(self, symbol, from_date, to_date):
        """
        Get news for a specific company
        
        Args:
            symbol (str): Stock symbol
            from_date (str): From date in format YYYY-MM-DD
            to_date (str): To date in format YYYY-MM-DD
            
        Returns:
            list: List of news articles
        """
        params = {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        }
        return self._make_request("/company-news", params)
