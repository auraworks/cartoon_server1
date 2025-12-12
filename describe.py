import os
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import requests
from typing import Optional
from PIL import Image
import io

# .env 파일에서 환경변수 로드
load_dotenv()

def get_gemini_client():
    """Gemini 클라이언트를 설정합니다."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def load_image_from_url(image_url: str) -> Optional[Image.Image]:
    """URL에서 이미지를 다운로드하여 PIL Image로 변환합니다."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        print(f"이미지 로드 중 오류 발생: {str(e)}")
        return None

def load_image_from_base64(base64_string: str) -> Optional[Image.Image]:
    """Base64 문자열을 PIL Image로 변환합니다."""
    try:
        # data:image/jpeg;base64, 접두사 제거
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        print(f"Base64 이미지 변환 중 오류 발생: {str(e)}")
        return None

def describe_face_detailed_v2(image_url: str = None, base64_image: str = None) -> Optional[str]:
    """
    일반적인 얼굴 특징을 상세히 묘사하는 함수 (개인정보 보호 적용)
    개인 식별 불가능한 일반적 특징만 분석합니다.
    
    Args:
        image_url (str): 분석할 이미지의 URL (선택사항)
        base64_image (str): Base64로 인코딩된 이미지 데이터 (선택사항)
    
    Returns:
        str: 일반적인 얼굴 특징 묘사 (비식별 정보)
        None: 에러가 발생한 경우
    """
    try:
        model = get_gemini_client()
        
        # 이미지 로드
        image = None
        if image_url:
            image = load_image_from_url(image_url)
        elif base64_image:
            image = load_image_from_base64(base64_image)
        else:
            return None
        
        if image is None:
            return None
        
        prompt = """이 이미지에서 사람의 일반적인 얼굴 특징을 분석해주세요. 다음 요소들을 포함하여 한국어로 상세히 묘사해주세요:

1. 눈: 일반적인 모양 (둥근형/아몬드형/좁은형), 대략적인 크기, 눈썹 스타일
2. 코: 일반적인 모양 (직선형/곡선형), 대략적인 크기
3. 입: 입술 모양 (얇은/도톰한), 입 크기
4. 얼굴형: 타원형/둥근형/각진형/하트형, 턱선 구조
5. 머리카락: 색상 카테고리, 스타일 (직모/웨이브/곱슬), 대략적인 길이
6. 일반적인 표정: 밝은/중성적인/진지한 등
7. 대략적인 연령대와 성별 표현
8. 보이는 액세서리 (안경, 귀걸이 등)

개인을 식별할 수 있는 고유한 특징은 제외하고, 일반적이고 비식별적인 얼굴 특성만 묘사해주세요."""

        response = model.generate_content([prompt, image])
        
        if response.text:
            return response.text.strip()
        else:
            return None
        
    except Exception as e:
        print(f"이미지 묘사 중 오류 발생: {str(e)}")
        return None

def describe_face_artistic_v2(image_url: str = None, base64_image: str = None) -> Optional[str]:
    """
    일반적인 얼굴 특징을 예술적/감성적으로 묘사하는 함수 (개인정보 보호 적용)
    개인 식별 불가능한 미적 특징과 인상만 분석합니다.
    
    Args:
        image_url (str): 분석할 이미지의 URL (선택사항)
        base64_image (str): Base64로 인코딩된 이미지 데이터 (선택사항)
    
    Returns:
        str: 예술적 일반 얼굴 특징 묘사 (비식별 정보)
        None: 에러가 발생한 경우
    """
    try:
        model = get_gemini_client()
        
        # 이미지 로드
        image = None
        if image_url:
            image = load_image_from_url(image_url)
        elif base64_image:
            image = load_image_from_base64(base64_image)
        else:
            return None
        
        if image is None:
            return None
        
        prompt = """이 이미지의 일반적인 얼굴 특징을 예술적이고 문학적인 표현으로 묘사해주세요. 다음 요소들에 집중하여 한국어로 아름답게 표현해주세요:

- 일반적인 눈의 특성 - 모양, 표정, 전달되는 감정
- 전체적인 얼굴 구조 - 부드러운, 각진, 둥근 등
- 빛이 얼굴 특징에 어떻게 닿는지
- 표현되고 있는 일반적인 분위기나 표정
- 일반적인 얼굴 비율과 특성
- 전체적인 미적 인상

개인을 식별할 수 있는 고유한 특징보다는 예술적이고 미적인 특성에 집중하여, 우아하고 서정적인 문체로 일반적인 외모적 특징과 표정을 묘사해주세요."""

        response = model.generate_content([prompt, image])
        
        if response.text:
            return response.text.strip()
        else:
            return None
        
    except Exception as e:
        print(f"이미지 묘사 중 오류 발생: {str(e)}")
        return None

def describe_face_multiple_perspectives(image_url: str = None, base64_image: str = None) -> Optional[dict]:
    """
    여러 관점에서 일반적인 얼굴 특징을 묘사하는 함수 (개인정보 보호 적용)
    상세 분석과 예술적 묘사 모두 비식별 정보만 포함합니다.
    
    Args:
        image_url (str): 분석할 이미지의 URL (선택사항)
        base64_image (str): Base64로 인코딩된 이미지 데이터 (선택사항)
    
    Returns:
        dict: 다양한 관점의 일반 특징 묘사들 (비식별 정보)
        None: 에러가 발생한 경우
    """
    try:
        detailed = describe_face_detailed_v2(image_url, base64_image)
        artistic = describe_face_artistic_v2(image_url, base64_image)
        
        return {
            "detailed_analysis": detailed,
            "artistic_description": artistic
        }
        
    except Exception as e:
        print(f"다중 관점 묘사 중 오류 발생: {str(e)}")
        return None

def describe_face_korean_simple(image_url: str = None, base64_image: str = None) -> Optional[str]:
    """
    간단하고 자연스러운 한국어로 얼굴 특징을 묘사하는 함수
    
    Args:
        image_url (str): 분석할 이미지의 URL (선택사항)
        base64_image (str): Base64로 인코딩된 이미지 데이터 (선택사항)
    
    Returns:
        str: 간단한 한국어 얼굴 특징 묘사
        None: 에러가 발생한 경우
    """
    try:
        model = get_gemini_client()
        
        # 이미지 로드
        image = None
        if image_url:
            image = load_image_from_url(image_url)
        elif base64_image:
            image = load_image_from_base64(base64_image)
        else:
            return None
        
        if image is None:
            return None
        
        prompt = """이 사진의 사람을 간단하고 자연스러운 한국어로 묘사해주세요. 
        
친구에게 설명하듯이 편안한 말투로, 다음과 같은 일반적인 특징들을 포함해서 설명해주세요:
- 대략적인 나이와 성별
- 얼굴형과 전체적인 인상
- 머리카락 스타일과 색
- 눈, 코, 입의 특징
- 표정이나 분위기
- 착용한 액세서리나 옷

개인을 특정할 수 있는 독특한 특징은 피하고, 일반적이고 친근한 방식으로 묘사해주세요."""

        response = model.generate_content([prompt, image])
        
        if response.text:
            return response.text.strip()
        else:
            return None
        
    except Exception as e:
        print(f"이미지 묘사 중 오류 발생: {str(e)}")
        return None

# 테스트용 함수
if __name__ == "__main__":
    # 테스트용 이미지 URL (예시)
    test_url = "https://fenienmnafvphqdwlswr.supabase.co/storage/v1/object/public/pictures/photo_74b1a06c-4e1b-4196-939d-672675a628bc_2025-08-07T13-49-55-521Z.jpg"
    
    print("=== Gemini API를 사용한 얼굴 묘사 테스트 ===\n")
    
    print("1. 간단한 한국어 묘사:")
    print("-" * 50)
    simple_description = describe_face_korean_simple(image_url=test_url)
    if simple_description:
        print(simple_description)
    else:
        print("묘사 실패")
    
    print("\n2. 상세 분석:")
    print("-" * 50)
    detailed_description = describe_face_detailed_v2(image_url=test_url)
    if detailed_description:
        print(detailed_description)
    else:
        print("상세 분석 실패")
    
    print("\n3. 예술적 묘사:")
    print("-" * 50)
    artistic_description = describe_face_artistic_v2(image_url=test_url)
    if artistic_description:
        print(artistic_description)
    else:
        print("예술적 묘사 실패")
    
    print("\n4. 다중 관점 분석:")
    print("-" * 50)
    multiple_descriptions = describe_face_multiple_perspectives(image_url=test_url)
    if multiple_descriptions:
        for perspective, description in multiple_descriptions.items():
            print(f"\n{perspective.upper()}:")
            print(description or "분석 실패")
    else:
        print("다중 관점 분석 실패")