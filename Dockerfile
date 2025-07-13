# Yahoo Finance MCP - API Server & Database System
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uv 패키지 관리자 설치
RUN pip install --no-cache-dir uv

# 의존성 파일 복사
COPY pyproject.toml ./

# 의존성 설치
RUN uv pip install --system --no-cache .

# 소스 코드 복사
COPY server.py ./
COPY db_manager.py ./
COPY database/ ./database/

# 포트 노출
EXPOSE 8000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# 기본적으로 FastAPI 서버 실행 (db_manager.py는 별도 실행)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]