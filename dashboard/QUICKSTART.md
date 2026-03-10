# Quick Start Guide

Get the Bitcoin Valuation Dashboard running in under 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- OR: Python 3.11+ and Node.js 20+ installed

---

## Option 1: Docker (Fastest - 2 minutes)

```bash
cd dashboard

# 1. Start all services
docker-compose up --build -d

# 2. Import your existing data (optional)
docker-compose exec pipeline python -m pipeline.src.scheduler import --csv resources/btc.csv

# 3. Open dashboard
open http://localhost:3000

# 4. View API docs
open http://localhost:8000/docs
```

To stop:
```bash
docker-compose down
```

---

## Option 2: Manual Setup (5 minutes)

### Step 1: Backend API

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt
pip install -r pipeline/requirements.txt

# Initialize database
python -c "from shared.models.database import init_database; init_database('sqlite:///data/btc_valuation.db')"

# Start API server
cd api/src
uvicorn main:app --reload --port 8000
```

API is now running at http://localhost:8000

### Step 2: Import Data

In a new terminal:

```bash
# Import your existing btc.csv data
python -m pipeline.src.scheduler import --csv resources/btc.csv

# Backfill recent data
python -m pipeline.src.scheduler backfill --start-date 2021-04-07
```

### Step 3: Frontend

```bash
cd webapp
npm install
npm run dev
```

Dashboard is now running at http://localhost:3000

---

## Verify Installation

### Check API Health
```bash
curl http://localhost:8000/health
```

### Test Endpoints
```bash
# Get latest metrics
curl http://localhost:8000/api/metrics/latest

# Get historical data
curl http://localhost:8000/api/metrics/historical?days=30

# Get valuation status
curl http://localhost:8000/api/valuation/status
```

### View in Browser

1. **Dashboard**: http://localhost:3000
   - Real-time BTC price and valuation
   - Interactive charts
   - Time range selector

2. **API Docs**: http://localhost:8000/docs
   - Interactive Swagger UI
   - Test all endpoints
   - View schemas

---

## Common Issues

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different ports
docker-compose -p btc-dashboard up
```

### Database Locked
```bash
# Remove and recreate database
rm data/btc_valuation.db
docker-compose restart
```

### Frontend Can't Connect to API
```bash
# Check API is running
curl http://localhost:8000/health

# Update .env file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > webapp/.env.local
```

---

## Next Steps

1. **Explore the Dashboard**
   - View current valuation signal
   - Change time ranges (30D/90D/180D/1Y/ALL)
   - Check correlation statistics

2. **Review the Code**
   - `shared/models/valuation.py` - Your refactored notebook logic
   - `api/src/main.py` - API endpoints
   - `webapp/app/page.tsx` - Dashboard UI

3. **Customize**
   - Edit constants in `shared/models/valuation.py`
   - Add new metrics to the fetcher
   - Modify chart styling in components

4. **Deploy**
   - See README.md for deployment options
   - Railway, Render, or VPS

---

## Makefile Commands

```bash
make help              # Show all commands
make up               # Start with Docker
make dev-backend      # Run backend locally
make dev-frontend     # Run frontend locally
make db-import        # Import CSV data
make db-backfill      # Fetch new data
make logs             # View logs
make down             # Stop everything
make clean            # Clean build files
```

---

## Data Pipeline

The pipeline automatically runs daily at midnight UTC to fetch new data.

To run manually:
```bash
# With Docker
docker-compose exec pipeline python -m pipeline.src.scheduler run

# Without Docker
python -m pipeline.src.scheduler run
```

To start scheduler:
```bash
# Runs continuously, executes daily
docker-compose exec pipeline python -m pipeline.src.scheduler schedule
```

---

**You're all set!** 🚀

Visit http://localhost:3000 to see your live Bitcoin Valuation Dashboard.
