# Project Structure

```
dashboard/
│
├── 📁 api/                          # FastAPI Backend
│   ├── requirements.txt
│   └── src/
│       ├── __init__.py
│       └── main.py                  # REST API with all endpoints
│
├── 📁 pipeline/                     # Data Pipeline
│   ├── requirements.txt
│   └── src/
│       ├── __init__.py
│       ├── fetcher.py               # BGeometrics API client
│       ├── processor.py             # Metcalfe calculations & DB ops
│       └── scheduler.py             # APScheduler daily sync
│
├── 📁 shared/                       # Shared Python modules
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── valuation.py             # Metcalfe Law logic (refactored)
│   │   └── database.py              # SQLAlchemy models
│   └── utils/
│       ├── __init__.py
│       └── helpers.py               # Utility functions
│
├── 📁 webapp/                       # Next.js Frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── next.config.js
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx                 # Main dashboard page
│   ├── components/
│   │   ├── ui/
│   │   │   └── Card.tsx             # Reusable card components
│   │   ├── charts/
│   │   │   └── MetcalfeChart.tsx    # Recharts visualizations
│   │   └── dashboard/
│   │       ├── Header.tsx
│   │       ├── StatsGrid.tsx
│   │       └── Methodology.tsx
│   ├── lib/
│   │   ├── api.ts                   # API client
│   │   └── utils.ts                 # Helper functions
│   └── types/
│       └── index.ts                 # TypeScript interfaces
│
├── 🐳 Dockerfile.api                # API container
├── 🐳 Dockerfile.pipeline           # Pipeline container
├── 🐳 Dockerfile.webapp             # Frontend container
├── 📋 docker-compose.yml            # Full stack orchestration
├── 📋 Makefile                      # Development commands
├── 🔧 .env.example                  # Environment template
└── 📖 README.md                     # Full documentation
```

## Key Components

### Backend (FastAPI)
- **Main API** (`api/src/main.py`): 9 endpoints for metrics, valuation, correlations
- **Auto-generated docs**: Available at `/docs` (Swagger UI)
- **CORS enabled**: Ready for frontend integration

### Data Pipeline
- **Fetcher** (`pipeline/src/fetcher.py`): BGeometrics API with CoinMetrics backup
- **Processor** (`pipeline/src/processor.py`): Runs Metcalfe calculations, saves to DB
- **Scheduler** (`pipeline/src/scheduler.py`): Daily sync at midnight UTC

### Frontend (Next.js)
- **Dashboard** (`webapp/app/page.tsx`): Main page with all visualizations
- **Charts** (`components/charts/`): Interactive Recharts components
- **Real-time updates**: Auto-refreshes every 5 minutes
- **Dark theme**: Crypto-native aesthetic

### Shared Models
- **Valuation** (`shared/models/valuation.py`): Core Metcalfe/Odlyzko calculations
- **Database** (`shared/models/database.py`): SQLAlchemy ORM models

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  BGeometrics API                                            │
│  (Daily Active Addresses, Market Cap, Price, Tx Count)     │
└───────────────────────┬─────────────────────────────────────┘
                        │ Daily @ 00:00 UTC
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Data Pipeline                                              │
│  • Fetch from API                                           │
│  • Calculate Metcalfe boundaries                            │
│  • Determine valuation signals                              │
│  • Save to Database                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  SQLite / PostgreSQL                                        │
│  • btc_daily_metrics (main table)                           │
│  • data_sync_logs (pipeline runs)                           │
│  • alert_history (valuation signals)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Backend                                            │
│  • /api/metrics/latest                                      │
│  • /api/metrics/historical                                  │
│  • /api/valuation/status                                    │
│  • /api/correlations                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP / WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Next.js Frontend                                           │
│  • Interactive charts (Recharts)                            │
│  • Real-time valuation display                              │
│  • Time range selection (30D/90D/180D/1Y/ALL)              │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/api/metrics/latest` | Current BTC metrics |
| GET | `/api/metrics/historical` | Time-series data |
| GET | `/api/valuation/status` | Valuation signal |
| GET | `/api/metcalfe/boundaries` | Boundary values |
| GET | `/api/correlations` | Correlation stats |
| GET | `/api/stats` | Database stats |
| GET | `/api/signals/history` | Signal history |

## Quick Commands

```bash
# Full stack with Docker
make up

# Individual services
make dev-backend      # API on :8000
make dev-frontend     # Next.js on :3000
make dev-pipeline     # Run pipeline once

# Data operations
make db-import        # Import legacy CSV
make db-backfill      # Fetch historical data

# View logs
make logs

# Stop everything
make down
```
