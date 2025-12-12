#!/usr/bin/env python3
"""
EC2에서 안정적으로 실행하기 위한 FastAPI 서버 실행 스크립트
"""

import uvicorn
from app import app

if __name__ == "__main__":
    print("[SERVER] EC2 최적화 서버 시작")
    uvicorn.run(
        "app:app",  # 애플리케이션 경로
        host="0.0.0.0",
        port=8000,
        
        # 타임아웃 설정
        timeout_keep_alive=0,  # keep-alive 타임아웃 무제한
        timeout_graceful_shutdown=600,  # graceful shutdown 10분
        timeout_notify=60,  # 60초
        
        # 워커 설정
        workers=1,  # 단일 워커 (메모리 사용량 최적화)
        
        # 요청 제한 설정
        limit_max_requests=0,  # 무제한
        limit_concurrency=1000,  # 동시 요청 수
        
        # 로깅 설정
        log_level="info",
        access_log=True,
        
        # 개발 설정
        reload=False,
        
        # EC2 최적화 설정
        backlog=2048,  # 연결 대기열 크기
        max_concurrency=1000,  # 최대 동시 연결
        
        # HTTP 설정
        h11_max_incomplete_event_size=16777216,  # 16MB
    ) 