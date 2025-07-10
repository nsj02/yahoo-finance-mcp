import json
from enum import Enum

import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Query

# Define an enum for the type of financial statement
class FinancialType(str, Enum):
    income_stmt = "income_stmt"
    quarterly_income_stmt = "quarterly_income_stmt"
    balance_sheet = "balance_sheet"
    quarterly_balance_sheet = "quarterly_balance_sheet"
    cashflow = "cashflow"
    quarterly_cashflow = "quarterly_cashflow"


class HolderType(str, Enum):
    major_holders = "major_holders"
    institutional_holders = "institutional_holders"
    mutualfund_holders = "mutualfund_holders"
    insider_transactions = "insider_transactions"
    insider_purchases = "insider_purchases"
    insider_roster_holders = "insider_roster_holders"


class RecommendationType(str, Enum):
    recommendations = "recommendations"
    upgrades_downgrades = "upgrades_downgrades"


app = FastAPI(
    title="Yahoo Finance API Server",
    description="yfinance 라이브러리를 활용한 금융 데이터 API",
    version="1.0.0",
)


@app.get("/stock/history", summary="주식 과거 시세 조회")
def get_historical_stock_prices(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    period: str = Query(
        "1mo",
        description="조회 기간 (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)",
        example="1y",
    ),
    interval: str = Query(
        "1d",
        description="조회 간격 (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)",
        example="1d",
    ),
):
    """
    주어진 티커에 대한 과거 시세 데이터를 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        # Use .info to check for existence, as it's a cached property
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )
        hist_data = company.history(period=period, interval=interval)
        if hist_data.empty:
            return {"message": "No historical data found for the given parameters."}
        hist_data = hist_data.reset_index()
        return json.loads(hist_data.to_json(orient="records", date_format="iso"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/info", summary="주식 종합 정보 조회")
def get_stock_info(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")
):
    """
    주어진 티커에 대한 종합 정보(회사 프로필, 주가, 재무 지표 등)를 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )
        return company.info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/news", summary="주식 관련 뉴스 조회")
def get_yahoo_finance_news(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")
):
    """
    주어진 티커에 대한 최신 뉴스를 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )
        news = company.news
        if not news:
            return {"message": f"No news found for ticker '{ticker}'."}
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/actions", summary="주식 활동(배당, 분할) 조회")
def get_stock_actions(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")
):
    """
    주어진 티커에 대한 배당 및 주식 분할 내역을 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )
        actions_df = company.actions
        if actions_df.empty:
            return {"message": "No actions found for the given ticker."}
        actions_df = actions_df.reset_index()
        return json.loads(actions_df.to_json(orient="records", date_format="iso"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/financials", summary="재무제표 조회")
def get_financial_statement(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    financial_type: FinancialType = Query(
        ..., description="조회할 재무제표 종류", example="income_stmt"
    ),
):
    """
    주어진 티커에 대한 지정된 종류의 재무제표를 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )

        statement_map = {
            "income_stmt": company.income_stmt,
            "quarterly_income_stmt": company.quarterly_income_stmt,
            "balance_sheet": company.balance_sheet,
            "quarterly_balance_sheet": company.quarterly_balance_sheet,
            "cashflow": company.cashflow,
            "quarterly_cashflow": company.quarterly_cashflow,
        }
        financial_statement = statement_map.get(financial_type.value)

        if financial_statement is None or financial_statement.empty:
            return {"message": f"No data available for financial type '{financial_type.value}'."}

        financial_statement = financial_statement.reset_index().rename(columns={'index': 'Metric'})
        return json.loads(financial_statement.to_json(orient="records", date_format="iso"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/holders", summary="주주 정보 조회")
def get_holder_info(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    holder_type: HolderType = Query(
        ..., description="조회할 주주 정보 종류", example="major_holders"
    ),
):
    """
    주어진 티커에 대한 지정된 종류의 주주 정보를 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )

        holder_map = {
            "major_holders": company.major_holders,
            "institutional_holders": company.institutional_holders,
            "mutualfund_holders": company.mutualfund_holders,
            "insider_transactions": company.insider_transactions,
            "insider_purchases": company.insider_purchases,
            "insider_roster_holders": company.insider_roster_holders,
        }
        holder_info = holder_map.get(holder_type.value)

        if holder_info is None or holder_info.empty:
            return {"message": f"No data available for holder type '{holder_type.value}'."}

        holder_info = holder_info.reset_index()
        return json.loads(holder_info.to_json(orient="records", date_format="iso"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/options/expirations", summary="옵션 만기일 조회")
def get_option_expiration_dates(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")
):
    """
    주어진 티커에 대한 옵션 만기일 목록을 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )
        options = company.options
        if not options:
            return {"message": "No option expiration dates found."}
        return {"expiration_dates": options}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/options/chain", summary="옵션 체인 조회")
def get_option_chain(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    expiration_date: str = Query(
        ..., description="옵션 만기일 (YYYY-MM-DD 형식)", example="2025-12-19"
    ),
):
    """
    주어진 티커와 만기일에 대한 콜/풋 옵션 체인을 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )

        if expiration_date not in company.options:
            raise HTTPException(
                status_code=404,
                detail=f"No options available for the date {expiration_date}. Available dates: {company.options}",
            )

        option_chain = company.option_chain(expiration_date)
        calls = json.loads(option_chain.calls.to_json(orient="records", date_format="iso"))
        puts = json.loads(option_chain.puts.to_json(orient="records", date_format="iso"))

        return {"calls": calls, "puts": puts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/recommendations", summary="애널리스트 추천 정보 조회")
def get_recommendations(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    recommendation_type: RecommendationType = Query(
        "recommendations",
        description="조회할 추천 정보 종류",
        example="upgrades_downgrades",
    ),
    months_back: int = Query(
        12, description="upgrades_downgrades 조회 시, 과거 몇 개월까지의 데이터를 볼지 설정", ge=1
    ),
):
    """
    주어진 티커에 대한 애널리스트의 추천 또는 등급 변경 내역을 반환합니다.
    """
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found or no info available."
            )

        if recommendation_type == RecommendationType.recommendations:
            recs = company.recommendations
            if recs.empty:
                return {"message": "No recommendation data available."}
            return json.loads(recs.to_json(orient="records", date_format="iso"))

        elif recommendation_type == RecommendationType.upgrades_downgrades:
            upgrades_downgrades = company.upgrades_downgrades
            if upgrades_downgrades.empty:
                return {"message": "No upgrade/downgrade data available."}

            upgrades_downgrades = upgrades_downgrades.reset_index()
            cutoff_date = pd.Timestamp.now(tz='UTC') - pd.DateOffset(months=months_back)
            upgrades_downgrades = upgrades_downgrades[
                upgrades_downgrades["GradeDate"] >= cutoff_date
            ]
            upgrades_downgrades = upgrades_downgrades.sort_values(
                "GradeDate", ascending=False
            )
            return json.loads(upgrades_downgrades.to_json(orient="records", date_format="iso"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))