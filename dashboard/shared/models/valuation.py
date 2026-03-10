"""
Core data models for Bitcoin Valuation based on Metcalfe's Law.
Refactored from the original Jupyter notebook analysis.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Tuple
from enum import Enum
import numpy as np
import pandas as pd


class ValuationSignal(Enum):
    """Valuation status relative to fundamental NAV."""
    UNDERVALUED = "undervalued"      # Below lower boundary
    FAIR_VALUE = "fair_value"        # Within boundaries
    OVERVALUED = "overvalued"        # Above upper boundary
    

@dataclass
class BoundaryConstants:
    """
    Empirically-derived constants for Metcalfe Law curve fitting.
    These were determined through manual testing to find the narrowest
    channel containing actual market cap.
    """
    # Upper boundary (Metcalfe's Law: NV ~ n²)
    a1: float = 0.0       # Metcalfe intercept
    b1: float = 1.0       # Metcalfe slope
    
    # Lower boundary (Odlyzko's Law: NV ~ n×ln(n))
    a2: float = -3.48     # Odlyzko intercept
    b2: float = 1.65      # Odlyzko slope
    
    # SMA window for smoothing
    sma_window: int = 30


@dataclass
class DailyMetrics:
    """Single day of Bitcoin on-chain metrics."""
    date: date
    price_usd: Optional[float] = None
    market_cap_usd: Optional[float] = None
    active_addresses: Optional[int] = None
    tx_count: Optional[int] = None
    tx_volume_usd: Optional[float] = None
    hash_rate: Optional[float] = None
    nvt_ratio: Optional[float] = None
    
    # Calculated fields (populated after processing)
    metcalfe_upper: Optional[float] = None
    metcalfe_lower: Optional[float] = None
    fundamental_nav: Optional[float] = None
    valuation_signal: Optional[ValuationSignal] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date.isoformat(),
            "price_usd": self.price_usd,
            "market_cap_usd": self.market_cap_usd,
            "active_addresses": self.active_addresses,
            "tx_count": self.tx_count,
            "tx_volume_usd": self.tx_volume_usd,
            "hash_rate": self.hash_rate,
            "nvt_ratio": self.nvt_ratio,
            "metcalfe_upper": self.metcalfe_upper,
            "metcalfe_lower": self.metcalfe_lower,
            "fundamental_nav": self.fundamental_nav,
            "valuation_signal": self.valuation_signal.value if self.valuation_signal else None
        }


class MetcalfeValuation:
    """
    Implements Bitcoin valuation based on Metcalfe's Law and variations.
    
    The fundamental hypothesis is that Bitcoin's network value (market cap)
    is related to the square of its daily active users, similar to how
    telecommunications networks are valued according to Metcalfe's Law.
    """
    
    def __init__(self, constants: Optional[BoundaryConstants] = None):
        self.constants = constants or BoundaryConstants()
    
    def calculate_metcalfe_upper(
        self, 
        active_addresses: pd.Series,
        sma_window: Optional[int] = None
    ) -> pd.Series:
        """
        Calculate upper boundary using Metcalfe's Law (NV ~ n²).
        
        Formula: upperbound = a1 + b1 × ln(SMA_30(metcalfe_n))
        where metcalfe_n = Active_Address_Count²
        """
        window = sma_window or self.constants.sma_window
        
        # Metcalfe's Law: NV ~ n²
        metcalfe_n = active_addresses ** 2
        
        # 30-day SMA
        sma_metcalfe = metcalfe_n.rolling(window=window, min_periods=1).mean()
        
        # Log transform and apply constants
        upper_bound = self.constants.a1 + self.constants.b1 * np.log(sma_metcalfe)
        
        return upper_bound
    
    def calculate_odlyzko_lower(
        self, 
        active_addresses: pd.Series,
        sma_window: Optional[int] = None
    ) -> pd.Series:
        """
        Calculate lower boundary using Odlyzko's Law (NV ~ n×ln(n)).
        
        Formula: lowerbound = a2 + b2 × SMA_30(ln(SMA_30(odlyzko_n)))
        where odlyzko_n = Active_Address_Count × ln(Active_Address_Count)
        """
        window = sma_window or self.constants.sma_window
        
        # Odlyzko's Law: NV ~ n×ln(n)
        # Handle log of zero by replacing with NaN
        aa_safe = active_addresses.replace(0, np.nan)
        odlyzko_n = aa_safe * np.log(aa_safe)
        
        # First SMA
        sma_odlyzko_1 = odlyzko_n.rolling(window=window, min_periods=1).mean()
        
        # Log transform
        log_sma = np.log(sma_odlyzko_1.replace(0, np.nan))
        
        # Second SMA and apply constants
        lower_bound = self.constants.a2 + self.constants.b2 * log_sma.rolling(
            window=window, min_periods=1
        ).mean()
        
        return lower_bound
    
    def calculate_generalized_metcalfe(
        self,
        active_addresses: pd.Series,
        exponent: float = 1.5,
        sma_window: Optional[int] = None
    ) -> pd.Series:
        """
        Calculate generalized Metcalfe's Law (NV ~ n^exponent).
        Default exponent is 1.5 as an intermediate between Metcalfe and Odlyzko.
        """
        window = sma_window or self.constants.sma_window
        
        generalized_n = active_addresses ** exponent
        sma_generalized = generalized_n.rolling(window=window, min_periods=1).mean()
        
        return np.log(sma_generalized)
    
    def calculate_fundamental_nav(
        self,
        upper_bound: pd.Series,
        lower_bound: pd.Series
    ) -> pd.Series:
        """
        Calculate fundamental NAV as the midpoint between upper and lower boundaries.
        """
        return (upper_bound + lower_bound) / 2
    
    def determine_valuation_signal(
        self,
        actual_nav: float,
        upper_bound: float,
        lower_bound: float
    ) -> ValuationSignal:
        """
        Determine if BTC is overvalued, undervalued, or at fair value.
        """
        if actual_nav > upper_bound:
            return ValuationSignal.OVERVALUED
        elif actual_nav < lower_bound:
            return ValuationSignal.UNDERVALUED
        else:
            return ValuationSignal.FAIR_VALUE
    
    def process_dataframe(
        self,
        df: pd.DataFrame,
        date_col: str = 'date',
        aa_col: str = 'AdrActCnt',
        market_cap_col: str = 'CapMrktCurUSD'
    ) -> pd.DataFrame:
        """
        Process a DataFrame with raw metrics and add all valuation calculations.
        
        Returns DataFrame with added columns:
        - metcalfe_upper
        - metcalfe_lower
        - fundamental_nav
        - valuation_signal
        """
        result = df.copy()
        
        # Calculate boundaries
        result['metcalfe_upper'] = self.calculate_metcalfe_upper(result[aa_col])
        result['metcalfe_lower'] = self.calculate_odlyzko_lower(result[aa_col])
        result['fundamental_nav'] = self.calculate_fundamental_nav(
            result['metcalfe_upper'],
            result['metcalfe_lower']
        )
        
        # Calculate log market cap for comparison
        result['log_market_cap'] = np.log(result[market_cap_col].replace(0, np.nan))
        
        # Determine valuation signals
        result['valuation_signal'] = result.apply(
            lambda row: self.determine_valuation_signal(
                row['log_market_cap'] if pd.notna(row['log_market_cap']) else 0,
                row['metcalfe_upper'] if pd.notna(row['metcalfe_upper']) else 0,
                row['metcalfe_lower'] if pd.notna(row['metcalfe_lower']) else 0
            ).value,
            axis=1
        )
        
        return result
    
    def calculate_correlations(
        self,
        df: pd.DataFrame,
        market_cap_col: str = 'CapMrktCurUSD',
        aa_col: str = 'AdrActCnt'
    ) -> dict:
        """
        Calculate Pearson correlation between actual market cap and:
        - Metcalfe's Law (NV ~ n²)
        - Generalized Metcalfe (NV ~ n^1.5)
        - Odlyzko's Law (NV ~ n×ln(n))
        
        Returns dict with correlation coefficients.
        """
        # Remove NaN values
        clean_df = df[[market_cap_col, aa_col]].dropna()
        
        if len(clean_df) < 2:
            return {
                'metcalfe_law': 0.0,
                'generalized_metcalfe': 0.0,
                'odlyzko_law': 0.0
            }
        
        log_market_cap = np.log(clean_df[market_cap_col])
        active_addresses = clean_df[aa_col]
        
        # Metcalfe's Law (n²)
        metcalfe_n = active_addresses ** 2
        corr_metcalfe = log_market_cap.corr(np.log(metcalfe_n))
        
        # Generalized Metcalfe (n^1.5)
        generalized_n = active_addresses ** 1.5
        corr_generalized = log_market_cap.corr(np.log(generalized_n))
        
        # Odlyzko's Law (n×ln(n))
        aa_safe = active_addresses.replace(0, np.nan)
        odlyzko_n = aa_safe * np.log(aa_safe)
        corr_odlyzko = log_market_cap.corr(np.log(odlyzko_n))
        
        return {
            'metcalfe_law': round(corr_metcalfe, 4) if pd.notna(corr_metcalfe) else 0.0,
            'generalized_metcalfe': round(corr_generalized, 4) if pd.notna(corr_generalized) else 0.0,
            'odlyzko_law': round(corr_odlyzko, 4) if pd.notna(corr_odlyzko) else 0.0
        }
