# Bitcoin Valuation Dashboard

A modern, real-time web application for Bitcoin valuation based on **Metcalfe's Law** and on-chain metrics.

![Dashboard Preview](docs/preview.png)

---

## Features

### 📊 Real-time Valuation
- Live Bitcoin price vs Fundamental NAV comparison
- Color-coded valuation signals (Overvalued 🔴 / Fair 🟡 / Undervalued 🟢)
- Deviation percentage from fundamental value

### 📈 Interactive Charts
- **Metcalfe Boundaries Chart**: Market cap with upper/lower boundaries
- **Price vs NAV Chart**: Actual vs fundamental value over time
- Time range selection (30D / 90D / 180D / 1Y / ALL)
- Hover tooltips with detailed metrics

### 🔄 Automated Data Pipeline
- Daily sync from BGeometrics API (midnight UTC)
- SQLite/PostgreSQL database for historical data
- Automatic backfill capabilities
- Data integrity checks

### 📱 Modern UI/UX
- Dark theme (crypto-native aesthetic)
- Responsive design (desktop & mobile)
- Real-time updates (auto-refresh every 5 minutes)
- Smooth animations and transitions

---

## Quick Start

### Prerequisites

- Docker & Docker Compose **OR**
- Python 3.11+ and Node.js 20+

### Option 1: Docker (Recommended - 2 minutes)

```bash
cd dashboard

# Copy environment file
cp .env.example .env

# Build and start all services
docker-compose up --build -d

# Access the dashboard
open http://localhost:3000
```

To stop:
```bash
docker-compose down
```

### Option 2: Manual Setup (5 minutes)

**1. Backend (FastAPI)**

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

**2. Data Pipeline**

In a new terminal:

```bash
# Import your existing btc.csv data
python -m pipeline.src.scheduler import --csv ../../resources/btc.csv

# Backfill recent data
python -m pipeline.src.scheduler backfill --start-date 2021-04-07
```

**3. Frontend (Next.js)**

```bash
cd webapp
npm install
npm run dev
```

Dashboard is now running at http://localhost:3000

---

## Architecture

```
dashboard/
├── 📁 api/                    # FastAPI Backend
│   ├── requirements.txt
│   └── src/
│       └── main.py           # REST API endpoints
├── 📁 pipeline/               # Data Pipeline
│   ├── requirements.txt
│   └── src/
│       ├── fetcher.py        # BGeometrics API client
│       ├── processor.py      # Metcalfe calculations
│       └── scheduler.py      # APScheduler daily sync
├── 📁 shared/                 # Shared Python modules
│   ├── models/
│   │   ├── valuation.py      # Metcalfe logic (refactored)
│   │   └── database.py       # SQLAlchemy models
│   └── utils/
│       └── helpers.py        # Utility functions
├── 📁 webapp/                 # Next.js Frontend
│   ├── app/                  # App Router
│   ├── components/           # React components
│   ├── lib/                  # API client & helpers
│   └── types/                # TypeScript interfaces
├── 🐳 Dockerfile.api          # API container
├── 🐳 Dockerfile.pipeline     # Pipeline container
├── 🐳 Dockerfile.webapp       # Frontend container
└── 📋 docker-compose.yml      # Full stack orchestration
```

---

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  BGeometrics    │────▶│  Data Pipeline   │────▶│  PostgreSQL DB  │
│     API         │     │  (Daily @ 00:00) │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                           ┌──────────────────────────────┘
                           ▼
                    ┌──────────────┐
                    │  FastAPI     │
                    │  Backend     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │ Next.js │  │ Alerts  │  │  API    │
        │Dashboard│  │ Service │  │ Clients │
        └─────────┘  └─────────┘  └─────────┘
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /health` | Health check |
| `GET /api/metrics/latest` | Current BTC price, NAV, valuation signal |
| `GET /api/metrics/historical` | Full time-series data for charts |
| `GET /api/valuation/status` | Valuation status and recommendation |
| `GET /api/metcalfe/boundaries` | Upper/lower boundary values |
| `GET /api/correlations` | Correlation coefficients for all three laws |
| `GET /api/stats` | Database statistics |
| `GET /api/signals/history` | Historical over/undervaluation signals |

**API Documentation**: http://localhost:8000/docs (Swagger UI)

---

## Methodology

### Metcalfe's Law (Upper Boundary)
```
Network Value ∝ n²
upper_bound = ln(SMA_30(n²))

Constants: a₁ = 0, b₁ = 1
```

### Odlyzko's Law (Lower Boundary)
```
Network Value ∝ n×ln(n)
lower_bound = -3.48 + 1.65 × SMA_30(ln(SMA_30(n×ln(n))))

Constants: a₂ = -3.48, b₂ = 1.65
```

### Fundamental NAV
```
NAV = (upper_bound + lower_bound) / 2
```

Where **n** = Daily Active Addresses

### Correlation Analysis
The model calculates Pearson correlation between actual market cap and:
- **Metcalfe's Law** (NV ~ n²): ~0.9705
- **Generalized Metcalfe** (NV ~ n^1.5): ~0.9702
- **Odlyzko's Law** (NV ~ n×ln(n)): ~0.9692

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///data/btc_valuation.db` | Database connection string |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | API endpoint for frontend |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |

Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your settings
```

---

## Makefile Commands

```bash
make help              # Show all commands
make up               # Start with Docker
make down             # Stop all services
make logs             # View logs
make dev-backend      # Run backend locally
make dev-frontend     # Run frontend locally
make dev-pipeline     # Run pipeline once
make db-import        # Import legacy CSV
make db-backfill      # Fetch historical data
make clean            # Clean build files
```

---

## Data Sources

- **Primary**: [BGeometrics](https://charts.bgeometrics.com) - Free Bitcoin on-chain data
- **Backup**: [CoinMetrics](https://coinmetrics.io) Community API
- **Legacy**: Original `btc.csv` from the research project

### Metrics Retrieved
- Daily Active Addresses (DAA)
- Market Cap (USD)
- Price (USD)
- Transaction Count
- Transaction Volume
- Hash Rate
- NVT Ratio

---

## Deployment

### Railway / Render / Fly.io

1. Push code to GitHub
2. Connect your platform to the repo
3. Set environment variables
4. Deploy!

### VPS / Self-hosted

```bash
# Clone repository
git clone <repo-url>
cd dashboard

# Deploy with Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Development

### Adding New Metrics

1. Update `shared/models/valuation.py` with new calculation
2. Add column to `shared/models/database.py`
3. Update fetcher in `pipeline/src/fetcher.py`
4. Update frontend components

### Running Tests

```bash
# Backend tests
cd api
pytest

# Frontend tests
cd webapp
npm test
```

---

## Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
# Or use different ports
docker-compose -p btc-dashboard up
```

### Database Locked
```bash
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

## Roadmap

- [ ] Email/Discord alerts for valuation signals
- [ ] NVT Ratio dashboard section
- [ ] Additional cryptocurrencies (ETH, etc.)
- [ ] Machine learning price predictions
- [ ] Mobile app (React Native)
- [ ] User authentication & portfolio tracking

---

## License

MIT - Feel free to use and modify!

---

## Acknowledgments

- Original analysis by the notebook author
- [BGeometrics](https://charts.bgeometrics.com) for free on-chain data
- [CoinMetrics](https://coinmetrics.io) for community API
- Dmitry Kalichkin for Metcalfe's Law application research

---

## Disclaimer

> **Not financial advice.** This dashboard is for educational and research purposes only. Cryptocurrency investments carry significant risk. Always do your own research.
