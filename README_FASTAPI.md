# 이미지 묘사 FastAPI

Gemini API를 사용해서 이미지 URL을 받아 영어로 이미지를 묘사해주는 FastAPI 서버입니다.

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements_fastapi.txt
```

### 2. 환경변수 설정
`.env` 파일을 생성하고 Gemini API 키를 설정하세요:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 서버 실행
```bash
python fastapi_image_describe.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 엔드포인트

### 1. 루트 엔드포인트
- **GET** `/`
- 서버 상태 확인

### 2. 헬스 체크
- **GET** `/health`
- 서버 및 Gemini API 설정 상태 확인

### 3. 이미지 묘사
- **POST** `/describe`
- 이미지 URL을 받아서 영어로 묘사를 반환

#### 요청 예시:
```json
{
  "image_url": "https://example.com/image.jpg"
}
```

#### 응답 예시:
```json
{
  "success": true,
  "description": "A young woman with long dark hair and a bright smile. She is wearing a casual blue sweater and appears to be in a natural outdoor setting. Her eyes are warm and friendly, and she has a gentle, approachable demeanor."
}
```

#### 오류 응답 예시:
```json
{
  "success": false,
  "error": "이미지 묘사를 생성할 수 없습니다. 이미지 URL을 확인해주세요."
}
```

## 테스트

### Python 스크립트로 테스트
```bash
python test_fastapi_describe.py
```

### curl로 테스트
```bash
# 헬스 체크
curl -X GET http://localhost:8000/health

# 이미지 묘사
curl -X POST "http://localhost:8000/describe" \
     -H "Content-Type: application/json" \
     -d '{
       "image_url": "https://example.com/your-image.jpg"
     }'
```

## 주요 기능

- **이미지 URL 검증**: Pydantic을 사용한 URL 형식 검증
- **오류 처리**: 적절한 HTTP 상태 코드와 오류 메시지 반환
- **CORS 지원**: 웹 애플리케이션에서 API 호출 가능
- **API 문서**: FastAPI 자동 생성 문서 (`http://localhost:8000/docs`)
- **헬스 체크**: 서버 및 설정 상태 모니터링

## 파일 구조

- `fastapi_image_describe.py`: 메인 FastAPI 애플리케이션
- `requirements_fastapi.txt`: Python 의존성 목록
- `test_fastapi_describe.py`: API 테스트 스크립트
- `README_FASTAPI.md`: 이 문서

## 환경 요구사항

- Python 3.8+
- Gemini API 키
- 인터넷 연결 (이미지 다운로드 및 Gemini API 호출용)
