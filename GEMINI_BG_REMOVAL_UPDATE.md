# Gemini 기반 배경 제거 업데이트

## 개요
`fastapi_image_describe.py`에 Gemini AI를 활용한 고급 배경 제거 기능이 통합되었습니다.

## 주요 변경사항

### 1. 새로운 기능
- **Gemini 이미지 분석**: 배경 제거 전 이미지를 분석하여 최적의 처리 방법 결정
- **적응형 모델 선택**: 이미지 특성에 따라 다른 rembg 모델 자동 선택
- **고급 후처리**: 가우시안 필터를 사용한 경계 부드럽게 처리

### 2. 추가된 함수들

#### `analyze_image_with_gemini_for_bg_removal(image_data, model_name)`
- Gemini를 사용하여 이미지 분석
- 주요 피사체, 배경 유형, 사람 감지, 복잡도 등 파악
- JSON 형식으로 분석 결과 반환

#### `remove_background_advanced(image_data, analysis)`
- Gemini 분석 결과를 활용한 고급 배경 제거
- 분석 결과에 따라 최적의 rembg 모델 선택:
  - 사람 감지 시: `u2net_human_seg` 모델
  - 복잡한 배경: `u2netp` 모델
  - 일반 배경: `u2net` 모델
- 알파 매팅과 가우시안 필터로 경계 품질 개선

#### 수정된 `remove_background_from_url(image_url)`
- Gemini API 키가 있으면 자동으로 Gemini 분석 수행
- 분석 결과에 따라 고급 배경 제거 또는 기본 방법 사용
- 더 안정적인 이미지 다운로드 (User-Agent 헤더 추가)

### 3. 작동 흐름

```
1. 이미지 URL 다운로드
   ↓
2. Gemini로 이미지 분석 (옵션)
   - 주요 피사체 감지
   - 배경 복잡도 평가
   - 사람 존재 여부 확인
   ↓
3. 분석 결과에 따른 최적 모델 선택
   - 사람: u2net_human_seg
   - 복잡: u2netp
   - 일반: u2net
   ↓
4. 배경 제거 수행
   - 알파 매팅 적용
   - 경계 부드럽게 처리
   ↓
5. Supabase에 업로드
   ↓
6. 공개 URL 반환
```

### 4. 필요한 환경 변수
```bash
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ACCESS_KEY=your_supabase_key
```

### 5. 새로운 의존성
```
scipy==1.11.4
numpy==1.24.3
rembg==2.0.50
```

### 6. 사용 예시

#### Cartoonize API 호출 시
```python
response = requests.post(
    "http://localhost:8000/cartoonize",
    json={
        "image_url": "https://example.com/image.jpg",
        "character_id": "character_123",
        "custom_prompt": "cartoon style",
        "job_id": "job_001"
    }
)

result = response.json()
# result["background_removed_image_url"] - Gemini 기반으로 배경 제거된 이미지 URL
```

### 7. 성능 개선
- **더 정확한 배경 제거**: Gemini 분석으로 이미지 특성 파악
- **적응형 처리**: 이미지에 따라 최적의 모델 자동 선택
- **품질 향상**: 알파 매팅과 가우시안 필터로 자연스러운 경계

### 8. 테스트
```bash
# 패키지 설치
pip install -r requirements_fastapi.txt

# 서버 실행
python fastapi_image_describe.py

# 테스트 스크립트 실행
python test_gemini_bg_removal.py
```

### 9. 주의사항
- Gemini API 키가 없으면 기본 rembg 방법으로 자동 폴백
- 이미지 분석에 약간의 추가 시간 소요 (1-2초)
- 전체적인 품질은 향상되지만 처리 시간은 약간 증가

## 결론
Gemini AI를 활용하여 더 스마트하고 정확한 배경 제거가 가능해졌습니다. 
이미지 특성을 분석하여 최적의 처리 방법을 자동으로 선택하므로 다양한 이미지에 대해 더 나은 결과를 제공합니다.
