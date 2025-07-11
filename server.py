# server.py

import json
from enum import Enum
from typing import List, Optional, Any, Dict

import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ==============================================================================
# 1. Pydantic 응답 모델(Response Models) - 최종 수정본
# ==============================================================================

class Message(BaseModel):
    message: str
    
    class Config:
        extra = 'forbid'

# 기본 주식 데이터 모델들을 Dict로 대체다을 사용
StockHistoryData = Dict[str, Any]
StockInfoData = Dict[str, Any]
StockActionData = Dict[str, Any]

# 재무제표 데이터를 위해 간단한 Dict 타입 사용
FinancialsData = Dict[str, Any]

# 홀더 데이터를 위해 간단한 Dict 타입 사용
HolderData = Dict[str, Any]

# 추천 데이터를 위해 간단한 Dict 타입 사용
RecommendationData = Dict[str, Any]

# 옵션 관련 모델들은 제거됨

# ==============================================================================
# 1-2. API 파라미터용 Enum 정의
# ==============================================================================

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

# ==============================================================================
# 2. FastAPI 애플리케이션 및 헬퍼 함수 정의 - 최종 수정본
# ==============================================================================

app = FastAPI(
    title="Yahoo Finance API Server",
    description="yfinance 라이브러리를 활용한 금융 데이터 API",
    version="1.0.0",
)

# CORS 설정 추가 (하이퍼클로바 스튜디오 호환성)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # 모든 오리진 허용 (프로덕션에서는 제한 필요)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAPI 3.0.3 스키마를 사용하도록 강제 설정
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # OpenAPI 버전을 3.0.3으로 강제 설정
    openapi_schema["openapi"] = "3.0.3"
    
    # 네이버클라우드 서버 정보 추가
    openapi_schema["servers"] = [
        {
            "url": "http://49.50.131.32:8000",
            "description": "Naver Cloud Platform Server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

common_responses = {
    404: {"model": Message, "description": "Ticker not found"},
    500: {"model": Message, "description": "Internal Server Error"},
}

def get_ticker_object(ticker: str) -> yf.Ticker:
    """Helper function to get a Ticker object and robustly check for its validity."""
    company = yf.Ticker(ticker)
    if company.history(period="1d").empty:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found.")
    return company

def dataframe_to_safe_json(df: Optional[pd.DataFrame]) -> List[Dict[str, Any]]:
    """Helper function to robustly convert DataFrame to a JSON-compatible list of dicts."""
    if df is None or df.empty:
        return []
    
    # DataFrame의 복사본 생성
    df_copy = df.copy()
    
    # 인덱스가 DatetimeIndex인 경우 Date 컬럼으로 변환
    if isinstance(df_copy.index, pd.DatetimeIndex):
        df_copy = df_copy.reset_index()
        if 'Date' not in df_copy.columns and len(df_copy.columns) > 0:
            df_copy = df_copy.rename(columns={df_copy.columns[0]: 'Date'})
    else:
        df_copy = df_copy.reset_index()
    
    # API 모델과 필드 이름을 맞추기 위한 처리
    # 컬럼명을 안전하게 문자열로 변환
    df_copy.columns = [str(col).replace(' ', '_') for col in df_copy.columns]
    
    # Stock Splits 컬럼명을 Stock_Splits로 변경
    if 'Stock_Splits' in df_copy.columns:
        df_copy = df_copy.rename(columns={'Stock_Splits': 'Stock_Splits'})
    
    # 모든 NaN, NaT, inf 값을 파이썬의 None으로 변환
    df_copy = df_copy.replace([np.inf, -np.inf], None)
    df_copy = df_copy.where(pd.notna(df_copy), None)
    
    records = df_copy.to_dict(orient="records")
    
    # 각 레코드를 순회하며 타입을 안전하게 변환
    for record in records:
        for key, value in record.items():
            if value is None:
                continue
            elif isinstance(value, (pd.Timestamp, np.datetime64)):
                try:
                    if pd.notna(value):
                        record[key] = pd.Timestamp(value).isoformat()
                    else:
                        record[key] = None
                except:
                    record[key] = None
            elif isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
                record[key] = int(value)
            elif isinstance(value, (np.float64, np.float32, np.float16)):
                if np.isnan(value) or np.isinf(value):
                    record[key] = None
                else:
                    record[key] = float(value)
            elif isinstance(value, (np.bool_, bool)):
                record[key] = bool(value)
            elif isinstance(value, bytes):
                record[key] = value.decode('utf-8', errors='ignore')
    
    return records

def convert_to_financials_data(df: Optional[pd.DataFrame]) -> List[Dict[str, Any]]:
    """Convert DataFrame to FinancialsData format."""
    if df is None or df.empty:
        return []
    
    # 인덱스가 금융 데이터 항목이고 컬럼이 연도인 경우
    df_copy = df.copy()
    
    # 인덱스를 리셋하여 index 컬럼으로 만들기
    df_copy = df_copy.reset_index()
    
    # 컬럼명을 안전하겎 문자열로 변환
    df_copy.columns = [str(col).replace(' ', '_') for col in df_copy.columns]
    
    # NaN, inf 값 처리
    df_copy = df_copy.replace([np.inf, -np.inf], None)
    df_copy = df_copy.where(pd.notna(df_copy), None)
    
    # 레코드로 변환
    records = df_copy.to_dict(orient="records")
    
    # 각 레코드를 순회하며 타입을 안전하게 변환
    for record in records:
        for key, value in record.items():
            if value is None:
                continue
            elif isinstance(value, (pd.Timestamp, np.datetime64)):
                try:
                    if pd.notna(value):
                        record[key] = pd.Timestamp(value).isoformat()
                    else:
                        record[key] = None
                except:
                    record[key] = None
            elif isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
                record[key] = int(value)
            elif isinstance(value, (np.float64, np.float32, np.float16)):
                if np.isnan(value) or np.isinf(value):
                    record[key] = None
                else:
                    record[key] = float(value)
            elif isinstance(value, (np.bool_, bool)):
                record[key] = bool(value)
            elif isinstance(value, bytes):
                record[key] = value.decode('utf-8', errors='ignore')
    
    return records


@app.get("/stock/history", summary="주식 과거 시세 조회", response_model=List[StockHistoryData], responses=common_responses)
def get_historical_stock_prices(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    period: str = Query("1mo", description="조회 기간", example="1y"),
    interval: str = Query("1d", description="조회 간격", example="1d"),
):
    try:
        company = get_ticker_object(ticker)
        hist_data = company.history(period=period, interval=interval)
        return dataframe_to_safe_json(hist_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/info", summary="주식 종합 정보 조회", response_model=StockInfoData, responses=common_responses)
def get_stock_info(ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")):
    try:
        company = get_ticker_object(ticker)
        return company.info
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 뉴스 API 삭제됨 - yfinance의 뉴스 기능이 안정적이지 않음

@app.get("/stock/actions", summary="주식 활동(배당, 분할) 조회", response_model=List[StockActionData], responses=common_responses)
def get_stock_actions(ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL")):
    try:
        company = get_ticker_object(ticker)
        return dataframe_to_safe_json(company.actions)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/financials", summary="재무제표 조회", response_model=List[FinancialsData], responses=common_responses)
def get_financial_statement(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    financial_type: FinancialType = Query(..., description="조회할 재무제표 종류", example="income_stmt"),
):
    try:
        company = get_ticker_object(ticker)
        statement_map = {
            "income_stmt": company.income_stmt,
            "quarterly_income_stmt": company.quarterly_income_stmt,
            "balance_sheet": company.balance_sheet,
            "quarterly_balance_sheet": company.quarterly_balance_sheet,
            "cashflow": company.cashflow,
            "quarterly_cashflow": company.quarterly_cashflow,
        }
        return dataframe_to_safe_json(statement_map.get(financial_type.value))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/holders", summary="주주 정보 조회", response_model=List[HolderData], responses=common_responses)
def get_holder_info(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    holder_type: HolderType = Query(..., description="조회할 주주 정보 종류", example="major_holders"),
):
    try:
        company = get_ticker_object(ticker)
        holder_map = {
            "major_holders": company.major_holders,
            "institutional_holders": company.institutional_holders,
            "mutualfund_holders": company.mutualfund_holders,
            "insider_transactions": company.insider_transactions,
            "insider_purchases": company.insider_purchases,
            "insider_roster_holders": company.insider_roster_holders,
        }
        return dataframe_to_safe_json(holder_map.get(holder_type.value))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 옵션 관련 API는 타입 변환 문제로 인해 제거됨


@app.get("/stock/recommendations", summary="애널리스트 추천 정보 조회", response_model=List[RecommendationData], responses=common_responses)
def get_recommendations(
    ticker: str = Query(..., description="조회할 주식의 티커", example="AAPL"),
    recommendation_type: RecommendationType = Query("recommendations", description="조회할 추천 정보 종류", example="upgrades_downgrades"),
    months_back: int = Query(12, description="upgrades_downgrades 조회 시, 과거 몇 개월까지의 데이터를 볼지 설정", ge=1),
):
    try:
        company = get_ticker_object(ticker)
        if recommendation_type == RecommendationType.recommendations:
            recs = company.recommendations
        else: # upgrades_downgrades
            recs = company.upgrades_downgrades
            if not recs.empty and 'GradeDate' in recs.columns:
                recs = recs.copy()
                recs['GradeDate'] = pd.to_datetime(recs['GradeDate'], utc=True)
                cutoff_date = pd.Timestamp.now(tz='UTC') - pd.DateOffset(months=months_back)
                recs = recs[recs["GradeDate"] >= cutoff_date]
        
        if not recs.empty:
            if 'GradeDate' in recs.columns:
                recs = recs.sort_values("GradeDate", ascending=False)
            return dataframe_to_safe_json(recs)
        else:
            return []
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))