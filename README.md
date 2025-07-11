# Yahoo Finance API Server

💰 A production-ready RESTful API server providing comprehensive financial data from Yahoo Finance using the `yfinance` library. Built with FastAPI for high performance and automatic OpenAPI documentation.

## 🎆 Features

-   **⚡ High Performance**: Built with FastAPI, providing async support and automatic data validation
-   **📊 Comprehensive Financial Data**:
    -   Historical stock prices (OHLCV data)
    -   Detailed company information and metrics
    -   Stock actions (dividends and splits)
    -   Financial statements (income statement, balance sheet, cash flow)
    -   Holder information (institutional, major shareholders)
    -   Analyst recommendations and upgrades/downgrades
-   **🚀 Production Ready**: 
    -   Dockerized for easy deployment
    -   Robust error handling and data validation
    -   Type-safe data conversion (pandas/numpy to JSON)
    -   Health checks and monitoring support
-   **📝 Auto-generated Documentation**: Interactive API docs available at `/docs`
-   **🔒 Secure**: Built-in security best practices and data sanitization

## 🚀 Quick Start

### Prerequisites

-   Python 3.11+
-   [uv](https://github.com/astral-sh/uv) (recommended for fast package management)

### Local Development

1.  **Clone and setup:**
    ```bash
    git clone https://github.com/nsj02/yahoo-finance-api.git
    cd yahoo-finance-api
    
    # Create virtual environment and install dependencies
    uv venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    uv pip install .
    ```

2.  **Start the server:**
    ```bash
    uvicorn server:app --reload --host 0.0.0.0 --port 8000
    ```
    
3.  **Access the API:**
    - API Server: `http://localhost:8000`
    - Interactive Docs: `http://localhost:8000/docs`
    - OpenAPI Schema: `http://localhost:8000/openapi.json`

### 📝 Interactive Documentation

Once the server is running, explore the full API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

The Swagger UI provides an interactive interface to test all endpoints directly from your browser.

## 🚀 Docker Deployment

### Quick Deploy

```bash
# Build and run
docker build -t yahoo-finance-api .
docker run -d -p 8000:8000 --name yahoo-finance-api yahoo-finance-api
```

### Production Deployment

```bash
# Build for production
docker build -t yahoo-finance-api:latest .

# Run with health checks and restart policy
docker run -d \
  --name yahoo-finance-api \
  --restart unless-stopped \
  -p 8000:8000 \
  --health-cmd="curl -f http://localhost:8000/docs || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  yahoo-finance-api:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  yahoo-finance-api:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 📊 API Endpoints

### Core Stock Data

| Endpoint | Description | Example |
|----------|-------------|----------|
| `GET /stock/history` | Historical OHLCV data | `?ticker=AAPL&period=1y&interval=1d` |
| `GET /stock/info` | Company information & metrics | `?ticker=AAPL` |
| `GET /stock/actions` | Dividends and stock splits | `?ticker=AAPL` |

### Financial Statements

| Endpoint | Description | Parameters |
|----------|-------------|------------|
| `GET /stock/financials` | Income statement, balance sheet, cash flow | `ticker`, `financial_type` |

**Financial Types:**
- `income_stmt` - Annual income statement
- `quarterly_income_stmt` - Quarterly income statement  
- `balance_sheet` - Annual balance sheet
- `quarterly_balance_sheet` - Quarterly balance sheet
- `cashflow` - Annual cash flow
- `quarterly_cashflow` - Quarterly cash flow

### Ownership & Analysis

| Endpoint | Description | Parameters |
|----------|-------------|------------|
| `GET /stock/holders` | Shareholder information | `ticker`, `holder_type` |
| `GET /stock/recommendations` | Analyst recommendations | `ticker`, `recommendation_type` |

### Example Usage

```bash
# Get Apple's stock history for the last year
curl "http://localhost:8000/stock/history?ticker=AAPL&period=1y&interval=1d"

# Get Tesla's company information
curl "http://localhost:8000/stock/info?ticker=TSLA"

# Get Microsoft's annual income statement
curl "http://localhost:8000/stock/financials?ticker=MSFT&financial_type=income_stmt"
```

## 📝 API Response Format

All endpoints return JSON data with proper error handling:

```json
{
  "Date": "2025-07-10T00:00:00-04:00",
  "Open": 210.50,
  "High": 213.48,
  "Low": 210.12,
  "Close": 212.41,
  "Volume": 43770740,
  "Dividends": 0.0,
  "Stock Splits": null
}
```

## 🔧 Development

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run linting
black server.py
isort server.py

# Type checking
mypy server.py
```

## 📊 Monitoring

- Health check endpoint: `GET /docs` (returns 200 if healthy)
- Metrics and monitoring can be added via middleware
- Docker health checks included

## 🛡️ Error Handling

- **404**: Ticker not found
- **500**: Internal server error (with details)
- **422**: Validation error (invalid parameters)

## 📜 License

MIT License - see LICENSE file for details.