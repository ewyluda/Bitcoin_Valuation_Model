"""
APScheduler-based data pipeline scheduler.
Runs daily to fetch new data and update valuations.
"""

import logging
import os
import sys
import time
from datetime import date, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from pipeline.src.fetcher import BGeometricsFetcher, CoinMetricsFetcher
from pipeline.src.processor import DataProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineScheduler:
    """
    Scheduler for running the Bitcoin valuation data pipeline.
    """
    
    def __init__(
        self,
        db_url: str = "sqlite:///btc_valuation.db",
        primary_source: str = "bgeometrics"
    ):
        self.db_url = db_url
        self.primary_source = primary_source
        self.scheduler = BackgroundScheduler()
        self.processor = DataProcessor(db_url)
        
        # Initialize fetchers
        if primary_source == "bgeometrics":
            self.fetcher = BGeometricsFetcher()
        else:
            self.fetcher = CoinMetricsFetcher()
        
        # Backup fetcher
        self.backup_fetcher = CoinMetricsFetcher()
        
        # Add listeners
        self.scheduler.add_listener(
            self._job_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )
    
    def _job_listener(self, event):
        """Listen for job events."""
        if event.exception:
            logger.error(f"Job crashed: {event.job_id}")
        else:
            logger.info(f"Job executed: {event.job_id}")
    
    def run_daily_sync(self):
        """
        Run the daily data sync.
        Fetches new data from API and updates the database.
        """
        logger.info("=" * 50)
        logger.info("Starting daily data sync")
        logger.info("=" * 50)
        
        try:
            # Determine date range to fetch
            latest_db_date = self.processor.get_latest_date()
            
            if latest_db_date:
                # Fetch from the day after latest to today
                start_date = latest_db_date + timedelta(days=1)
            else:
                # No data in DB, fetch last 90 days
                start_date = date.today() - timedelta(days=90)
            
            end_date = date.today()
            
            # Don't fetch future dates
            if start_date > end_date:
                logger.info("Database is already up to date")
                return
            
            logger.info(f"Fetching data from {start_date} to {end_date}")
            
            # Try primary fetcher
            try:
                if hasattr(self.fetcher, 'fetch_all_metrics'):
                    df = self.fetcher.fetch_all_metrics(start_date, end_date)
                else:
                    # CoinMetrics fallback
                    df = self.fetcher.fetch_metrics(
                        ["AdrActCnt", "CapMrktCurUSD", "PriceUSD", "TxCnt"],
                        start_date, end_date
                    )
            except Exception as e:
                logger.warning(f"Primary fetcher failed: {e}. Trying backup...")
                df = self.backup_fetcher.fetch_metrics(
                    ["AdrActCnt", "CapMrktCurUSD", "PriceUSD", "TxCnt"],
                    start_date, end_date
                )
            
            if df.empty:
                logger.warning("No data fetched from API")
                return
            
            # Process and save
            sync_log = self.processor.sync_data(df, start_date, end_date)
            
            logger.info(f"Sync completed: {sync_log.records_inserted} new, {sync_log.records_updated} updated")
            
        except Exception as e:
            logger.error(f"Daily sync failed: {e}", exc_info=True)
    
    def run_backfill(
        self,
        start_date: date,
        end_date: Optional[date] = None,
        batch_size: int = 365
    ):
        """
        Backfill historical data in batches.
        Useful for initial population or catching up after downtime.
        """
        end_date = end_date or date.today()
        
        logger.info(f"Starting backfill from {start_date} to {end_date}")
        
        current = start_date
        while current <= end_date:
            batch_end = min(current + timedelta(days=batch_size - 1), end_date)
            
            logger.info(f"Fetching batch: {current} to {batch_end}")
            
            try:
                if hasattr(self.fetcher, 'fetch_all_metrics'):
                    df = self.fetcher.fetch_all_metrics(current, batch_end)
                else:
                    df = self.fetcher.fetch_metrics(
                        ["AdrActCnt", "CapMrktCurUSD", "PriceUSD", "TxCnt"],
                        current, batch_end
                    )
                
                if not df.empty:
                    self.processor.sync_data(df, current, batch_end)
                
            except Exception as e:
                logger.error(f"Failed to fetch batch {current} to {batch_end}: {e}")
            
            current = batch_end + timedelta(days=1)
            
            # Rate limiting
            time.sleep(1)
        
        logger.info("Backfill completed")
    
    def import_legacy_csv(self, csv_path: str):
        """
        Import existing btc.csv data from the original notebook.
        """
        logger.info(f"Importing legacy data from {csv_path}")
        
        try:
            inserted, updated = self.processor.import_from_csv(csv_path, "legacy_csv")
            logger.info(f"Legacy import: {inserted} inserted, {updated} updated")
        except Exception as e:
            logger.error(f"Legacy import failed: {e}")
    
    def schedule_daily_job(self, hour: int = 0, minute: int = 5):
        """
        Schedule the daily sync job.
        Default: Run at 00:05 UTC daily (after markets close).
        """
        trigger = CronTrigger(hour=hour, minute=minute)
        
        self.scheduler.add_job(
            self.run_daily_sync,
            trigger=trigger,
            id="daily_btc_sync",
            name="Daily Bitcoin Data Sync",
            replace_existing=True
        )
        
        logger.info(f"Scheduled daily sync at {hour:02d}:{minute:02d} UTC")
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.scheduler.running


def run_pipeline_once(db_url: str = "sqlite:///btc_valuation.db"):
    """
    Run the pipeline once (for manual execution or testing).
    """
    scheduler = PipelineScheduler(db_url)
    scheduler.run_daily_sync()


def start_scheduler(db_url: str = "sqlite:///btc_valuation.db"):
    """
    Start the background scheduler.
    """
    scheduler = PipelineScheduler(db_url)
    scheduler.schedule_daily_job()
    scheduler.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bitcoin Valuation Pipeline")
    parser.add_argument(
        "command",
        choices=["run", "schedule", "backfill", "import"],
        help="Command to execute"
    )
    parser.add_argument("--db", default="sqlite:///btc_valuation.db", help="Database URL")
    parser.add_argument("--start-date", help="Start date for backfill (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date for backfill (YYYY-MM-DD)")
    parser.add_argument("--csv", help="Path to CSV file for import")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_pipeline_once(args.db)
    
    elif args.command == "schedule":
        start_scheduler(args.db)
    
    elif args.command == "backfill":
        if not args.start_date:
            print("Error: --start-date required for backfill")
            sys.exit(1)
        
        scheduler = PipelineScheduler(args.db)
        start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(args.end_date, "%Y-%m-%d").date() if args.end_date else date.today()
        scheduler.run_backfill(start, end)
    
    elif args.command == "import":
        if not args.csv:
            print("Error: --csv required for import")
            sys.exit(1)
        
        scheduler = PipelineScheduler(args.db)
        scheduler.import_legacy_csv(args.csv)
