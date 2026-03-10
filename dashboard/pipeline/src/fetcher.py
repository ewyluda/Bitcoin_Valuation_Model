"""
BGeometrics API Data Fetcher for Bitcoin on-chain metrics.

API Documentation: https://charts.bgeometrics.com/bitcoin_api.html
"""

import os
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import json

import requests
import pandas as pd
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BGeometricsConfig(BaseModel):
    """Configuration for BGeometrics API."""
    base_url: str = "https://charts.bgeometrics.com/api"
    api_key: Optional[str] = None
    timeout: int = 30
    retries: int = 3


class BGeometricsFetcher:
    """
    Fetches Bitcoin on-chain data from BGeometrics API.
    
    Free tier provides:
    - Daily Active Addresses
    - Market Cap (Realized Cap, Market Cap)
    - Transaction data (volume, count, fees)
    - Price data
    """
    
    def __init__(self, config: Optional[BGeometricsConfig] = None):
        self.config = config or BGeometricsConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "BTC-Valuation-Dashboard/1.0"
        })
        
        if self.config.api_key:
            self.session.headers.update({"X-API-Key": self.config.api_key})
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request with retry logic."""
        url = f"{self.config.base_url}/{endpoint}"
        
        for attempt in range(self.config.retries):
            try:
                logger.debug(f"Requesting {url} (attempt {attempt + 1})")
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.config.retries - 1:
                    raise
        
        return {}
    
    def fetch_active_addresses(
        self, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch Daily Active Addresses (DAA) data.
        
        This is the primary metric for Metcalfe's Law calculations.
        """
        logger.info(f"Fetching active addresses from {start_date} to {end_date}")
        
        # BGeometrics endpoint for active addresses
        # Format: timestamp, value
        endpoint = "addresses/active"
        
        params = {}
        if start_date:
            params["start"] = int(datetime.combine(start_date, datetime.min.time()).timestamp())
        if end_date:
            params["end"] = int(datetime.combine(end_date, datetime.min.time()).timestamp())
        
        try:
            data = self._make_request(endpoint, params)
            
            # Convert to DataFrame
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data, columns=["timestamp", "active_addresses"])
                df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
                df = df.drop("timestamp", axis=1)
                df = df.sort_values("date").reset_index(drop=True)
                return df
            else:
                logger.warning("Empty response for active addresses")
                return pd.DataFrame(columns=["date", "active_addresses"])
                
        except Exception as e:
            logger.error(f"Failed to fetch active addresses: {e}")
            return pd.DataFrame(columns=["date", "active_addresses"])
    
    def fetch_market_cap(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch Market Cap data.
        """
        logger.info(f"Fetching market cap from {start_date} to {end_date}")
        
        endpoint = "market/cap"
        
        params = {}
        if start_date:
            params["start"] = int(datetime.combine(start_date, datetime.min.time()).timestamp())
        if end_date:
            params["end"] = int(datetime.combine(end_date, datetime.min.time()).timestamp())
        
        try:
            data = self._make_request(endpoint, params)
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data, columns=["timestamp", "market_cap"])
                df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
                df = df.drop("timestamp", axis=1)
                df = df.sort_values("date").reset_index(drop=True)
                return df
            else:
                logger.warning("Empty response for market cap")
                return pd.DataFrame(columns=["date", "market_cap"])
                
        except Exception as e:
            logger.error(f"Failed to fetch market cap: {e}")
            return pd.DataFrame(columns=["date", "market_cap"])
    
    def fetch_price(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch BTC price in USD.
        """
        logger.info(f"Fetching price from {start_date} to {end_date}")
        
        endpoint = "price/usd"
        
        params = {}
        if start_date:
            params["start"] = int(datetime.combine(start_date, datetime.min.time()).timestamp())
        if end_date:
            params["end"] = int(datetime.combine(end_date, datetime.min.time()).timestamp())
        
        try:
            data = self._make_request(endpoint, params)
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data, columns=["timestamp", "price"])
                df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
                df = df.drop("timestamp", axis=1)
                df = df.sort_values("date").reset_index(drop=True)
                return df
            else:
                logger.warning("Empty response for price")
                return pd.DataFrame(columns=["date", "price"])
                
        except Exception as e:
            logger.error(f"Failed to fetch price: {e}")
            return pd.DataFrame(columns=["date", "price"])
    
    def fetch_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch transaction count data.
        """
        logger.info(f"Fetching transaction count from {start_date} to {end_date}")
        
        endpoint = "transactions/count"
        
        params = {}
        if start_date:
            params["start"] = int(datetime.combine(start_date, datetime.min.time()).timestamp())
        if end_date:
            params["end"] = int(datetime.combine(end_date, datetime.min.time()).timestamp())
        
        try:
            data = self._make_request(endpoint, params)
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data, columns=["timestamp", "tx_count"])
                df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
                df = df.drop("timestamp", axis=1)
                df = df.sort_values("date").reset_index(drop=True)
                return df
            else:
                logger.warning("Empty response for transactions")
                return pd.DataFrame(columns=["date", "tx_count"])
                
        except Exception as e:
            logger.error(f"Failed to fetch transactions: {e}")
            return pd.DataFrame(columns=["date", "tx_count"])
    
    def fetch_all_metrics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch and merge all metrics into a single DataFrame.
        """
        logger.info(f"Fetching all metrics from {start_date} to {end_date}")
        
        # Fetch all individual metrics
        df_active = self.fetch_active_addresses(start_date, end_date)
        df_market = self.fetch_market_cap(start_date, end_date)
        df_price = self.fetch_price(start_date, end_date)
        df_tx = self.fetch_transactions(start_date, end_date)
        
        # Merge on date
        merged = df_active
        
        if not df_market.empty:
            merged = merged.merge(df_market, on="date", how="outer")
        
        if not df_price.empty:
            merged = merged.merge(df_price, on="date", how="outer")
        
        if not df_tx.empty:
            merged = merged.merge(df_tx, on="date", how="outer")
        
        # Rename columns to match our schema
        column_mapping = {
            "active_addresses": "AdrActCnt",
            "market_cap": "CapMrktCurUSD",
            "price": "PriceUSD",
            "tx_count": "TxCnt"
        }
        merged = merged.rename(columns=column_mapping)
        
        # Sort by date
        merged = merged.sort_values("date").reset_index(drop=True)
        
        logger.info(f"Fetched {len(merged)} records with {merged.shape[1]} columns")
        
        return merged
    
    def fetch_latest(self, days: int = 30) -> pd.DataFrame:
        """
        Fetch the most recent N days of data.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return self.fetch_all_metrics(start_date, end_date)


# Alternative: CoinMetrics Community API as backup
class CoinMetricsFetcher:
    """
    Backup fetcher using CoinMetrics Community API.
    Free tier: 10 requests per 6 seconds, no API key needed.
    """
    
    def __init__(self):
        self.base_url = "https://community-api.coinmetrics.io/v4"
        self.session = requests.Session()
    
    def fetch_metrics(
        self,
        metrics: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch metrics from CoinMetrics.
        
        Available metrics:
        - AdrActCnt: Active addresses count
        - CapMrktCurUSD: Market cap
        - PriceUSD: Price
        - TxCnt: Transaction count
        """
        endpoint = f"{self.base_url}/timeseries/asset-metrics"
        
        params = {
            "assets": "btc",
            "metrics": ",".join(metrics),
            "frequency": "1d"
        }
        
        if start_date:
            params["start_time"] = start_date.isoformat()
        if end_date:
            params["end_time"] = end_date.isoformat()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data:
                df = pd.DataFrame(data["data"])
                df["time"] = pd.to_datetime(df["time"]).dt.date
                df = df.rename(columns={"time": "date"})
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"CoinMetrics fetch failed: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    # Test the fetcher
    fetcher = BGeometricsFetcher()
    
    # Fetch last 30 days
    df = fetcher.fetch_latest(days=30)
    if not df.empty:
        print(df.head())
        print(f"\nShape: {df.shape}")
        print(f"\nColumns: {df.columns.tolist()}")
    else:
        print("No data fetched - API may be unavailable")
