from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, List, Any
from datetime import datetime

from config import Config
from data.fetcher import DataFetcher

# Initialize FastAPI app
app = FastAPI(
    title="M&A Screening API",
    description="Financial data fetching and valuation API for M&A screening",
    version="1.0.0"
)

# Add CORS middleware for n8n compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data fetcher
fetcher = DataFetcher()

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "M&A Screening API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/filings/{ticker}")
def get_company_filings(ticker: str) -> Dict[str, Any]:
    """
    Fetch complete company financial data
    This endpoint matches your n8n workflow: /filings/CRM
    """
    try:
        # Validate ticker
        ticker = ticker.upper().strip()
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker symbol is required")
        
        print(f"Processing request for ticker: {ticker}")
        
        # Fetch company data
        company_data = fetcher.fetch_company_data(ticker)
        
        # Check if there was an error in fetching
        if "error" in company_data:
            raise HTTPException(
                status_code=500, 
                detail=f"Error fetching data for {ticker}: {company_data['error']}"
            )
        
        # Format data for n8n spreadsheet creation
        # n8n expects flat structure for easy Excel export
        excel_ready_data = format_for_excel(company_data)
        
        return {
            "success": True,
            "ticker": ticker,
            "company_name": company_data.get("company_name", ""),
            "fetch_timestamp": company_data.get("fetch_timestamp"),
            "data": excel_ready_data,
            "raw_data": company_data  # Include full data for debugging
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error processing {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/filings/batch/{tickers}")
def get_multiple_companies(tickers: str) -> Dict[str, Any]:
    """
    Fetch data for multiple companies
    Usage: /filings/batch/CRM,AAPL,MSFT
    """
    try:
        # Parse comma-separated tickers
        ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
        
        if not ticker_list:
            raise HTTPException(status_code=400, detail="No valid tickers provided")
        
        if len(ticker_list) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 tickers allowed per request")
        
        print(f"Processing batch request for: {ticker_list}")
        
        # Fetch data for all companies
        results = fetcher.fetch_multiple_companies(ticker_list)
        
        # Format for Excel export
        excel_data = []
        for ticker, data in results.items():
            if "error" not in data:
                formatted = format_for_excel(data)
                formatted["ticker"] = ticker
                excel_data.append(formatted)
        
        return {
            "success": True,
            "tickers_requested": ticker_list,
            "successful_fetches": len(excel_data),
            "timestamp": datetime.now().isoformat(),
            "data": excel_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing batch request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def format_for_excel(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format company data for easy Excel export via n8n
    Returns flat dictionary with key financial metrics
    """
    market_data = company_data.get("market_data", {})
    key_metrics = company_data.get("key_metrics", {})
    
    return {
        # Company Info
        "Company_Name": company_data.get("company_name", ""),
        "Ticker": company_data.get("ticker", ""),
        "Fetch_Date": company_data.get("fetch_timestamp", ""),
        
        # Market Data
        "Current_Price": market_data.get("current_price"),
        "Market_Cap": market_data.get("market_cap"),
        "Enterprise_Value": market_data.get("enterprise_value"),
        "PE_Ratio": market_data.get("pe_ratio"),
        "PB_Ratio": market_data.get("pb_ratio"),
        "Debt_to_Equity": market_data.get("debt_to_equity"),
        
        # Financial Metrics
        "Revenue_TTM": key_metrics.get("revenue_ttm"),
        "Net_Income_TTM": key_metrics.get("net_income_ttm"),
        "Free_Cash_Flow_TTM": key_metrics.get("free_cash_flow_ttm"),
        "Total_Debt": key_metrics.get("total_debt"),
        "Total_Cash": key_metrics.get("total_cash"),
        "Book_Value": key_metrics.get("book_value"),
        
        # Placeholder for future ML predictions
        "Predicted_FCF_Next_Q": None,  # Will be filled by ML model
        "DCF_Valuation": None,         # Will be calculated in next step
        "Risk_Score": None,            # Will be calculated in next step
        "Recommendation": "PENDING"    # Will be determined by screening logic
    }

if __name__ == "__main__":
    # Validate configuration
    Config.validate()
    
    print("🚀 Starting M&A Screening API...")
    print(f"📊 Server will run on http://{Config.HOST}:{Config.PORT}")
    print("🔗 n8n endpoint: http://127.0.0.1:8000/filings/CRM")
    
    uvicorn.run(
        app, 
        host=Config.HOST, 
        port=Config.PORT,
        reload=True  # Enable auto-reload during development
    )