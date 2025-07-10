# server.py

import json
from enum import Enum
from typing import List, Optional, Any, Dict

import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# ==============================================================================
# 1. Pydantic 응답 모델(Response Models) 정의
# 각 API가 어떤 구조의 데이터를 반환하는지 명확하게 정의합니다.
# ==============================================================================

# Generic-purpose Models
class Message(BaseModel):
    message: str

# /stock/history
class StockHistoryData(BaseModel):
    Date: str
    Open: float
    High: float
    Low: float
    Close: float
    Volume: int
    Dividends: float
    Stock_Splits: float = Field(..., alias='Stock Splits')

# /stock/info
# .info는 필드가 너무 많고 유동적이므로, 자주 사용되는 핵심 필드만 정의합니다.
# 존재하지 않을 수 있는 대부분의 필드는 Optional로 처리합니다.
class StockInfoData(BaseModel):
    symbol: str
    shortName: Optional[str] = None
    longName: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    marketCap: Optional[int] = None
    totalAssets: Optional[int] = None
    # 재무 정보
    trailingPE: Optional[float] = None
    forwardPE: Optional[float] = None
    # 주가 정보
    previousClose: Optional[float] = None
    open: Optional[float] = None
    dayHigh: Optional[float] = None
    dayLow: Optional[float] = None
    # 배당 정보
    dividendRate: Optional[float] = None
    dividendYield: Optional[float] = None
    
    class Config:
        # yfinance가 반환하는 필드 중 없는 필드는 무시하도록 설정
        extra = 'ignore'

# /stock/news
class NewsData(BaseModel):
    uuid: str
    title: str
    publisher: str
    link: str
    providerPublishTime: int
    type: str
    thumbnail: Optional[Dict[str, Any]] = None
    relatedTickers: Optional[List[str]] = None

# /stock/actions
class StockActionData(BaseModel):
    Date: str
    Dividends: float
    Stock_Splits: float = Field(..., alias='Stock Splits')

# /stock/financials
# 재무제표는 동적인 컬럼(날짜)을 가지므로, 일반적인 모델로 정의하기 어렵습니다.
# 따라서 '어떤 타입이든 허용'하는 형태로 반환합니다.
FinancialsData = Any

# /stock/holders
class HolderData(BaseModel):
    # 각 홀더 타입마다 구조가 다르므로, 가장 일반적인 형태를 가정합니다.
    # 실제로는 holder_type에 따라 다른 모델을 정의하는 것이 더 정확합니다.
    Holder: Optional[str] = None
    Shares: Optional[int] = None
    Date_Reported: Optional[str] = Field(None, alias='Date Reported')
    Value: Optional[int] = None
    
    class Config:
        extra = 'ignore' # yfinance가 반환하는 추가 필드는 무시

# /stock/options/expirations
class OptionExpirationsData(BaseModel):
    expiration_dates: List[str]

# /stock/options/chain
class OptionData(BaseModel):
    contractSymbol: str
    lastTradeDate: str
    strike: float
    lastPrice: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    change: float
    percentChange: float
    volume: Optional[int] = None
    openInterest: Optional[int] = None
    impliedVolatility: float
    inTheMoney: bool
    contractSize: str
    currency: str

class OptionChainData(BaseModel):
    calls: List[OptionData]
    puts: List[OptionData]

# /stock/recommendations
class RecommendationData(BaseModel):
    # .recommendations와 .upgrades_downgrades의 구조가 다르므로 Any로 처리
    # 필요 시 각 타입에 맞는 모델을 별도로 생성할 수 있습니다.
    Firm: Optional[str] = None
    To_Grade: Optional[str] = Field(None, alias='To Grade')
    From_Grade: Optional[str] = Field(None, alias='From Grade')
    Action: Optional[str] = None
    
    class Config:
        extra = 'ignore'

# ==============================================================================
# 2. FastAPI 애플리케이션 정의
# ==============================================================================

app = FastAPI(
    title="Yahoo Finance API Server",
    description="yfinance 라이브러리를 활용한 금융 데이터 API",
    version="1.0.0",
)

# 공통 에러 응답 모델 정의
common_responses = {
    404: {"model": Message, "description": "Ticker not found"},
    500: {"model": Message, "description": "Internal Server Error"},
}

@app.get("/stock/history", summary="주식 과거 시세 조회", response_model=List[StockHistoryData], responses=common_responses)
def get_historical_stock_prices(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    period: str = Query("1mo", description="조회 기간 (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)", example="1y"),
    interval: str = Query("1d", description="조회 간격 (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)", example="1d"),
):
    try:
        company = yf.Ticker(ticker)
        if not company.history(period="1d"): # Ticker 존재 여부 확인용 간단한 호출
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")
            
        hist_data = company.history(period=period, interval=interval)
        if hist_data.empty:
            return []
        hist_data = hist_data.reset_index()
        hist_data.rename(columns={'Stock Splits': 'Stock_Splits'}, inplace=True)
        return json.loads(hist_data.to_json(orient="records", date_format="iso"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/info", summary="주식 종합 정보 조회", response_model=StockInfoData, responses=common_responses)
def get_stock_info(ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")):
    try:
        company = yf.Ticker(ticker)
        if not company.info:
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found or no info available.")
        return company.info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/news", summary="주식 관련 뉴스 조회", response_model=List[NewsData], responses=common_responses)
def get_yahoo_finance_news(ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")):
    try:
        company = yf.Ticker(ticker)
        if not company.history(period="1d"):
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")
        news = company.news
        if not news:
            return []
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/actions", summary="주식 활동(배당, 분할) 조회", response_model=List[StockActionData], responses=common_responses)
def get_stock_actions(ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")):
    try:
        company = yf.Ticker(ticker)
        if not company.history(period="1d"):
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")
        actions_df = company.actions
        if actions_df.empty:
            return []
        actions_df = actions_df.reset_index()
        actions_df.rename(columns={'Stock Splits': 'Stock_Splits'}, inplace=True)
        return json.loads(actions_df.to_json(orient="records", date_format="iso"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/financials", summary="재무제표 조회", response_model=FinancialsData, responses=common_responses)
def get_financial_statement(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    financial_type: FinancialType = Query(..., description="조회할 재무제표 종류", example="income_stmt"),
):
    try:
        company = yf.Ticker(ticker)
        if not company.history(period="1d"):
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")

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


@app.get("/stock/holders", summary="주주 정보 조회", response_model=List[HolderData], responses=common_responses)
def get_holder_info(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    holder_type: HolderType = Query(..., description="조회할 주주 정보 종류", example="major_holders"),
):
    try:
        company = yf.Ticker(ticker)
        if not company.history(period="1d"):
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")

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
            return []

        holder_info = holder_info.reset_index()
        # 컬럼 이름의 공백 등을 API 친화적인 이름으로 변경
        holder_info.columns = [col.replace(' ', '_').replace('%', 'pct') for col in holder_info.columns]
        return json.loads(holder_info.to_json(orient="records", date_format="iso"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/options/expirations", summary="옵션 만기일 조회", response_model=OptionExpirationsData, responses=common_responses)
def get_option_expiration_dates(ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")):
    try:
        company = yf.Ticker(ticker)
        if not company.history(period="1d"):
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")
        options = company.options
        if not options:
            return {"expiration_dates": []}
        return {"expiration_dates": options}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/options/chain", summary="옵션 체인 조회", response_model=OptionChainData, responses=common_responses)
def get_option_chain(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    expiration_date: str = Query(..., description="옵션 만기일 (YYYY-MM-DD 형식)", example="2025-12-19"),
):
    try:
        company = yf.Ticker(ticker)
        if not company.history(period="1d"):
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")

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


@app.get("/stock/recommendations", summary="애널리스트 추천 정보 조회", response_model=List[RecommendationData], responses=common_responses)
def get_recommendations(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    recommendation_type: RecommendationType = Query("recommendations", description="조회할 추천 정보 종류", example="upgrades_downgrades"),
    months_back: int = Query(12, description="upgrades_downgrades 조회 시, 과거 몇 개월까지의 데이터를 볼지 설정", ge=1),
):
    try:
        company = yf.Ticker(ticker)
        if not company.history(period="1d"):
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")

        if recommendation_type == RecommendationType.recommendations:
            recs = company.recommendations
            if recs.empty:
                return []
            recs = recs.reset_index()
            recs.rename(columns={'To Grade': 'To_Grade', 'From Grade': 'From_Grade'}, inplace=True)
            return json.loads(recs.to_json(orient="records", date_format="iso"))

        elif recommendation_type == RecommendationType.upgrades_downgrades:
            upgrades_downgrades = company.upgrades_downgrades
            if upgrades_downgrades.empty:
                return []

            upgrades_downgrades = upgrades_downgrades.reset_index()
            cutoff_date = pd.Timestamp.now(tz='UTC') - pd.DateOffset(months=months_back)
            upgrades_downgrades = upgrades_downgrades[upgrades_downgrades["GradeDate"] >= cutoff_date]
            upgrades_downgrades = upgrades_downgrades.sort_values("GradeDate", ascending=False)
            upgrades_downgrades.rename(columns={'To Grade': 'To_Grade', 'From Grade': 'From_Grade'}, inplace=True)
            return json.loads(upgrades_downgrades.to_json(orient="records", date_format="iso"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
