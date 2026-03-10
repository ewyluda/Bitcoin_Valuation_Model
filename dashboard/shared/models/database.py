"""
SQLAlchemy database models for Bitcoin Valuation Dashboard.
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    create_engine, Column, Integer, Float, Date, DateTime, 
    String, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class ValuationSignalDB(str, enum.Enum):
    """Database enum for valuation signals."""
    UNDERVALUED = "undervalued"
    FAIR_VALUE = "fair_value"
    OVERVALUED = "overvalued"


class BTCDailyMetric(Base):
    """Daily Bitcoin on-chain metrics."""
    __tablename__ = "btc_daily_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    
    # Raw metrics from API
    price_usd = Column(Float, nullable=True)
    market_cap_usd = Column(Float, nullable=True)
    active_addresses = Column(Integer, nullable=True)
    tx_count = Column(Integer, nullable=True)
    tx_volume_usd = Column(Float, nullable=True)
    hash_rate = Column(Float, nullable=True)
    nvt_ratio = Column(Float, nullable=True)
    
    # Calculated valuation metrics
    metcalfe_upper = Column(Float, nullable=True)
    metcalfe_lower = Column(Float, nullable=True)
    fundamental_nav = Column(Float, nullable=True)
    valuation_signal = Column(SQLEnum(ValuationSignalDB), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    data_source = Column(String(50), default="bgeometrics")
    
    __table_args__ = (
        Index('idx_date_signal', 'date', 'valuation_signal'),
        UniqueConstraint('date', name='uq_date'),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
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
            "valuation_signal": self.valuation_signal.value if self.valuation_signal else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DataSyncLog(Base):
    """Log of data synchronization runs."""
    __tablename__ = "data_sync_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_date = Column(DateTime, server_default=func.now())
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    records_processed = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, success, error
    error_message = Column(String(500), nullable=True)
    data_source = Column(String(50), default="bgeometrics")


class AlertHistory(Base):
    """History of valuation alerts."""
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    alert_type = Column(String(20), nullable=False)  # overvalued, undervalued
    price_usd = Column(Float, nullable=False)
    fundamental_nav = Column(Float, nullable=False)
    deviation_percent = Column(Float, nullable=False)
    sent = Column(Integer, default=0)  # 0 = not sent, 1 = sent
    sent_at = Column(DateTime, nullable=True)


def init_database(db_url: str = "sqlite:///btc_valuation.db"):
    """Initialize database with all tables."""
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session_maker(engine):
    """Get session maker bound to engine."""
    return sessionmaker(bind=engine)
