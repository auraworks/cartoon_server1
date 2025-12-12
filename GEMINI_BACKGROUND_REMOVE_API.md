# Gemini 배경 제거 API 가이드

Gemini AI를 활용한 스마트 배경 제거 기능을 제공하는 API입니다. 기존의 기본적인 배경 제거 라이브러리보다 더 정교하고 지능적인 결과를 제공합니다.

## 주요 특징

- 🤖 **Gemini AI 분석**: 이미지를 먼저 분석하여 최적의 배경 제거 방법 추천
- 🎯 **다중 알고리즘**: rembg, GrabCut, Watershed 등 다양한 방법 지원
- 📊 **상세 분석 정보**: 주요 객체, 배경 타입, 처리 난이도 등 제공
- ⚡ **성능 최적화**: 이미지 특성에 따른 최적 방법 자동 선택
- 🔧 **후처리 개선**: 가장자리 개선, 노이즈 제거 등

## API 엔드포인트

### POST `/remove-background`

배경 제거를 수행합니다.

#### 요청 (Request)

```json
{
  "image_url": "https://example.com/image.jpg",
  "method": "gemini",           // "gemini", "rembg", "auto" 중 선택
  "analysis_only": false,       // true시 분석만 수행
  "job_id": "optional-job-id"   // 선택적 작업 ID
}
```

**필수 필드:**
- `image_url`: 처리할 이미지의 URL

**선택 필드:**
- `method`: 사용할 방법 (기본값: "gemini")
  - `"gemini"`: Gemini 분석 후 최적 방법 사용
  - `"rembg"`: 기본 rembg 라이브러리 사용
  - `"auto"`: 자동 선택
- `analysis_only`: 분석만 수행할지 여부 (기본값: false)
- `job_id`: 작업 추적을 위한 ID (자동 생성)

#### 응답 (Response)

##### 성공 응답

```json
{
  "success": true,
  "result_image_url": "https://storage.url/background_removed/image.png",
  "analysis": {
    "main_subject": "person",
    "subject_position": "center",
    "background_type": "indoor",
    "edges_clarity": 8,
    "color_contrast": 7,
    "recommended_method": "grabcut",
    "difficulty_level": 4,
    "tips": "객체와 배경의 대비가 좋아 정확한 분리가 가능합니다."
  },
  "method_used": "grabcut",
  "processing_time": 3.2,
  "job_id": "12345678-abcd-efgh"
}
```

##### 실패 응답

```json
{
  "success": false,
  "error_message": "이미지 다운로드에 실패했습니다.",
  "processing_time": 1.1,
  "job_id": "12345678-abcd-efgh"
}
```

## 분석 정보 상세

### `analysis` 객체 필드

- **`main_subject`**: 주요 객체 타입
  - 예: "person", "cat", "car", "flower", "object"
  
- **`subject_position`**: 객체 위치
  - 예: "center", "left", "right", "top", "bottom"
  
- **`background_type`**: 배경 타입
  - 예: "indoor", "outdoor", "plain", "complex", "transparent"
  
- **`edges_clarity`**: 경계 명확도 (1-10)
  - 높을수록 배경 제거가 쉬움
  
- **`color_contrast`**: 색상 대비도 (1-10)
  - 높을수록 객체와 배경 구분이 명확
  
- **`recommended_method`**: 추천 방법
  - "rembg": 기본 배경 제거
  - "grabcut": GrabCut 알고리즘
  - "watershed": Watershed 분할
  
- **`difficulty_level`**: 처리 난이도 (1-10)
  - 1-3: 쉬움, 4-6: 보통, 7-10: 어려움
  
- **`tips`**: 처리 팁 및 주의사항

## 사용 예시

### 1. 기본 배경 제거

```python
import requests

response = requests.post("http://localhost:8000/remove-background", json={
    "image_url": "https://example.com/portrait.jpg"
})

result = response.json()
if result["success"]:
    print(f"배경 제거 완료: {result['result_image_url']}")
    print(f"사용된 방법: {result['method_used']}")
    print(f"처리 시간: {result['processing_time']}초")
```

### 2. 이미지 분석만 수행

```python
response = requests.post("http://localhost:8000/remove-background", json={
    "image_url": "https://example.com/photo.jpg",
    "analysis_only": True
})

result = response.json()
if result["success"]:
    analysis = result["analysis"]
    print(f"주요 객체: {analysis['main_subject']}")
    print(f"추천 방법: {analysis['recommended_method']}")
    print(f"난이도: {analysis['difficulty_level']}/10")
    print(f"팁: {analysis['tips']}")
```

### 3. 특정 방법 지정

```python
# 기본 rembg 방법 사용
response = requests.post("http://localhost:8000/remove-background", json={
    "image_url": "https://example.com/image.jpg",
    "method": "rembg"
})
```

## 성능 비교

| 방법 | 속도 | 품질 | 적합한 이미지 |
|------|------|------|---------------|
| rembg | 빠름 | 보통 | 일반적인 인물/객체 |
| Gemini + GrabCut | 보통 | 높음 | 명확한 경계의 객체 |
| Gemini + Watershed | 느림 | 매우 높음 | 복잡한 배경의 객체 |

## 제한사항

- 최대 이미지 크기: 10MB
- 지원 형식: JPG, JPEG, PNG, WEBP
- 처리 시간: 이미지 크기와 복잡도에 따라 1-30초
- API 요청 제한: 분당 60회

## 오류 코드

| 상태 코드 | 오류 메시지 | 해결 방법 |
|-----------|-------------|-----------|
| 400 | Invalid image URL | 올바른 이미지 URL 확인 |
| 422 | Validation error | 요청 형식 확인 |
| 500 | Processing failed | 서버 로그 확인, 다른 이미지로 재시도 |

## 환경 설정

### 필수 환경 변수

```bash
# .env 파일
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url      # 선택적
SUPABASE_ACCESS_KEY=your_key        # 선택적
```

### 필수 패키지

```bash
pip install -r requirements_enhanced.txt
```

주요 패키지:
- google-generativeai
- rembg
- opencv-python
- pillow
- numpy
- fastapi
- uvicorn

## 테스트 실행

```bash
# 서버 시작
python fastapi_image_describe.py

# 테스트 실행
python test_gemini_background_remove.py
```

## 개발자 도구

### 로컬 파일 처리

```python
from bg_remover_gemini import remove_background_gemini

# 로컬 파일 처리
success, output_path, analysis = remove_background_gemini("input.jpg")
print(f"결과: {output_path}")
print(f"분석: {analysis}")
```

### 일괄 처리

```python
from bg_remover_gemini import batch_remove_background_gemini

# 폴더 내 모든 이미지 처리
results = batch_remove_background_gemini("./images", "*.jpg,*.png")
for result in results:
    print(result)
```

## 업데이트 로그

### v1.0.0 (2024-01-XX)
- 초기 Gemini 배경 제거 API 출시
- GrabCut, Watershed 알고리즘 지원
- 실시간 이미지 분석 기능
- Supabase 스토리지 연동

## 지원

문제 발생 시:
1. 서버 로그 확인
2. API 키 설정 확인  
3. 이미지 URL 접근 가능 여부 확인
4. 네트워크 연결 상태 확인

개선 사항이나 버그 신고는 이슈 트래커를 이용해 주세요.
