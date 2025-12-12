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

def describe_face_simple(image_url: str = None, base64_image: str = None) -> Optional[str]:
    """
    심플하고 자연스러운 한국어로 얼굴 특징을 묘사하는 함수
    
    Args:
        image_url (str): 분석할 이미지의 URL (선택사항)
        base64_image (str): Base64로 인코딩된 이미지 데이터 (선택사항)
    
    Returns:
        str: 심플한 한국어 얼굴 특징 묘사
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
        
        prompt = """Please describe the person's appearance in simple keywords. Focus only on:
1. Hair: length and style (short hair, long hair, curly hair, etc.)
2. Eyes: size and features (big eyes, small eyes, wear glasses, etc.)
3. Face: basic features (round face, oval face, etc.)
4. Facial accessories: if any (wear glasses, earrings, etc.)

Respond with simple phrases like: "short black hair, big eyes, round face, wear glasses"
Keep it very simple and use only basic descriptive phrases."""

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
    
    print("=== Gemini API를 사용한 심플한 얼굴 묘사 테스트 ===\n")
    
    simple_description = describe_face_simple(image_url=test_url)
    if simple_description:
        print(simple_description)
    else:
        print("묘사 실패")