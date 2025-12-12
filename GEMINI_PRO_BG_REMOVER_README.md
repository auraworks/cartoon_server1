# Gemini Pro 배경 제거 API

고급 Gemini 모델(2.0 Flash Experimental, 1.5 Pro)을 사용한 지능형 배경 제거 API입니다.

## 주요 기능

### 1. 이미지 URL 지원
- 웹에서 이미지 URL을 직접 받아 다운로드
- 다양한 이미지 형식 지원 (JPG, PNG, WEBP, BMP)
- 자동 파일 형식 감지 및 처리

### 2. Gemini AI 이미지 분석
- **Gemini 2.0 Flash Experimental** (최신 모델) 기본 사용
- **Gemini 1.5 Pro** 선택 가능
- 이미지 내용 자동 분석:
  - 주요 피사체 감지
  - 배경 복잡도 평가
  - 인물 포함 여부 확인
  - 최적 처리 방법 추천

### 3. 지능형 배경 제거
- AI 분석 결과에 따른 최적 모델 자동 선택:
  - **u2net_human_seg**: 인물 사진용
  - **u2netp**: 복잡한 배경용
  - **u2net**: 일반 이미지용
- 알파 매팅으로 부드러운 경계 처리
- 가우시안 필터를 통한 경계 품질 개선

## 설치 방법

### 1. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. Gemini API 키 설정
`.env` 파일을 생성하고 API 키를 추가:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

API 키 발급: https://makersuite.google.com/app/apikey

### 3. 서버 실행
```bash
python run_gemini_pro_server.py
```

또는 직접 실행:
```bash
uvicorn bg_remover_gemini_pro:app --reload --port 8000
```

## API 엔드포인트

### 1. URL에서 배경 제거
**POST** `/remove-background-url`

#### 요청 파라미터:
- `return_format` (Query Parameter, 선택사항): 
  - `"image"` (기본값): 배경이 제거된 이미지를 직접 반환 (브라우저에서 바로 볼 수 있음)
  - `"json"`: Base64 인코딩된 이미지를 JSON으로 반환

#### 방법 1: 이미지 직접 반환 (기본값)
```json
{
  "image_url": "https://example.com/image.jpg",
  "output_format": "png",
  "quality": 95,
  "use_gemini_analysis": true,
  "model_name": "gemini-2.0-flash-exp"
}
```

**응답:** PNG 이미지 파일 (브라우저에서 바로 표시됨)

**응답 헤더:**
- `Content-Type: image/png`
- `Content-Disposition: inline; filename=removed_background_xxxxx.png`
- `X-Original-URL: https://example.com/image.jpg`
- `X-Model-Used: gemini-2.0-flash-exp`
- `X-Original-Size: 245678`
- `X-Output-Size: 189234`
- `X-Compression-Ratio: 23.0%`

#### 방법 2: JSON 응답 받기
**POST** `/remove-background-url?return_format=json`

```json
{
  "image_url": "https://example.com/image.jpg",
  "output_format": "png",
  "quality": 95,
  "use_gemini_analysis": true,
  "model_name": "gemini-2.0-flash-exp"
}
```

**응답:**
```json
{
  "success": true,
  "message": "배경 제거가 성공적으로 완료되었습니다.",
  "image_base64": "...",
  "metadata": {
    "original_url": "https://example.com/image.jpg",
    "original_size": 245678,
    "output_size": 189234,
    "compression_ratio": "23.0%",
    "timestamp": "2024-01-15T10:30:00",
    "model_used": "gemini-2.0-flash-exp",
    "analysis": {
      "main_subject": "사람",
      "background_type": "복잡한 배경",
      "has_person": true,
      "complexity": "medium",
      "recommended_method": "u2net_human_seg",
      "description": "..."
    }
  }
}
```

### 2. 파일 업로드로 배경 제거
**POST** `/remove-background-file`

Form Data:
- `file`: 이미지 파일
- `use_gemini_analysis`: true/false
- `model_name`: "gemini-2.0-flash-exp"

**응답:** PNG 이미지 파일

### 3. 이미지 분석만 수행
**POST** `/analyze-image`

Form Data:
- `image_url` 또는 `file`
- `model_name`: Gemini 모델 이름

**응답:**
```json
{
  "success": true,
  "analysis": {
    "main_subject": "강아지",
    "background_type": "단색 배경",
    "has_person": false,
    "complexity": "easy",
    "recommended_method": "u2net",
    "description": "..."
  },
  "model_used": "gemini-2.0-flash-exp",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 4. 헬스 체크
**GET** `/health`

## 테스트

테스트 스크립트 실행:
```bash
python test_gemini_pro_bg_remover.py
```

## 사용 가능한 모델

### Gemini 모델
- `gemini-2.0-flash-exp` (권장, 최신)
- `gemini-1.5-pro` (고성능)
- `gemini-1.5-flash` (빠른 처리)

### 배경 제거 모델
- `u2net`: 일반 이미지
- `u2netp`: 고정밀도
- `u2net_human_seg`: 인물 특화

## 주요 특징

1. **지능형 처리**: Gemini AI가 이미지를 분석하여 최적의 처리 방법 자동 선택
2. **고품질 결과**: 알파 매팅과 가우시안 필터로 부드러운 경계 처리
3. **다양한 입력**: URL 또는 파일 업로드 지원
4. **상세한 메타데이터**: 처리 과정과 결과에 대한 상세 정보 제공
5. **확장 가능**: 새로운 모델 추가 용이

## 성능 최적화 팁

1. **모델 선택**:
   - 빠른 처리: `gemini-1.5-flash`
   - 정확한 분석: `gemini-2.0-flash-exp`
   - 최고 품질: `gemini-1.5-pro`

2. **이미지 크기**: 
   - 권장: 1024x1024 이하
   - 최대: 10MB

3. **배치 처리**: 
   - 여러 이미지는 병렬로 요청하여 처리 시간 단축

## 문제 해결

### GEMINI_API_KEY 오류
`.env` 파일에 올바른 API 키가 설정되어 있는지 확인

### 메모리 부족
큰 이미지 처리 시 발생할 수 있음. 이미지 크기를 줄이거나 서버 메모리 증설

### 느린 처리 속도
- 더 빠른 Gemini 모델 사용 (`gemini-1.5-flash`)
- `use_gemini_analysis`를 false로 설정하여 AI 분석 건너뛰기

## 라이선스

MIT License
