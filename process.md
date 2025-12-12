# main.py 전체 분석 보고서

## 📋 개요

**파일 경로:** `d:\000.FrontEnd\102.image_upload_and_swap\main.py`
**총 라인 수:** 1,324줄
**파일 크기:** 약 579바이트
**역할:** **Gemini 기반 이미지 설명 및 캐릭터 캐리커쳐 생성 API 서버**

이 파일은 `fastapi_image_describe.py`와 거의 동일한 기능을 제공하는 FastAPI 서버입니다. Google Gemini API를 중심으로 이미지 설명, 캐리커쳐 생성, 배경 제거 기능을 통합한 올인원 API 서버입니다.

---

## 🎯 핵심 기능

| 기능 | 엔드포인트 | 메서드 | 주요 역할 |
|------|-----------|--------|---------|
| **이미지 설명** | `/describe` | POST | Gemini로 얼굴 특징 간단히 설명 |
| **캐리커쳐 생성** | `/cartoonize` | POST | 6단계 파이프라인으로 캐릭터 기반 이미지 생성 |
| **헬스 체크** | `/health` | GET | 모든 API 키 설정 확인 |
| **상태 확인** | `/` | GET | API 정상 작동 확인 |

---

## 🏗️ 아키텍처 구조

```
FastAPI 서버 (main.py)
    │
    ├─ Gemini 2.0 Flash (이미지 설명, 번역, 배경 제거)
    ├─ Replicate Flux Kontext Pro (캐리커쳐 생성)
    ├─ RapidAPI (배경 제거 - 우선순위 1)
    ├─ Supabase (데이터베이스 & 스토리지)
    └─ NumPy/SciPy (이미지 처리 보조)
```

---

## 📦 의존성 및 라이브러리

### 주요 라이브러리

```python
# 웹 프레임워크
fastapi                    # API 서버
uvicorn                    # ASGI 서버
pydantic                   # 데이터 검증
CORSMiddleware             # CORS 설정

# AI 서비스
google.generativeai        # Gemini API
replicate                  # Replicate API

# 데이터베이스 & 스토리지
supabase                   # Supabase 클라이언트

# 이미지 처리
PIL (Pillow)               # 이미지 조작
numpy                      # 배열 연산
scipy.ndimage              # 가우시안 블러

# 유틸리티
requests                   # HTTP 요청
dotenv                     # 환경변수 로드
uuid                       # 고유 ID 생성
datetime, time             # 시간 처리
json                       # JSON 파싱
tempfile                   # 임시 파일
urllib.parse               # URL 파싱
```

---

## 🔑 환경변수 설정

```python
# .env 파일에서 로드되는 환경변수
GEMINI_API_KEY             # Google Gemini API 키
REPLICATE_API_TOKEN        # Replicate API 토큰
SUPABASE_URL               # Supabase 프로젝트 URL
SUPABASE_ACCESS_KEY        # Supabase 액세스 키
RAPIDAPI_KEY               # RapidAPI 키 (선택적)
```

**참고:** line 759에 RapidAPI 키가 하드코딩되어 있습니다. 보안상 `.env` 파일로 이동 권장.

---

## 🔧 주요 클래스 및 데이터 모델

### 요청 모델 (Request Models)

#### 1. **ImageDescribeRequest** (line 44-48)

```python
class ImageDescribeRequest(BaseModel):
    image_url: HttpUrl              # 분석할 이미지 URL
    character_id: Optional[str]     # 캐릭터 ID (선택)
    custom_prompt: Optional[str]    # 커스텀 프롬프트 (선택)
    job_id: Optional[str]           # 작업 ID (선택)
```

**용도:** 이미지 설명 요청

#### 2. **CartoonizeRequest** (line 50-54)

```python
class CartoonizeRequest(BaseModel):
    image_url: HttpUrl          # 캐리커쳐화할 이미지 URL
    character_id: str           # 캐릭터 ID (필수)
    custom_prompt: str          # 커스텀 프롬프트 (필수)
    job_id: Optional[str]       # 작업 ID (선택)
```

**용도:** 캐리커쳐 생성 요청

### 응답 모델 (Response Models)

#### 3. **ImageDescribeResponse** (line 56-63)

```python
class ImageDescribeResponse(BaseModel):
    success: bool                          # 성공 여부
    description: Optional[str]             # 이미지 설명
    character_id: Optional[str]            # 캐릭터 ID
    character_image_url: Optional[str]     # 캐릭터 이미지 URL
    processing_time: Optional[float]       # 처리 시간
    job_id: Optional[str]                  # 작업 ID
    error: Optional[str]                   # 에러 메시지
```

#### 4. **TimingInfo** (line 65-72)

```python
class TimingInfo(BaseModel):
    character_image_fetch: Optional[float]    # 캐릭터 이미지 가져오기 시간
    face_description: Optional[float]         # 얼굴 묘사 생성 시간
    prompt_translation: Optional[float]       # 프롬프트 번역 시간
    image_generation: Optional[float]         # 이미지 생성 시간
    background_removal: Optional[float]       # 배경 제거 시간
    image_upload: Optional[float]             # 업로드 시간
    total_time: Optional[float]               # 총 소요 시간
```

**용도:** 각 단계별 성능 측정

#### 5. **CartoonizeResponse** (line 74-84)

```python
class CartoonizeResponse(BaseModel):
    success: bool                                  # 성공 여부
    result_image_url: Optional[str]                # 생성된 이미지 URL
    background_removed_image_url: Optional[str]    # 배경 제거된 이미지 URL
    character_id: Optional[str]                    # 캐릭터 ID
    character_image_url: Optional[str]             # 캐릭터 이미지 URL
    translated_prompt: Optional[str]               # 번역된 프롬프트
    face_description: Optional[str]                # 얼굴 묘사
    timing: Optional[TimingInfo]                   # 타이밍 정보
    job_id: Optional[str]                          # 작업 ID
    error: Optional[str]                           # 에러 메시지
```

---

## 🚀 API 엔드포인트 상세 분석

### 1. **GET /** - 상태 확인 (line 969-972)

**역할:** API 정상 작동 확인

**응답 예시:**
```json
{
    "message": "이미지 묘사 API가 정상 작동중입니다.",
    "status": "healthy"
}
```

---

### 2. **POST /describe** - 이미지 설명 (line 974-1049)

**역할:** 이미지 URL을 받아서 Gemini API로 간단한 얼굴 특징을 영어로 설명

#### 요청 예시

```json
{
    "image_url": "https://example.com/face.jpg",
    "character_id": "char_001",
    "custom_prompt": "얼굴의 주요 특징을 간단히 설명해주세요",
    "job_id": "job_12345"
}
```

#### 처리 흐름

```
1. 환경변수 확인 (GEMINI_API_KEY)
    ↓
2. character_id가 있으면 캐릭터 이미지 URL 조회 (Supabase)
    ↓
3. describe_face_simple() 호출 → Gemini API로 얼굴 설명
    ↓
4. 처리 시간 계산
    ↓
5. job_id가 있으면 Supabase에 결과 업데이트
    ↓
6. 응답 반환
```

#### 응답 예시 (성공)

```json
{
    "success": true,
    "description": "big brown eyes, round face, short black hair, wear glasses",
    "character_id": "char_001",
    "character_image_url": "https://...",
    "processing_time": 3.45,
    "job_id": "job_12345"
}
```

#### 응답 예시 (실패)

```json
{
    "success": false,
    "character_id": "char_001",
    "character_image_url": "https://...",
    "processing_time": 2.10,
    "job_id": "job_12345",
    "error": "이미지 묘사를 생성할 수 없습니다. 이미지 URL을 확인해주세요."
}
```

---

### 3. **POST /cartoonize** - 캐리커쳐 생성 (line 1051-1280)

**역할:** 입력 이미지와 캐릭터 이미지를 결합하여 커스텀 프롬프트에 맞는 캐리커쳐 생성

#### 요청 예시

```json
{
    "image_url": "https://example.com/face.jpg",
    "character_id": "char_001",
    "custom_prompt": "해변에 앉아있는 모습",
    "job_id": "job_67890"
}
```

#### 6단계 처리 흐름

```
1단계: 캐릭터 이미지 URL 가져오기 (Supabase)
   ├─ get_random_character_image(character_id)
   └─ character 테이블에서 picture_cartoon 중 랜덤 선택

2단계: 입력 이미지의 얼굴 묘사 생성 (Gemini)
   ├─ describe_face_simple(image_url)
   └─ 예: "short black hair, big eyes, round face"

3단계: 커스텀 프롬프트 번역 (한국어 → 영어)
   ├─ translate_to_english(custom_prompt)
   ├─ 직업 관련 표현 제거
   └─ 예: "sitting on beach" (from "해변에 앉아있는 모습")

4단계: Replicate API로 이미지 생성
   ├─ generate_cartoon_with_replicate()
   ├─ 모델: black-forest-labs/flux-kontext-pro
   ├─ 프롬프트: "he {face_description} and {translated_prompt} and white background"
   └─ 예: "he short black hair, big eyes and sitting on beach and white background"

5단계: 생성된 이미지에서 배경 제거
   ├─ remove_background_from_url(result_image_url)
   ├─ 우선순위 1: RapidAPI
   └─ 실패 시 Gemini 사용 (다단계 폴백)

6단계: 배경 제거된 이미지를 Supabase에 업로드
   ├─ upload_image_to_supabase(image_data)
   └─ PNG 형식으로 저장
```

#### 타이밍 정보

각 단계별 소요 시간이 `timing` 객체에 기록됩니다:

```python
timing = {
    "character_image_fetch": 0.85,      # 1단계
    "face_description": 3.20,           # 2단계
    "prompt_translation": 2.15,         # 3단계
    "image_generation": 45.60,          # 4단계 (가장 오래 걸림)
    "background_removal": 8.30,         # 5단계
    "image_upload": 2.10,               # 6단계
    "total_time": 62.20                 # 전체
}
```

#### 응답 예시 (성공)

```json
{
    "success": true,
    "result_image_url": "https://replicate.delivery/.../output.jpg",
    "background_removed_image_url": "https://supabase.co/.../cartoon_bg_removed_abc123.png",
    "character_id": "char_001",
    "character_image_url": "https://supabase.co/.../character.jpg",
    "translated_prompt": "sitting on beach",
    "face_description": "short black hair, big eyes, round face",
    "timing": {
        "character_image_fetch": 0.85,
        "face_description": 3.20,
        "prompt_translation": 2.15,
        "image_generation": 45.60,
        "background_removal": 8.30,
        "image_upload": 2.10,
        "total_time": 62.20
    },
    "job_id": "job_67890"
}
```

#### 응답 예시 (실패)

```json
{
    "success": false,
    "character_id": "char_001",
    "character_image_url": "https://...",
    "translated_prompt": "sitting on beach",
    "face_description": "short black hair, big eyes",
    "timing": {
        "character_image_fetch": 0.85,
        "face_description": 3.20,
        "prompt_translation": 2.15,
        "image_generation": 45.60,
        "total_time": 51.80
    },
    "job_id": "job_67890",
    "error": "이미지 생성에 실패했습니다. 가능한 원인:\n1. Replicate API 서버 문제\n2. 입력 이미지 형식 문제\n3. API 토큰 문제\n4. 네트워크 연결 문제\n서버 로그를 확인해주세요."
}
```

---

### 4. **GET /health** - 헬스 체크 (line 1282-1315)

**역할:** 모든 필수 API 키가 설정되어 있는지 확인

#### 응답 예시 (정상)

```json
{
    "status": "healthy",
    "gemini_api": "configured",
    "supabase": "configured",
    "replicate_api": "configured",
    "rapidapi": "configured"
}
```

#### 응답 예시 (비정상)

```json
{
    "status": "unhealthy",
    "error": "GEMINI_API_KEY가 설정되지 않음"
}
```

---

## 🧩 핵심 함수 상세 분석

### 1. **get_gemini_client()** (line 86-93)

```python
def get_gemini_client():
    """Gemini 클라이언트를 설정합니다."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')
```

**사용 모델:** `gemini-2.0-flash-exp` (최신 실험 모델)

---

### 2. **get_supabase_client()** (line 97-105)

```python
def get_supabase_client() -> Client:
    """Supabase 클라이언트를 설정합니다."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ACCESS_KEY")

    if not url or not key:
        raise ValueError("환경변수가 설정되지 않았습니다.")

    return create_client(url, key)
```

---

### 3. **get_random_character_image()** (line 107-149)

**역할:** Supabase의 `character` 테이블에서 `picture_cartoon` 배열 중 랜덤 이미지 URL 반환

#### 데이터베이스 쿼리

```python
response = supabase.table("character").select("picture_cartoon").eq("id", character_id).execute()
```

#### 데이터 형식 처리

```python
# picture_cartoon 필드는 배열 형태
[
    {"url": "https://..."},      # 딕셔너리 형태
    "https://...",               # 문자열 형태
    {"url": "https://..."}
]

# 랜덤 선택
random_item = random.choice(picture_cartoon)

# 딕셔너리면 'url' 키 추출
if isinstance(random_item, dict) and 'url' in random_item:
    return random_item['url']
# 문자열이면 그대로 반환
elif isinstance(random_item, str):
    return random_item
```

---

### 4. **describe_face_simple()** (line 161-202)

**역할:** Gemini API로 이미지의 얼굴 특징을 간단한 영어 문구로 설명

#### 프롬프트 (기본)

```
Please describe the person's appearance in simple keywords. Focus only on:
1. Eyes: size and features (big eyes, small eyes, wear glasses, etc.)
2. Face: basic features (round face, oval face, etc.)
3. Facial accessories: if any (wear glasses, earrings, etc.)

Respond with simple phrases like: "big brown eyes, round face, wear glasses"
Keep it very simple and use only basic descriptive phrases.
```

#### 예시 응답

```
"short black hair, big brown eyes, round face, wear glasses"
```

---

### 5. **translate_to_english()** (line 204-245)

**역할:** 한국어 프롬프트를 영어로 번역하되, 직업 관련 표현은 제거

#### 프롬프트

```
Translate this Korean text to English, but follow these rules:

1. INCLUDE hair descriptions (hair color, hairstyle, hair length, etc.)
2. EXCLUDE professional/occupational expressions (like "navy officer", "doctor", "teacher", etc.)
3. ONLY translate descriptions about:
   - Physical appearance (including hair, face, eyes, body, etc.)
   - Actions and behaviors
   - Clothing and accessories (but not uniforms that indicate profession)
   - Expressions and emotions

4. Remove any mentions of jobs, titles, or professional roles
5. Focus only on what the person looks like and what they are doing

Korean text: {korean_text}

Provide only the translated English text with appearance and behavior descriptions:
```

#### 예시

**입력:** `"해변에 앉아있는 해군 장교"`
**출력:** `"sitting on beach"` (해군 장교 부분 제거됨)

---

### 6. **generate_cartoon_with_replicate()** (line 247-375)

**역할:** Replicate API를 사용하여 캐릭터 이미지와 프롬프트를 결합한 캐리커쳐 생성

#### Replicate 모델

```python
model = "black-forest-labs/flux-kontext-pro"
```

#### 입력 데이터

```python
input_data = {
    "prompt": "he {face_description} and {translated_prompt} and white background",
    "input_image": character_image_url,
    "output_format": "jpg"
}
```

**프롬프트 예시:**
```
"he short black hair, big brown eyes and sitting on beach and white background"
```

#### 재시도 로직

```python
max_retries = 2
timeout_seconds = 300  # 5분

for attempt in range(max_retries + 1):
    try:
        output = replicate.run("black-forest-labs/flux-kontext-pro", input=input_data)
        break
    except Exception as retry_error:
        if attempt < max_retries:
            time.sleep(5)  # 5초 대기
        else:
            raise
```

#### 응답 처리 (다양한 형식 지원)

```python
# 1. 객체에 url 속성/메서드가 있는 경우
if hasattr(output, 'url'):
    result_url = output.url() if callable(output.url) else output.url

# 2. 문자열인 경우
elif isinstance(output, str):
    result_url = output

# 3. 리스트인 경우
elif isinstance(output, list):
    result_url = output[0] if output else None

# 4. 딕셔너리인 경우
elif isinstance(output, dict):
    result_url = output.get('url') or output.get('output')
```

---

### 7. **배경 제거 함수들**

#### 7.1 **remove_background_from_url()** (line 857-883)

**메인 진입점** - RapidAPI를 먼저 시도

```python
def remove_background_from_url(image_url: str) -> Optional[bytes]:
    # RapidAPI로 배경 제거 시도
    background_removed_data = remove_background_with_rapidapi(image_url)
    return background_removed_data
```

#### 7.2 **remove_background_with_rapidapi()** (line 730-818)

**RapidAPI 배경 제거 서비스 호출**

```python
conn = http.client.HTTPSConnection("remove-background18.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "83c9d8d142msh1a0fc7490405bd2p1937f6jsnb3258526aab8",  # 하드코딩 (보안 이슈)
    'x-rapidapi-host': "remove-background18.p.rapidapi.com",
    'Content-Type': "application/x-www-form-urlencoded"
}

payload = urllib.parse.urlencode({'image_url': image_url})
conn.request("POST", "/public/remove-background", payload, headers)
```

#### 7.3 **Gemini 기반 배경 제거 (폴백 메커니즘)**

**3단계 폴백:**

```
1. remove_background_with_gemini() [line 450-523]
   └─ Gemini에 직접 투명 배경 이미지 생성 요청

2. create_transparent_background_mask() [line 525-588]
   └─ Gemini로 마스크 정보 생성 후 적용

3. create_simple_transparent_background() [line 648-667]
   └─ 색상 기반 단순 배경 제거 (최후 수단)
```

#### 7.4 **analyze_image_with_gemini_for_bg_removal()** (line 377-448)

**Gemini로 배경 제거를 위한 이미지 분석**

**프롬프트:**
```
이 이미지를 분석하고 다음 정보를 JSON 형식으로 제공해주세요:

1. main_subject: 이미지의 주요 피사체 설명
2. background_type: 배경 유형 (단색, 그라데이션, 복잡한 배경 등)
3. has_person: 사람이 있는지 여부 (true/false)
4. complexity: 배경 제거 난이도 (easy, medium, hard)
5. recommended_method: 권장 배경 제거 방법
6. description: 이미지 전체 설명

JSON 형식으로만 응답해주세요.
```

**응답 예시:**
```json
{
    "main_subject": "person wearing blue shirt",
    "background_type": "white solid color",
    "has_person": true,
    "complexity": "easy",
    "recommended_method": "color_based",
    "description": "A person in blue shirt against white background"
}
```

#### 7.5 **create_simple_transparent_background_from_pil()** (line 669-728)

**색상 기반 단순 배경 제거 (NumPy + SciPy 사용)**

```python
# 1. 모서리 픽셀의 평균 색상을 배경색으로 간주
edge_pixels = []
edge_pixels.extend(img_array[0, :, :3])    # 상단
edge_pixels.extend(img_array[-1, :, :3])   # 하단
edge_pixels.extend(img_array[:, 0, :3])    # 좌측
edge_pixels.extend(img_array[:, -1, :3])   # 우측
bg_color = np.mean(edge_pixels, axis=0)

# 2. 배경색과의 거리 계산
color_diff = np.linalg.norm(img_array[:, :, :3] - bg_color, axis=2)
threshold = 50  # 색상 차이 임계값

# 3. 알파 채널 설정
alpha_channel = np.where(color_diff < threshold, 0, 255)

# 4. 가우시안 블러로 가장자리 부드럽게
alpha_smooth = gaussian_filter(alpha_channel.astype(float), sigma=1.0)
img_array[:, :, 3] = np.clip(alpha_smooth, 0, 255).astype(np.uint8)
```

---

### 8. **upload_image_to_supabase()** (line 885-931)

**역할:** 이미지 데이터를 Supabase Storage에 업로드

```python
def upload_image_to_supabase(image_data: bytes, file_name: str = None) -> Optional[str]:
    supabase = get_supabase_client()

    # 파일명 자동 생성
    if not file_name:
        file_name = f"bg_removed_{uuid.uuid4().hex}.png"

    bucket_name = "images"

    # 이미지 업로드
    upload_response = supabase.storage.from_(bucket_name).upload(
        path=file_name,
        file=image_data,
        file_options={"content-type": "image/png"}
    )

    # 공개 URL 생성
    public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
    return public_url
```

---

### 9. **update_image_result_in_supabase()** (line 933-967)

**역할:** Supabase의 `image` 테이블에 작업 결과 업데이트

```python
def update_image_result_in_supabase(job_id: str, result_data: dict) -> bool:
    supabase = get_supabase_client()

    # job_id로 행을 찾아서 result 컬럼 업데이트
    response = supabase.table("image").update({
        "result": result_data
    }).eq("job_id", job_id).execute()

    return bool(response.data)
```

**데이터베이스 스키마 (추정):**
```sql
CREATE TABLE image (
    job_id TEXT PRIMARY KEY,
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔄 완전한 작업 흐름 다이어그램

### POST /cartoonize 전체 흐름

```
클라이언트 요청
    ↓
[환경변수 검증]
├─ GEMINI_API_KEY
├─ REPLICATE_API_TOKEN
├─ SUPABASE_URL
└─ SUPABASE_ACCESS_KEY
    ↓
[1단계: 캐릭터 이미지 조회]
get_random_character_image(character_id)
    ↓
Supabase DB 쿼리
    ↓
picture_cartoon 배열에서 랜덤 선택
    ↓
[2단계: 얼굴 묘사 생성]
describe_face_simple(image_url)
    ↓
Gemini API 호출
    ↓
"short black hair, big eyes, round face"
    ↓
[3단계: 프롬프트 번역]
translate_to_english(custom_prompt)
    ↓
Gemini API 호출 (번역 + 직업 제거)
    ↓
"sitting on beach"
    ↓
[4단계: 캐리커쳐 생성]
generate_cartoon_with_replicate()
    ↓
프롬프트 결합: "he short black hair, big eyes and sitting on beach and white background"
    ↓
Replicate API 호출 (Flux Kontext Pro)
    ↓
생성된 이미지 URL 반환
    ↓
[5단계: 배경 제거]
remove_background_from_url(result_image_url)
    ↓
┌─────────────┬─────────────┬─────────────┐
│  RapidAPI   │  Gemini AI  │  색상 기반   │
│  (1순위)    │  (2순위)    │  (3순위)    │
└─────────────┴─────────────┴─────────────┘
    ↓
배경 제거된 이미지 데이터 (bytes)
    ↓
[6단계: Supabase 업로드]
upload_image_to_supabase(image_data)
    ↓
"cartoon_bg_removed_abc123.png"
    ↓
공개 URL 반환
    ↓
[결과 업데이트]
update_image_result_in_supabase(job_id, result_data)
    ↓
Supabase DB 업데이트 (result 컬럼)
    ↓
[응답 생성]
CartoonizeResponse 객체 생성
    ↓
클라이언트에게 반환
```

---

## ⚙️ CORS 설정 (line 34-41)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 모든 도메인 허용 (운영 환경에서는 제한 필요)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**⚠️ 보안 경고:** 운영 환경에서는 `allow_origins`를 특정 도메인으로 제한해야 합니다.

---

## 📊 성능 및 타임아웃

### 타임아웃 설정

```python
# 이미지 다운로드 타임아웃
requests.get(image_url, timeout=60)

# Replicate API 타임아웃
timeout_seconds = 300  # 5분
```

### 재시도 정책

```python
# Replicate API 재시도
max_retries = 2
for attempt in range(max_retries + 1):
    try:
        output = replicate.run(...)
        break
    except Exception:
        if attempt < max_retries:
            time.sleep(5)  # 5초 대기
        else:
            raise
```

---

## 🐛 에러 처리 전략

### 1. **환경변수 누락**

```python
if not api_key:
    raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
```

### 2. **API 호출 실패**

```python
try:
    response = model.generate_content([prompt, image])
except Exception as e:
    print(f"이미지 묘사 중 오류 발생: {str(e)}")
    return None
```

### 3. **다단계 폴백 (배경 제거)**

```
RapidAPI 실패
    ↓
Gemini 직접 생성 시도
    ↓
Gemini 마스크 기반 시도
    ↓
색상 기반 단순 처리
    ↓
원본 이미지 반환
```

---

## 🔒 보안 고려사항

### ⚠️ 발견된 보안 이슈

1. **하드코딩된 API 키** (line 759)
```python
'x-rapidapi-key': "83c9d8d142msh1a0fc7490405bd2p1937f6jsnb3258526aab8"  # 하드코딩됨
```

**권장 수정:**
```python
'x-rapidapi-key': os.getenv("RAPIDAPI_KEY")
```

2. **CORS 전면 개방** (line 37)
```python
allow_origins=["*"]  # 모든 도메인 허용
```

**권장 수정:**
```python
allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
```

---

## 📝 로깅 시스템

### 로그 이모지 코드

```python
print("✅ 성공")
print("❌ 실패")
print("⚠️ 경고")
print("🔍 분석 중")
print("📥 다운로드")
print("📤 업로드")
print("🎨 생성 중")
print("🎭 배경 제거")
print("🚀 API 호출")
print("📊 통계")
print("🔄 재시도")
```

### 로그 예시

```
📥 1단계: 캐릭터 이미지 URL 가져오는 중...
✅ 1단계 완료 (소요시간: 0.85초)
🔍 2단계: 입력 이미지의 얼굴 묘사 생성 중...
✅ 2단계 완료 (소요시간: 3.20초)
🔄 3단계: 커스텀 프롬프트를 영어로 번역 중...
✅ 3단계 완료 (소요시간: 2.15초)
🎨 4단계: Replicate API로 이미지 생성 중...
🚀 Replicate API 호출 시작...
⏱️ API 호출 소요 시간: 45.60초
✅ 4단계 완료 (소요시간: 45.60초)
🎭 5단계: 생성된 이미지에서 배경 제거 중...
✅ 5단계 완료 (소요시간: 8.30초)
📤 6단계: 배경 제거된 이미지를 Supabase에 업로드 중...
✅ 6단계 완료 (소요시간: 2.10초)
🎉 모든 단계 완료! 전체 소요시간: 62.20초
```

---

## 🚀 서버 실행 (line 1317-1323)

```python
if __name__ == "__main__":
    uvicorn.run(
        "fastapi_image_describe:app",   # 모듈명:앱명
        host="0.0.0.0",                  # 모든 인터페이스에서 접근 허용
        port=8000,                       # 포트 번호
        reload=True                      # 코드 변경 시 자동 재시작
    )
```

**실행 명령:**
```bash
python main.py
```

**또는:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📈 성능 최적화 포인트

### 1. **이미지 크기 조정** (line 468-474)

```python
max_size = 1024
if max(image.size) > max_size:
    ratio = max_size / max(image.size)
    new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
    image = image.resize(new_size, Image.Resampling.LANCZOS)
```

**목적:** Gemini API 호출 효율성 향상

### 2. **캐싱 고려사항**

현재 캐싱 없음. 다음 항목들에 대한 캐싱 추가 권장:

- `get_random_character_image()` - 캐릭터 이미지 목록
- `describe_face_simple()` - 동일 이미지에 대한 반복 설명
- Gemini API 응답

### 3. **비동기 처리 고려**

현재 동기 처리. 다음 작업을 비동기로 전환 권장:

- 이미지 다운로드
- API 호출 (Gemini, Replicate, RapidAPI)
- Supabase 업로드

---

## 🔍 fastapi_image_describe.py와의 비교

| 항목 | main.py | fastapi_image_describe.py |
|------|---------|--------------------------|
| **파일 크기** | 1,324줄 | 더 큼 (추정) |
| **Gemini 모델** | `gemini-2.0-flash-exp` | `gemini-2.0-flash-exp` |
| **배경 제거** | RapidAPI 우선 | RapidAPI 우선 |
| **API 키 하드코딩** | ⚠️ 있음 (line 759) | 불명 |
| **CORS 설정** | 전면 개방 | 전면 개방 (추정) |
| **에러 처리** | 상세한 에러 메시지 | 상세한 에러 메시지 |
| **타이밍 정보** | ✅ 있음 | ✅ 있음 |
| **Supabase 연동** | ✅ 있음 | ✅ 있음 |

**결론:** 두 파일은 거의 동일한 기능을 제공하는 것으로 보입니다. 통합 권장.

---

## 🎯 종합 평가

### ✅ 장점

1. **체계적인 6단계 파이프라인** - 명확한 작업 흐름
2. **다단계 폴백 메커니즘** - 배경 제거 실패 시 여러 방법 시도
3. **상세한 타이밍 정보** - 성능 분석 가능
4. **풍부한 로깅** - 디버깅 용이
5. **Pydantic 모델** - 타입 안전성 보장
6. **Gemini 최신 모델 사용** - `gemini-2.0-flash-exp`

### ⚠️ 개선 필요 사항

1. **보안**
   - API 키 하드코딩 제거
   - CORS 정책 강화
   - 환경변수 검증 강화

2. **성능**
   - 비동기 처리 도입
   - 캐싱 메커니즘 추가
   - 연결 풀링

3. **코드 품질**
   - 중복 코드 제거 (fastapi_image_describe.py와 통합)
   - 단위 테스트 추가
   - 타입 힌팅 강화

4. **에러 처리**
   - 더 세밀한 예외 클래스
   - 재시도 정책 개선
   - 사용자 친화적 에러 메시지

---

## 📚 사용 예시

### cURL 예시

#### 1. 이미지 설명

```bash
curl -X POST "http://localhost:8000/describe" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/face.jpg",
    "character_id": "char_001",
    "job_id": "job_12345"
  }'
```

#### 2. 캐리커쳐 생성

```bash
curl -X POST "http://localhost:8000/cartoonize" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/face.jpg",
    "character_id": "char_001",
    "custom_prompt": "해변에 앉아있는 모습",
    "job_id": "job_67890"
  }'
```

#### 3. 헬스 체크

```bash
curl -X GET "http://localhost:8000/health"
```

---

## 🗂️ 파일 위치 참조

- **메인 파일:** `d:\000.FrontEnd\102.image_upload_and_swap\main.py`
- **환경변수:** `d:\000.FrontEnd\102.image_upload_and_swap\.env`
- **Requirements:** `d:\000.FrontEnd\102.image_upload_and_swap\requirements.txt`

---

**분석 완료일:** 2025-12-01
**분석 대상:** main.py (1,324줄)
**주요 기술 스택:** FastAPI, Gemini API, Replicate, Supabase, NumPy, PIL
