"""
Gemini Pro 배경 제거 API 서버 실행 스크립트
"""

import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# GEMINI_API_KEY 확인
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️ 경고: GEMINI_API_KEY가 설정되지 않았습니다.")
    print("   .env 파일을 생성하고 GEMINI_API_KEY를 설정하세요.")
    print("   예시:")
    print("   GEMINI_API_KEY=your_api_key_here")
    print()
    response = input("GEMINI API 키 없이 계속 진행하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

# uvicorn 실행
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Gemini Pro 배경 제거 API 서버 시작...")
    print("   주소: http://localhost:8000")
    print("   문서: http://localhost:8000/docs")
    print()
    
    uvicorn.run(
        "bg_remover_gemini_pro:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
