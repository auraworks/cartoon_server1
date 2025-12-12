# 환경변수 설정 가이드

## RapidAPI 배경 제거 기능 설정

이 프로젝트는 RapidAPI의 remove background API를 사용하여 배경 제거 기능을 제공합니다.

### 필요한 환경변수

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 환경변수들을 설정해주세요:

```env
# Gemini API 설정
GEMINI_API_KEY=your_gemini_api_key_here

# Replicate API 설정
REPLICATE_API_TOKEN=your_replicate_api_token_here

# RapidAPI 설정 (배경 제거용)
RAPIDAPI_KEY=83c9d8d142msh1a0fc7490405bd2p1937f6jsnb3258526aab8

# Supabase 설정
SUPABASE_URL=your_supabase_project_url
SUPABASE_ACCESS_KEY=your_supabase_anon_key
```

### RapidAPI 키 설정

현재 코드에는 제공해주신 RapidAPI 키가 기본값으로 설정되어 있습니다:
- API 키: `83c9d8d142msh1a0fc7490405bd2p1937f6jsnb3258526aab8`
- API 호스트: `remove-background18.p.rapidapi.com`

### 변경된 기능

1. **배경 제거 API 변경**: Gemini 기반 → RapidAPI 기반
2. **새로운 함수들**:
   - `remove_background_with_rapidapi()`: RapidAPI 호출
   - `download_image_from_url()`: 결과 이미지 다운로드
   - 업데이트된 `remove_background_from_url()`: 메인 인터페이스

### API 플로우

1. **이미지 URL 전송** → RapidAPI에 배경 제거 요청
2. **결과 URL 수신** → API 응답에서 배경이 제거된 이미지 URL 추출
3. **이미지 다운로드** → 결과 URL에서 이미지 데이터 다운로드
4. **Supabase 업로드** → 다운로드한 이미지를 Supabase 스토리지에 업로드
5. **최종 URL 반환** → 업로드된 이미지의 공개 URL 반환

### 헬스체크

서버 상태는 `/health` 엔드포인트에서 확인할 수 있으며, 모든 필요한 API 키가 설정되었는지 확인합니다:

```json
{
  "status": "healthy",
  "gemini_api": "configured",
  "supabase": "configured", 
  "replicate_api": "configured",
  "rapidapi": "configured"
}
```

### 사용 방법

기존 `/cartoonize` 엔드포인트를 호출하면 자동으로 새로운 RapidAPI 기반 배경 제거 기능이 사용됩니다.

### 주의사항

- RapidAPI 응답 형식에 따라 URL 추출 로직이 달라질 수 있습니다
- 네트워크 타임아웃은 60초로 설정되어 있습니다
- 모든 에러는 로그에 자세히 기록됩니다



