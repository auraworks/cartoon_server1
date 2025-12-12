# 얼굴 묘사 기능 개선 가이드

기존의 `describe.py`가 만족스럽지 않다면, 다음과 같은 개선된 옵션들을 사용해보세요.

## 🎯 사용 가능한 옵션들

### 1. `describe_v2.py` - OpenAI 개선 버전
- **더 상세한 묘사**: 10가지 관점에서 분석
- **예술적 묘사**: 감성적이고 문학적인 표현
- **더 많은 토큰**: 기본 400 토큰 (기존 150 → 400)

```python
from describe_v2 import describe_face_detailed_v2, describe_face_artistic_v2

# 상세한 분석
detailed = describe_face_detailed_v2(image_url="your_url")

# 예술적 묘사
artistic = describe_face_artistic_v2(image_url="your_url")
```

### 2. `describe_claude.py` - Anthropic Claude 사용
- **Claude의 뛰어난 시각 인식**: 더 정확하고 섬세한 묘사
- **자연스러운 한국어**: 더 자연스러운 표현 가능

```python
from describe_claude import describe_face_with_claude

description = describe_face_with_claude(image_url="your_url")
```

### 3. `describe_huggingface.py` - 오픈소스 모델들
- **BLIP 모델**: Salesforce의 이미지 캡셔닝 모델
- **GIT 모델**: Microsoft의 고성능 이미지 설명 모델
- **무료**: API 비용 없음 (처음 다운로드만 시간 소요)

```python
from describe_huggingface import describe_face_with_huggingface

descriptions = describe_face_with_huggingface(image_url="your_url")
```

## 🚀 빠른 시작

### 옵션 1: OpenAI 개선 버전만 사용 (추천)
```bash
# 기존 의존성으로 바로 사용 가능
python describe_v2.py
```

### 옵션 2: Claude도 사용
```bash
pip install anthropic
python describe_claude.py
```

### 옵션 3: 모든 기능 사용
```bash
pip install -r requirements_enhanced.txt
python describe_test_all.py
```

## 🔧 환경 변수 설정

`.env` 파일에 다음을 추가하세요:

```env
# 기존
OPENAI_ACCESS_KEY=your_openai_key

# Claude 사용시 추가
ANTHROPIC_API_KEY=your_anthropic_key
```

## 📊 성능 비교

| 방법 | 품질 | 속도 | 비용 | 특징 |
|------|------|------|------|------|
| 기존 OpenAI | ⭐⭐⭐ | 빠름 | 낮음 | 간단한 2가지 특징 |
| OpenAI 개선 | ⭐⭐⭐⭐ | 보통 | 중간 | 10가지 상세 분석 |
| Claude | ⭐⭐⭐⭐⭐ | 보통 | 중간 | 가장 자연스럽고 정확 |
| HuggingFace | ⭐⭐⭐ | 느림* | 무료 | 오픈소스, 처음만 느림 |

*첫 실행시 모델 다운로드로 시간 소요

## 🎨 예시 출력 비교

### 기존 방법
```
1. Brown eyes with dark eyebrows
2. Short black hair with a friendly smile
```

### 개선된 상세 분석
```
1. Eyes: Deep brown eyes with a warm, inviting gaze, framed by naturally arched eyebrows...
2. Facial Structure: Oval face shape with defined cheekbones and a gentle jawline...
3. Expression: A genuine, warm smile that reaches the eyes, conveying friendliness...
[계속...]
```

### 예술적 묘사
```
Their eyes hold the depth of autumn leaves, speaking of wisdom gained through gentle experiences. 
The curve of their smile suggests someone who finds joy in simple moments, while the way light 
catches their features reveals a character both thoughtful and approachable...
```

## 💡 사용 팁

1. **빠른 테스트**: `describe_v2.py`의 상세 분석부터 시도
2. **최고 품질**: Claude 버전 사용 (API 키 필요)
3. **비용 절약**: HuggingFace 버전 (처음만 느림)
4. **비교 테스트**: `describe_test_all.py` 실행

## 🔍 어떤 걸 선택할까?

- **지금 당장 개선하고 싶다면**: `describe_v2.py` 사용
- **최고의 품질을 원한다면**: `describe_claude.py` 사용  
- **비용이 부담된다면**: `describe_huggingface.py` 사용
- **모든 걸 비교해보고 싶다면**: `describe_test_all.py` 실행