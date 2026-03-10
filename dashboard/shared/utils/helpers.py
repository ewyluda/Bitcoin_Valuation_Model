"""
Utility helper functions for the dashboard.
"""

from datetime import date, datetime
from typing import Optional, Union
import math


def parse_date(date_input: Union[str, date, datetime]) -> date:
    """Parse various date inputs into date object."""
    if isinstance(date_input, date) and not isinstance(date_input, datetime):
        return date_input
    if isinstance(date_input, datetime):
        return date_input.date()
    if isinstance(date_input, str):
        # Try common formats
        formats = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_input, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_input}")
    raise ValueError(f"Unsupported date type: {type(date_input)}")


def format_currency(value: Optional[float], symbol: str = "$", decimals: int = 2) -> str:
    """Format a number as currency."""
    if value is None or math.isnan(value):
        return "N/A"
    
    if abs(value) >= 1e12:
        return f"{symbol}{value/1e12:.{decimals}f}T"
    elif abs(value) >= 1e9:
        return f"{symbol}{value/1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"{symbol}{value/1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"{symbol}{value/1e3:.{decimals}f}K"
    else:
        return f"{symbol}{value:,.{decimals}f}"


def format_number(value: Optional[float], decimals: int = 0) -> str:
    """Format a large number with K/M/B/T suffixes."""
    if value is None or math.isnan(value):
        return "N/A"
    
    if abs(value) >= 1e12:
        return f"{value/1e12:.{decimals}f}T"
    elif abs(value) >= 1e9:
        return f"{value/1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.{decimals}f}K"
    else:
        return f"{value:,.{decimals}f}"


def calculate_deviation_percent(actual: float, expected: float) -> float:
    """Calculate percentage deviation from expected value."""
    if expected == 0 or expected is None:
        return 0.0
    return ((actual - expected) / expected) * 100


def calculate_sma(series: list, window: int) -> list:
    """Calculate Simple Moving Average."""
    if not series or window <= 0:
        return series
    
    result = []
    for i in range(len(series)):
        if i < window - 1:
            # Use available data for initial values
            window_data = series[:i+1]
        else:
            window_data = series[i-window+1:i+1]
        
        # Filter out None values
        valid_data = [x for x in window_data if x is not None]
        if valid_data:
            result.append(sum(valid_data) / len(valid_data))
        else:
            result.append(None)
    
    return result


def safe_log(value: Optional[float]) -> Optional[float]:
    """Safely calculate natural log, handling edge cases."""
    if value is None or value <= 0:
        return None
    return math.log(value)


def date_range(start_date: date, end_date: date):
    """Generator for date range."""
    from datetime import timedelta
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)
