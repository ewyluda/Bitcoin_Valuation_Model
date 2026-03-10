"""
FastAPI backend for Bitcoin Valuation Dashboard.
"""

import os
from datetime import date, datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import uvicorn

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.models.database import init_database, get_session_maker, BTCDailyMetric
from shared.models.valuation import MetcalfeValuation, BoundaryConstants
from shared.utils.helpers import format_currency, format_number

# Configuration
DB_URL = os.getenv("DATABASE_URL", "sqlite:///btc_valuation.db")

# Initialize database on startup
engine = init_database(DB_URL)
SessionLocal = get_session_maker(engine)

# Pydantic models for API responses
class MetricsResponse(BaseModel):
    date: date
    price_usd: Optional[float]
    market_cap_usd: Optional[float]
    active_addresses: Optional[int]
    tx_count: Optional[int]
    metcalfe_upper: Optional[float]
    metcalfe_lower: Optional[float]
    fundamental_nav: Optional[float]
    valuation_signal: Optional[str]
    
    class Config:
        from_attributes = True


class LatestMetricsResponse(BaseModel):
    date: date
    price_usd: float
    price_formatted: str
    market_cap_usd: float
    market_cap_formatted: str
    active_addresses: int
    active_addresses_formatted: str
    fundamental_nav: float
    fundamental_nav_formatted: str
    valuation_signal: str
    deviation_percent: float
    

class ValuationStatusResponse(BaseModel):
    current_price: float
    fundamental_nav: float
    status: str  # overvalued, undervalued, fair_value
    deviation_percent: float
    upper_boundary: float
    lower_boundary: float
    recommendation: str


class HistoricalDataResponse(BaseModel):
    dates: List[str]
    prices: List[Optional[float]]
    market_caps: List[Optional[float]]
    active_addresses: List[Optional[int]]
    metcalfe_upper: List[Optional[float]]
    metcalfe_lower: List[Optional[float]]
    fundamental_nav: List[Optional[float]]


class CorrelationResponse(BaseModel):
    metcalfe_law: float
    generalized_metcalfe: float
    odlyzko_law: float


class StatsResponse(BaseModel):
    total_records: int
    date_range_start: Optional[date]
    date_range_end: Optional[date]
    latest_price: Optional[float]
    latest_market_cap: Optional[float]
    latest_active_addresses: Optional[int]
    avg_daily_active_addresses: Optional[float]
    max_price: Optional[float]
    min_price: Optional[float]


class SignalHistoryResponse(BaseModel):
    date: date
    signal: str
    price: float
    deviation_percent: float


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Database initialized: {DB_URL}")
    yield
    # Shutdown
    engine.dispose()

app = FastAPI(
    title="Bitcoin Valuation Dashboard API",
    description="API for Bitcoin valuation based on Metcalfe's Law",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API root with basic info."""
    return {
        "name": "Bitcoin Valuation Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "/api/metrics/latest",
            "/api/metrics/historical",
            "/api/valuation/status",
            "/api/metcalfe/boundaries",
            "/api/correlations",
            "/api/stats",
            "/api/signals/history"
        ]
    }


@app.get("/api/metrics/latest", response_model=LatestMetricsResponse)
async def get_latest_metrics(db: Session = Depends(get_db)):
    """Get the most recent metrics and valuation."""
    latest = db.query(BTCDailyMetric).order_by(
        BTCDailyMetric.date.desc()
    ).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No data available")
    
    # Calculate deviation from fundamental NAV
    deviation = 0.0
    if latest.fundamental_nav and latest.price_usd:
        # Convert log NAV to price-like scale for comparison
        # This is a simplified calculation
        deviation = ((latest.price_usd - (latest.fundamental_nav / 1e8)) / 
                    (latest.fundamental_nav / 1e8)) * 100 if latest.fundamental_nav else 0
    
    return LatestMetricsResponse(
        date=latest.date,
        price_usd=latest.price_usd or 0,
        price_formatted=format_currency(latest.price_usd),
        market_cap_usd=latest.market_cap_usd or 0,
        market_cap_formatted=format_currency(latest.market_cap_usd),
        active_addresses=latest.active_addresses or 0,
        active_addresses_formatted=format_number(latest.active_addresses),
        fundamental_nav=latest.fundamental_nav or 0,
        fundamental_nav_formatted=format_currency(latest.fundamental_nav),
        valuation_signal=latest.valuation_signal.value if latest.valuation_signal else "unknown",
        deviation_percent=round(deviation, 2)
    )


@app.get("/api/metrics/historical", response_model=HistoricalDataResponse)
async def get_historical_metrics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(None, description="Number of days to fetch (alternative to date range)"),
    db: Session = Depends(get_db)
):
    """
    Get historical metrics for charting.
    Provide either start_date+end_date OR days.
    """
    query = db.query(BTCDailyMetric)
    
    if days:
        start = date.today() - timedelta(days=days)
        query = query.filter(BTCDailyMetric.date >= start)
    else:
        if start_date:
            query = query.filter(BTCDailyMetric.date >= start_date)
        if end_date:
            query = query.filter(BTCDailyMetric.date <= end_date)
    
    records = query.order_by(BTCDailyMetric.date.asc()).all()
    
    if not records:
        return HistoricalDataResponse(
            dates=[], prices=[], market_caps=[], active_addresses=[],
            metcalfe_upper=[], metcalfe_lower=[], fundamental_nav=[]
        )
    
    return HistoricalDataResponse(
        dates=[r.date.isoformat() for r in records],
        prices=[r.price_usd for r in records],
        market_caps=[r.market_cap_usd for r in records],
        active_addresses=[r.active_addresses for r in records],
        metcalfe_upper=[r.metcalfe_upper for r in records],
        metcalfe_lower=[r.metcalfe_lower for r in records],
        fundamental_nav=[r.fundamental_nav for r in records]
    )


@app.get("/api/valuation/status", response_model=ValuationStatusResponse)
async def get_valuation_status(db: Session = Depends(get_db)):
    """Get current valuation status with recommendation."""
    latest = db.query(BTCDailyMetric).order_by(
        BTCDailyMetric.date.desc()
    ).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No data available")
    
    signal = latest.valuation_signal.value if latest.valuation_signal else "unknown"
    
    # Generate recommendation
    recommendations = {
        "overvalued": "Market cap is above Metcalfe upper boundary. Consider taking profits.",
        "undervalued": "Market cap is below Odlyzko lower boundary. Potential buying opportunity.",
        "fair_value": "Price is within fundamental boundaries. Hold or DCA.",
        "unknown": "Insufficient data for valuation."
    }
    
    # Calculate deviation
    deviation = 0.0
    if latest.market_cap_usd and latest.fundamental_nav:
        # Simple deviation calculation using log values
        log_mc = np.log(latest.market_cap_usd) if latest.market_cap_usd > 0 else 0
        deviation = ((log_mc - latest.fundamental_nav) / latest.fundamental_nav) * 100 if latest.fundamental_nav else 0
    
    return ValuationStatusResponse(
        current_price=latest.price_usd or 0,
        fundamental_nav=latest.fundamental_nav or 0,
        status=signal,
        deviation_percent=round(deviation, 2),
        upper_boundary=latest.metcalfe_upper or 0,
        lower_boundary=latest.metcalfe_lower or 0,
        recommendation=recommendations.get(signal, "No recommendation available.")
    )


@app.get("/api/metcalfe/boundaries")
async def get_metcalfe_boundaries(
    date_param: Optional[date] = Query(None, alias="date", description="Specific date (default: latest)"),
    db: Session = Depends(get_db)
):
    """Get Metcalfe upper and lower boundaries for a specific date."""
    if date_param:
        record = db.query(BTCDailyMetric).filter(
            BTCDailyMetric.date == date_param
        ).first()
    else:
        record = db.query(BTCDailyMetric).order_by(
            BTCDailyMetric.date.desc()
        ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="No data available")
    
    return {
        "date": record.date,
        "active_addresses": record.active_addresses,
        "upper_boundary": record.metcalfe_upper,
        "lower_boundary": record.metcalfe_lower,
        "fundamental_nav": record.fundamental_nav,
        "constants": {
            "a1": BoundaryConstants.a1,
            "b1": BoundaryConstants.b1,
            "a2": BoundaryConstants.a2,
            "b2": BoundaryConstants.b2,
            "sma_window": BoundaryConstants.sma_window
        }
    }


@app.get("/api/correlations", response_model=CorrelationResponse)
async def get_correlations(
    days: int = Query(365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Calculate correlation coefficients for all three law variations."""
    start_date = date.today() - timedelta(days=days)
    
    records = db.query(BTCDailyMetric).filter(
        BTCDailyMetric.date >= start_date
    ).order_by(BTCDailyMetric.date.asc()).all()
    
    if len(records) < 30:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient data. Only {len(records)} records available, need at least 30."
        )
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        'date': r.date,
        'AdrActCnt': r.active_addresses,
        'CapMrktCurUSD': r.market_cap_usd
    } for r in records])
    
    # Calculate correlations
    valuation = MetcalfeValuation()
    correlations = valuation.calculate_correlations(df)
    
    return CorrelationResponse(**correlations)


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get database statistics."""
    count = db.query(BTCDailyMetric).count()
    
    first = db.query(BTCDailyMetric).order_by(
        BTCDailyMetric.date.asc()
    ).first()
    
    latest = db.query(BTCDailyMetric).order_by(
        BTCDailyMetric.date.desc()
    ).first()
    
    # Calculate averages
    avg_aa = db.query(BTCDailyMetric).filter(
        BTCDailyMetric.active_addresses.isnot(None)
    ).all()
    
    avg_daa = sum(r.active_addresses for r in avg_aa) / len(avg_aa) if avg_aa else None
    
    # Price range
    prices = db.query(BTCDailyMetric).filter(
        BTCDailyMetric.price_usd.isnot(None)
    ).all()
    
    max_price = max(r.price_usd for r in prices) if prices else None
    min_price = min(r.price_usd for r in prices) if prices else None
    
    return StatsResponse(
        total_records=count,
        date_range_start=first.date if first else None,
        date_range_end=latest.date if latest else None,
        latest_price=latest.price_usd if latest else None,
        latest_market_cap=latest.market_cap_usd if latest else None,
        latest_active_addresses=latest.active_addresses if latest else None,
        avg_daily_active_addresses=round(avg_daa, 0) if avg_daa else None,
        max_price=max_price,
        min_price=min_price
    )


@app.get("/api/signals/history")
async def get_signal_history(
    signal_type: Optional[str] = Query(None, description="Filter by signal: overvalued, undervalued"),
    limit: int = Query(100, description="Maximum number of signals to return"),
    db: Session = Depends(get_db)
):
    """Get history of overvaluation/undervaluation signals."""
    query = db.query(BTCDailyMetric).filter(
        BTCDailyMetric.valuation_signal.isnot(None)
    )
    
    if signal_type:
        query = query.filter(
            BTCDailyMetric.valuation_signal == signal_type
        )
    else:
        # Only return non-fair-value signals
        query = query.filter(
            BTCDailyMetric.valuation_signal.in_(["overvalued", "undervalued"])
        )
    
    records = query.order_by(BTCDailyMetric.date.desc()).limit(limit).all()
    
    return [
        SignalHistoryResponse(
            date=r.date,
            signal=r.valuation_signal.value if r.valuation_signal else "unknown",
            price=r.price_usd or 0,
            deviation_percent=0.0  # Calculate if needed
        )
        for r in records
    ]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
