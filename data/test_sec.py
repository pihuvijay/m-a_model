# test_sec.py
import requests
import json
from config import Config

def test_sec_api(ticker="CRM"):
    """Simple test of SEC API"""
    config = Config()
    
    print(f"Testing SEC API for {ticker}...")
    print(f"SEC API Key: {'✅ Set' if config.SEC_API_KEY else '❌ Not set'}")
    
    if not config.SEC_API_KEY:
        print("❌ Need SEC API key to test")
        print("Get one free at: https://sec-api.io/")
        return
    
    try:
        # SEC API endpoint
        url = f"{config.SEC_BASE_URL}/filing-search"
        
        params = {
            "query": f"ticker:{ticker} AND formType:10-K",
            "token": config.SEC_API_KEY,
            "size": 3  # Just get 3 filings
        }
        
        print(f"Making request to: {url}")
        print(f"Query: {params['query']}")
        
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            filings = data.get("filings", [])
            
            print(f"✅ Found {len(filings)} filings for {ticker}")
            
            for i, filing in enumerate(filings[:3]):
                print(f"\nFiling {i+1}:")
                print(f"  Date: {filing.get('filedAt')}")
                print(f"  Form: {filing.get('formType')}")
                print(f"  Period: {filing.get('periodOfReport')}")
                print(f"  URL: {filing.get('linkToFilingDetails', '')[:50]}...")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    # Test different tickers
    test_sec_api("CRM")
    print("\n" + "="*50 + "\n")
    test_sec_api("AAPL")