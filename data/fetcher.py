import yfinance as yf
import requests
import pandas as pd
import json
from typing import Dict, List, Optional, Any
import time
from datetime import datetime, timedelta
from config import Config

class DataFetcher:
    def __init__(self):
        self.config = Config()
        
    def fetch_company_data(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch complete company data from multiple sources
        Returns structured data ready for ML pipeline
        """
        print(f"Fetching data for {ticker}...")
        
        # Get data from multiple sources
        yahoo_data = self._fetch_yahoo_data(ticker)
        sec_data = self._fetch_sec_data(ticker)
        
        # Combine into structured format
        company_data = {
            "ticker": ticker,
            "company_name": yahoo_data.get("company_name", ""),
            "fetch_timestamp": datetime.now().isoformat(),
            
            # Market Data (Current)
            "market_data": {
                "current_price": yahoo_data.get("current_price"),
                "market_cap": yahoo_data.get("market_cap"),
                "enterprise_value": yahoo_data.get("enterprise_value"),
                "pe_ratio": yahoo_data.get("pe_ratio"),
                "pb_ratio": yahoo_data.get("pb_ratio"),
                "debt_to_equity": yahoo_data.get("debt_to_equity")
            },
            
            # Financial Statements (Historical)
            "financials": {
                "income_statement": sec_data.get("income_statement", []),
                "balance_sheet": sec_data.get("balance_sheet", []),
                "cash_flow": sec_data.get("cash_flow", [])
            },
            
            # Key Metrics (Processed)
            "key_metrics": {
                "revenue_ttm": yahoo_data.get("revenue_ttm"),
                "net_income_ttm": yahoo_data.get("net_income_ttm"),
                "free_cash_flow_ttm": yahoo_data.get("free_cash_flow_ttm"),
                "total_debt": yahoo_data.get("total_debt"),
                "total_cash": yahoo_data.get("total_cash"),
                "book_value": yahoo_data.get("book_value")
            }
        }
        
        return company_data
    
    def _fetch_yahoo_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch data from Yahoo Finance"""
        try:
            # Add delay to respect rate limits
            time.sleep(self.config.YAHOO_FINANCE_DELAY)
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get financial data
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            return {
                "company_name": info.get("longName", ticker),
                "current_price": info.get("currentPrice"),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "debt_to_equity": info.get("debtToEquity"),
                "revenue_ttm": info.get("totalRevenue"),
                "net_income_ttm": info.get("netIncomeToCommon"),
                "free_cash_flow_ttm": info.get("freeCashflow"),
                "total_debt": info.get("totalDebt"),
                "total_cash": info.get("totalCash"),
                "book_value": info.get("bookValue"),
                "raw_financials": {
                    "income_statement": financials.to_dict() if not financials.empty else {},
                    "balance_sheet": balance_sheet.to_dict() if not balance_sheet.empty else {},
                    "cash_flow": cash_flow.to_dict() if not cash_flow.empty else {}
                }
            }
            
        except Exception as e:
            print(f"Error fetching Yahoo data for {ticker}: {e}")
            return {"error": str(e)}
    
    def _fetch_sec_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch data from SEC API"""
        try:
            if not self.config.SEC_API_KEY:
                print("SEC API key not provided, skipping SEC data")
                return {}
            
            # SEC API endpoint for company filings
            url = f"{self.config.SEC_BASE_URL}/filing-search"
            
            params = {
                "query": f"ticker:{ticker} AND formType:10-K",
                "token": self.config.SEC_API_KEY,
                "size": 5  # Get last 5 annual reports
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process SEC filings data
            filings = []
            for filing in data.get("filings", []):
                filings.append({
                    "filing_date": filing.get("filedAt"),
                    "period_end": filing.get("periodOfReport"),
                    "form_type": filing.get("formType"),
                    "url": filing.get("linkToFilingDetails")
                })
            
            return {
                "filings": filings,
                "income_statement": [],  # Will be populated in next steps
                "balance_sheet": [],
                "cash_flow": []
            }
            
        except Exception as e:
            print(f"Error fetching SEC data for {ticker}: {e}")
            return {"error": str(e)}
    
    def fetch_multiple_companies(self, tickers: List[str]) -> Dict[str, Any]:
        """Fetch data for multiple companies"""
        results = {}
        
        for ticker in tickers:
            try:
                results[ticker] = self.fetch_company_data(ticker)
                print(f"✅ Successfully fetched data for {ticker}")
            except Exception as e:
                print(f"❌ Failed to fetch data for {ticker}: {e}")
                results[ticker] = {"error": str(e)}
        
        return results

# Helper function for easy import
def get_company_data(ticker: str) -> Dict[str, Any]:
    """Simple function to fetch single company data"""
    fetcher = DataFetcher()
    return fetcher.fetch_company_data(ticker)