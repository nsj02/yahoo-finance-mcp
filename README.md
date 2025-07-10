# Yahoo Finance API Server

This project provides a RESTful API server to access comprehensive financial data from Yahoo Finance using the `yfinance` library. It is built with FastAPI and is ready for deployment as a Docker container.

## Features

-   **Modern API**: Built with FastAPI, providing high performance and automatic OpenAPI documentation.
-   **Comprehensive Data**: Access a wide range of financial data:
    -   Historical stock prices (OHLCV)
    -   Detailed stock information (company profile, financial metrics, etc.)
    -   Latest company news
    -   Stock actions (dividends and splits)
    -   Financial statements (income statement, balance sheet, cash flow)
    -   Holder information (major, institutional, etc.)
    -   Options data (expiration dates and option chains)
    -   Analyst recommendations and upgrades/downgrades.
-   **Dockerized**: Includes a `Dockerfile` for easy containerization and deployment to any cloud environment.
-   **Auto-generated Docs**: Interactive API documentation is available at the `/docs` endpoint.

## Getting Started

### Prerequisites

-   Python 3.11+
-   [uv](https://github.com/astral-sh/uv) (recommended for environment and package management)

### Installation & Running Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nsj02/yahoo-finance-mcp.git
    cd yahoo-finance-mcp
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    uv pip install -r pyproject.toml
    ```

3.  **Run the server:**
    ```bash
    uvicorn server:app --reload
    ```
    The server will be running at `http://127.0.0.1:8000`.

### API Documentation

Once the server is running, you can access the interactive API documentation (powered by Swagger UI) by navigating to:

[**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

This interface allows you to explore and test all the available API endpoints directly from your browser.

## Deployment with Docker

This project is configured for easy deployment using Docker.

1.  **Build the Docker image:**
    ```bash
    docker build -t yahoo-finance-api .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -d -p 8000:8000 --name yahoo-finance-api-container yahoo-finance-api
    ```
    The API will be accessible at `http://localhost:8000`.

## Available API Endpoints

Here is a summary of the main API endpoints. For detailed parameters and response models, please refer to the [API documentation](#api-documentation).

-   `GET /stock/history`: Get historical stock prices.
-   `GET /stock/info`: Get comprehensive stock information.
-   `GET /stock/news`: Get the latest news for a stock.
-   `GET /stock/actions`: Get stock dividends and splits.
-   `GET /stock/financials`: Get financial statements.
-   `GET /stock/holders`: Get holder information.
-   `GET /stock/options/expirations`: Get option expiration dates.
-   `GET /stock/options/chain`: Get the full option chain for a given expiration date.
-   `GET /stock/recommendations`: Get analyst recommendations.

## License

This project is licensed under the MIT License.