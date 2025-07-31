import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    SEC_API_KEY = os.getenv("SEC_API_KEY", "")
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
    
    # API Settings
    SEC_BASE_URL = "https://api.sec-api.io"
    YAHOO_FINANCE_DELAY = float(os.getenv("YAHOO_FINANCE_DELAY", "1"))
    
    # Data Settings
    CACHE_ENABLED = True
    CACHE_DURATION_HOURS = 24
    
    # Server Settings
    HOST = "127.0.0.1"
    PORT = 8000
    
    @classmethod
    def validate(cls):
        """Validate that required config is present"""
        if not cls.SEC_API_KEY:
            print("Warning: SEC_API_KEY not set")
        if not cls.ALPHA_VANTAGE_KEY:
            print("Warning: ALPHA_VANTAGE_KEY not set")
        
        return True