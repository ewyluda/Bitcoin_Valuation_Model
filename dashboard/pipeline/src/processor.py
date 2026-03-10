"""
Data Processor: Fetches data, runs Metcalfe calculations, and saves to database.
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.models.valuation import MetcalfeValuation, BoundaryConstants, ValuationSignal
from shared.models.database import (
    BTCDailyMetric, DataSyncLog, ValuationSignalDB, init_database, get_session_maker
)
from shared.utils.helpers import parse_date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes Bitcoin data: fetch → calculate → store.
    """
    
    def __init__(self, db_url: str = "sqlite:///btc_valuation.db"):
        self.db_url = db_url
        self.engine = init_database(db_url)
        self.Session = get_session_maker(self.engine)
        self.valuation = MetcalfeValuation(BoundaryConstants())
    
    def _row_to_model(self, row: pd.Series) -> BTCDailyMetric:
        """Convert DataFrame row to database model."""
        
        # Map valuation signal
        signal = None
        if 'valuation_signal' in row and pd.notna(row['valuation_signal']):
            try:
                signal = ValuationSignalDB(row['valuation_signal'])
            except ValueError:
                signal = None
        
        return BTCDailyMetric(
            date=parse_date(row['date']),
            price_usd=row.get('PriceUSD'),
            market_cap_usd=row.get('CapMrktCurUSD'),
            active_addresses=int(row['AdrActCnt']) if pd.notna(row.get('AdrActCnt')) else None,
            tx_count=int(row['TxCnt']) if pd.notna(row.get('TxCnt')) else None,
            tx_volume_usd=row.get('TxTfrValUSD'),
            hash_rate=row.get('HashRate'),
            nvt_ratio=row.get('NVTAdj'),
            metcalfe_upper=row.get('metcalfe_upper'),
            metcalfe_lower=row.get('metcalfe_lower'),
            fundamental_nav=row.get('fundamental_nav'),
            valuation_signal=signal
        )
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run Metcalfe calculations on raw data.
        """
        logger.info(f"Processing {len(df)} records with Metcalfe valuation")
        
        if df.empty:
            return df
        
        # Ensure required columns exist
        required = ['AdrActCnt', 'CapMrktCurUSD']
        for col in required:
            if col not in df.columns:
                logger.error(f"Missing required column: {col}")
                return df
        
        # Run valuation calculations
        processed = self.valuation.process_dataframe(df)
        
        logger.info("Metcalfe calculations completed")
        return processed
    
    def save_to_database(
        self, 
        df: pd.DataFrame,
        source: str = "bgeometrics"
    ) -> Tuple[int, int]:
        """
        Save processed data to database.
        Returns (records_inserted, records_updated).
        """
        if df.empty:
            logger.warning("No data to save")
            return 0, 0
        
        session = self.Session()
        inserted = 0
        updated = 0
        
        try:
            for _, row in df.iterrows():
                date_val = parse_date(row['date'])
                
                # Check if record exists
                existing = session.query(BTCDailyMetric).filter(
                    BTCDailyMetric.date == date_val
                ).first()
                
                metric = self._row_to_model(row)
                metric.data_source = source
                
                if existing:
                    # Update existing record
                    existing.price_usd = metric.price_usd
                    existing.market_cap_usd = metric.market_cap_usd
                    existing.active_addresses = metric.active_addresses
                    existing.tx_count = metric.tx_count
                    existing.tx_volume_usd = metric.tx_volume_usd
                    existing.hash_rate = metric.hash_rate
                    existing.nvt_ratio = metric.nvt_ratio
                    existing.metcalfe_upper = metric.metcalfe_upper
                    existing.metcalfe_lower = metric.metcalfe_lower
                    existing.fundamental_nav = metric.fundamental_nav
                    existing.valuation_signal = metric.valuation_signal
                    existing.data_source = source
                    updated += 1
                else:
                    # Insert new record
                    session.add(metric)
                    inserted += 1
            
            session.commit()
            logger.info(f"Database updated: {inserted} inserted, {updated} updated")
            return inserted, updated
            
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def sync_data(
        self,
        df: pd.DataFrame,
        start_date: date,
        end_date: date,
        source: str = "bgeometrics"
    ) -> DataSyncLog:
        """
        Full sync pipeline: process and save data, create sync log.
        """
        logger.info(f"Starting data sync from {start_date} to {end_date}")
        
        sync_log = DataSyncLog(
            start_date=start_date,
            end_date=end_date,
            status="pending",
            data_source=source
        )
        
        session = self.Session()
        session.add(sync_log)
        session.commit()
        
        try:
            # Process data
            processed_df = self.process_dataframe(df)
            
            # Save to database
            inserted, updated = self.save_to_database(processed_df, source)
            
            # Update sync log
            sync_log.status = "success"
            sync_log.records_processed = len(processed_df)
            sync_log.records_inserted = inserted
            sync_log.records_updated = updated
            
            session.commit()
            logger.info(f"Sync completed successfully: {inserted} inserted, {updated} updated")
            
        except Exception as e:
            sync_log.status = "error"
            sync_log.error_message = str(e)[:500]
            session.commit()
            logger.error(f"Sync failed: {e}")
            raise
        finally:
            session.close()
        
        return sync_log
    
    def get_latest_date(self) -> Optional[date]:
        """Get the most recent date in the database."""
        session = self.Session()
        try:
            latest = session.query(BTCDailyMetric).order_by(
                BTCDailyMetric.date.desc()
            ).first()
            return latest.date if latest else None
        finally:
            session.close()
    
    def get_date_range(self) -> Tuple[Optional[date], Optional[date]]:
        """Get the date range available in the database."""
        session = self.Session()
        try:
            min_date = session.query(BTCDailyMetric).order_by(
                BTCDailyMetric.date.asc()
            ).first()
            max_date = session.query(BTCDailyMetric).order_by(
                BTCDailyMetric.date.desc()
            ).first()
            return (
                min_date.date if min_date else None,
                max_date.date if max_date else None
            )
        finally:
            session.close()
    
    def export_to_csv(self, filepath: str, start_date: Optional[date] = None):
        """Export database contents to CSV (for backup/analysis)."""
        session = self.Session()
        try:
            query = session.query(BTCDailyMetric)
            if start_date:
                query = query.filter(BTCDailyMetric.date >= start_date)
            
            records = query.all()
            
            if not records:
                logger.warning("No records to export")
                return
            
            df = pd.DataFrame([r.to_dict() for r in records])
            df.to_csv(filepath, index=False)
            logger.info(f"Exported {len(df)} records to {filepath}")
            
        finally:
            session.close()
    
    def import_from_csv(
        self, 
        filepath: str,
        source: str = "csv_import"
    ) -> Tuple[int, int]:
        """
        Import data from CSV file (useful for migrating existing btc.csv).
        """
        logger.info(f"Importing data from {filepath}")
        
        df = pd.read_csv(filepath)
        
        # Map column names from old format if needed
        column_mapping = {
            'AdrActCnt': 'AdrActCnt',
            'CapMrktCurUSD': 'CapMrktCurUSD',
            'PriceUSD': 'PriceUSD',
            'TxCnt': 'TxCnt',
            'TxTfrValUSD': 'TxTfrValUSD',
            'HashRate': 'HashRate',
            'NVTAdj': 'NVTAdj'
        }
        
        # Ensure date column exists
        if 'date' not in df.columns:
            raise ValueError("CSV must have a 'date' column")
        
        # Process and save
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        processed_df = self.process_dataframe(df)
        return self.save_to_database(processed_df, source)


if __name__ == "__main__":
    # Test the processor
    processor = DataProcessor()
    
    # Check database status
    min_date, max_date = processor.get_date_range()
    print(f"Database date range: {min_date} to {max_date}")
