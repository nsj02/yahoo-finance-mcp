#!/usr/bin/env python3
# db_manager.py - 데이터베이스 관리 메인 스크립트

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import Session, init_db
from database.data_importer import (
    build_initial_database, 
    update_daily_data, 
    update_full_technical_indicators,
    update_market_stats
)
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """프로그램 시작 배너 출력"""
    print("=" * 60)
    print("🚀 Yahoo Finance Database Manager")
    print("🇰🇷 한국 주식 데이터베이스 관리 시스템")
    print("=" * 60)

def print_status(message):
    """상태 메시지 출력"""
    print(f"📊 {message}")

def print_error(message):
    """오류 메시지 출력"""
    print(f"❌ 오류: {message}")

def print_success(message):
    """성공 메시지 출력"""
    print(f"✅ 성공: {message}")

def check_database_status():
    """데이터베이스 상태 확인"""
    try:
        db = Session()
        from database.models import Stock, DailyPrice, TechnicalIndicator, MarketIndex, MarketStat
        
        stock_count = db.query(Stock).count()
        price_count = db.query(DailyPrice).count()
        indicator_count = db.query(TechnicalIndicator).count()
        index_count = db.query(MarketIndex).count()
        stat_count = db.query(MarketStat).count()
        
        print("\n📊 현재 데이터베이스 상태:")
        print(f"  • 종목 수: {stock_count:,}개")
        print(f"  • 주가 데이터: {price_count:,}개")
        print(f"  • 기술적 지표: {indicator_count:,}개")
        print(f"  • 시장 지수: {index_count:,}개")
        print(f"  • 시장 통계: {stat_count:,}개")
        
        if stock_count > 0:
            # 최신 데이터 날짜 확인
            latest_price = db.query(DailyPrice).order_by(DailyPrice.date.desc()).first()
            if latest_price:
                print(f"  • 최신 데이터: {latest_price.date}")
        
        db.close()
        return True
    except Exception as e:
        print_error(f"데이터베이스 연결 실패: {e}")
        return False

def run_task(task: str, **kwargs):
    """DB 업데이트 작업을 실행합니다."""
    db = Session()
    try:
        if task == "init":
            years = kwargs.get('years', 3)
            print_status(f"데이터베이스 초기화 시작 ({years}년치 데이터)")
            init_db()  # 테이블 생성
            build_initial_database(db, years=years)
            print_success("데이터베이스 초기화 완료")
            
        elif task == "update":
            days = kwargs.get('days', 2)
            print_status(f"일일 데이터 업데이트 시작 (최근 {days}일)")
            update_daily_data(db, days=days)
            print_status("기술적 지표 전체 재계산 중...")
            update_full_technical_indicators(db)
            print_status("시장 통계 재계산 중...")
            update_market_stats(db)
            print_success("모든 업데이트 완료")
            
        elif task == "test":
            print_status("빠른 테스트 실행 중...")
            from database.test_db import test_build_database
            test_build_database()
            print_success("테스트 완료")
            
        elif task == "status":
            check_database_status()
            return
            
        else:
            print_error("잘못된 작업입니다.")
            print_usage()
            return
            
        # 작업 완료 후 상태 출력
        print("\n" + "=" * 40)
        check_database_status()
        
    except Exception as e:
        logger.error(f"작업 실행 중 오류 발생: {e}")
        print_error(f"작업 실행 실패: {e}")
    finally:
        db.close()

def print_usage():
    """사용법 출력"""
    print("\n📖 사용법:")
    print("  python db_manager.py init [years]     # 데이터베이스 초기화 (기본: 3년)")
    print("  python db_manager.py update [days]    # 데이터 업데이트 (기본: 2일)")
    print("  python db_manager.py test             # 빠른 테스트 (8개 주요 종목)")
    print("  python db_manager.py status           # 데이터베이스 상태 확인")
    print("\n💡 예시:")
    print("  python db_manager.py init 1           # 1년치 데이터로 초기화")
    print("  python db_manager.py update 5         # 최근 5일 데이터 업데이트")

def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print_usage()
        return
    
    task_name = sys.argv[1]
    
    if task_name == "init":
        years = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        run_task("init", years=years)
    elif task_name == "update":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        run_task("update", days=days)
    elif task_name == "test":
        run_task("test")
    elif task_name == "status":
        run_task("status")
    else:
        print_error(f"알 수 없는 명령어: {task_name}")
        print_usage()

if __name__ == "__main__":
    main()