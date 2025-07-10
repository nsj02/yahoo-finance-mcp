# 1. 베이스 이미지 선택
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 복사 및 설치
COPY pyproject.toml . 
# Using uv for faster installation
RUN pip install uv
RUN uv pip install --no-cache-dir -r pyproject.toml

# 4. 소스 코드 복사
COPY . .

# 5. 서버 실행 포트 노출
EXPOSE 8000

# 6. 서버 실행 명령어
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]