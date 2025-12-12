# Gemini Image Features API 사용 가이드

제미니를 통해 이미지의 주요 특징 3가지를 영어로 추출하는 API입니다.

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements_api.txt
```

### 2. 환경변수 설정
`.env` 파일에 GEMINI_API_KEY를 설정해주세요:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. API 서버 실행
```bash
python gemini_features_api.py
```

서버는 기본적으로 `http://localhost:5000`에서 실행됩니다.

### 4. API 테스트
```bash
python test_features_api.py
```

## 📋 API 엔드포인트

### POST /api/features
이미지에서 주요 특징 3가지를 영어로 추출합니다.

**요청 예시 (이미지 URL 사용):**
```json
{
    "image_url": "https://example.com/image.jpg"
}
```

**요청 예시 (Base64 이미지 사용):**
```json
{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

**응답 예시:**
```json
{
    "success": true,
    "features": [
        "Young adult with friendly expression",
        "Dark brown wavy hair",
        "Casual blue shirt"
    ],
    "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**에러 응답 예시:**
```json
{
    "success": false,
    "error": "Either image_url or image_base64 is required",
    "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### GET /api/health
API 서버 상태를 확인합니다.

**응답:**
```json
{
    "status": "healthy",
    "service": "Gemini Image Features API"
}
```

### GET /
API 정보를 확인합니다.

## 🧪 사용 예시

### cURL 사용
```bash
# 이미지 URL로 요청
curl -X POST http://localhost:5000/api/features \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg"
  }'

# Base64 이미지로 요청
curl -X POST http://localhost:5000/api/features \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQ..."
  }'
```

### Python 사용
```python
import requests
import json

# 이미지 URL로 요청
response = requests.post('http://localhost:5000/api/features', 
                        json={'image_url': 'https://example.com/image.jpg'})

if response.status_code == 200:
    data = response.json()
    if data['success']:
        print("추출된 특징들:")
        for i, feature in enumerate(data['features'], 1):
            print(f"{i}. {feature}")
    else:
        print(f"에러: {data['error']}")
```

### JavaScript 사용
```javascript
fetch('http://localhost:5000/api/features', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        image_url: 'https://example.com/image.jpg'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('추출된 특징들:', data.features);
    } else {
        console.error('에러:', data.error);
    }
});
```

## ⚙️ 환경변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `GEMINI_API_KEY` | 구글 제미니 API 키 (필수) | - |
| `PORT` | API 서버 포트 | 5000 |
| `DEBUG` | 디버그 모드 활성화 | False |

## 🔧 에러 코드

| HTTP 코드 | 설명 |
|-----------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (이미지 URL 또는 Base64 누락) |
| 500 | 서버 내부 오류 (이미지 분석 실패 등) |

## 📝 주의사항

1. **이미지 형식**: JPEG, PNG, WebP 등 일반적인 이미지 형식을 지원합니다.
2. **이미지 크기**: 큰 이미지는 처리 시간이 오래 걸릴 수 있습니다.
3. **API 키**: GEMINI_API_KEY가 반드시 설정되어야 합니다.
4. **특징 개수**: 항상 정확히 3개의 특징을 반환합니다. (부족한 경우 "General appearance"로 채움)
5. **언어**: 반환되는 특징은 영어로 제공됩니다.

## 🔍 트러블슈팅

### API 키 관련 오류
```
ValueError: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.
```
→ `.env` 파일에 올바른 GEMINI_API_KEY를 설정해주세요.

### 이미지 로드 실패
```
"Failed to analyze image features"
```
→ 이미지 URL이 올바른지, 이미지에 접근 가능한지 확인해주세요.

### 서버 연결 실패
```
requests.exceptions.ConnectionError
```
→ API 서버가 실행 중인지 확인해주세요. (`python gemini_features_api.py`)