# Yahoo Finance API & Database System

💰 이 프로젝트는 야후 파이낸스 데이터를 활용한 두 가지 시스템을 제공합니다:

1. **FastAPI 서버**: 실시간 야후 파이낸스 데이터 API
2. **데이터베이스 시스템**: 한국 주식 데이터 수집 및 저장 시스템

## 🚀 주요 기능

### FastAPI 서버 (`server.py`)
- **⚡ 고성능**: FastAPI 기반 비동기 처리
- **📊 포괄적 금융 데이터**:
  - 과거 주가 데이터 (OHLCV)
  - 기업 정보 및 지표
  - 재무제표 (손익계산서, 대차대조표, 현금흐름표)
  - 주주 정보 및 애널리스트 추천
- **🔒 안전**: 데이터 검증 및 오류 처리
- **📝 자동 문서화**: `/docs`에서 인터랙티브 API 문서

### 데이터베이스 시스템
- **🇰🇷 한국 주식 특화**: KOSPI/KOSDAQ 전 종목 지원
- **📈 기술적 지표**: RSI, MACD, 볼린저 밴드 등 자동 계산
- **📊 시장 통계**: 상승/하락 종목 수, 거래량/거래대금
- **🔄 자동 업데이트**: 일일 데이터 자동 수집

## 📁 프로젝트 구조

```
yahoo-finance-mcp/
├── server.py              # FastAPI 서버 (실시간 데이터)
├── models.py              # 데이터베이스 모델 정의
├── data_importer.py       # 데이터 수집 및 저장 로직
├── run_update.py          # DB 업데이트 메인 스크립트
├── test_db.py            # 빠른 테스트 스크립트
├── README_DATABASE.md    # 데이터베이스 상세 문서
└── README.md             # 이 문서
```

## 🛠️ 설치 및 설정

### 1. 의존성 설치
```bash
pip install ta sqlalchemy psycopg2-binary pykrx tqdm yfinance fastapi uvicorn
```

### 2. PostgreSQL 설정
```bash
# PostgreSQL 설치 및 시작
brew install postgresql@14
brew services start postgresql@14

# 데이터베이스 생성
createdb finance_db
```

## 🚀 사용 방법

### FastAPI 서버 실행
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**접속 주소:**
- API 서버: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 데이터베이스 시스템

#### 초기 구축 (3년치 데이터)
```bash
python run_update.py init 3
```

#### 일일 업데이트
```bash
python run_update.py update 2
```

#### 빠른 테스트 (8개 주요 종목)
```bash
python test_db.py
```

## 📊 API 엔드포인트

### 핵심 주식 데이터

| 엔드포인트 | 설명 | 예시 |
|-----------|------|------|
| `GET /stock/history` | 과거 OHLCV 데이터 | `?ticker=005930.KS&period=1y` |
| `GET /stock/info` | 기업 정보 및 지표 | `?ticker=005930.KS` |
| `GET /stock/actions` | 배당 및 주식 분할 | `?ticker=005930.KS` |

### 재무제표

| 엔드포인트 | 설명 | 매개변수 |
|-----------|------|----------|
| `GET /stock/financials` | 손익계산서, 대차대조표, 현금흐름표 | `ticker`, `financial_type` |

**재무제표 타입:**
- `income_stmt` - 연간 손익계산서
- `quarterly_income_stmt` - 분기 손익계산서
- `balance_sheet` - 연간 대차대조표
- `quarterly_balance_sheet` - 분기 대차대조표
- `cashflow` - 연간 현금흐름표
- `quarterly_cashflow` - 분기 현금흐름표

### 사용 예시

```bash
# 삼성전자 1년 주가 데이터
curl "http://localhost:8000/stock/history?ticker=005930.KS&period=1y&interval=1d"

# 네이버 기업 정보
curl "http://localhost:8000/stock/info?ticker=035420.KS"

# SK하이닉스 연간 손익계산서
curl "http://localhost:8000/stock/financials?ticker=000660.KS&financial_type=income_stmt"
```

## 🏗️ 시스템 아키텍처

### 데이터베이스 모델
- **Stock**: 종목 기본 정보
- **DailyPrice**: 일일 주가 데이터
- **TechnicalIndicator**: 기술적 지표
- **MarketIndex**: 시장 지수 (KOSPI, KOSDAQ)
- **MarketStat**: 시장 통계

### 작동 원리
1. **종목 수집**: pykrx → Yahoo Finance 형식 변환
2. **주가 데이터**: 병렬 처리로 빠른 수집
3. **기술적 지표**: ta 라이브러리로 자동 계산
4. **시장 통계**: 일일 시장 동향 분석

## 🔄 자동화 설정

### Cron 설정 (매일 자동 업데이트)
```bash
# crontab -e
30 15 * * 1-5 cd /path/to/project && python run_update.py update 2
```

## 🐳 Docker 배포

### 빠른 배포
```bash
docker build -t yahoo-finance-api .
docker run -d -p 8000:8000 --name yahoo-finance-api yahoo-finance-api
```

### 프로덕션 배포
```bash
docker run -d \
  --name yahoo-finance-api \
  --restart unless-stopped \
  -p 8000:8000 \
  --health-cmd="curl -f http://localhost:8000/docs || exit 1" \
  --health-interval=30s \
  yahoo-finance-api:latest
```

## 📚 상세 문서

- **데이터베이스 시스템**: [README_DATABASE.md](README_DATABASE.md)
- **API 문서**: 서버 실행 후 `/docs` 경로

## 🎯 주요 특징

- **한국 주식 최적화**: KOSPI/KOSDAQ 전 종목 지원
- **실시간 + 히스토리**: 실시간 API + 축적된 데이터베이스
- **병렬 처리**: 빠른 대용량 데이터 수집
- **안정성**: 오류 복구 및 재시도 로직
- **확장성**: 새로운 지표 및 기능 쉽게 추가
- **자동화**: 무인 운영 가능한 업데이트 시스템

## 🛡️ 오류 처리

- **404**: 종목을 찾을 수 없음
- **500**: 내부 서버 오류 (상세 정보 포함)
- **422**: 검증 오류 (잘못된 매개변수)

## 📜 라이센스

MIT License - LICENSE 파일 참조