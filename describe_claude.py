import os
import anthropic
from dotenv import load_dotenv
import base64
import requests
from typing import Optional

# .env 파일에서 환경변수 로드
load_dotenv()

def get_claude_client():
    """Anthropic Claude 클라이언트를 생성합니다."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    
    return anthropic.Anthropic(api_key=api_key)

def download_image_as_base64(image_url: str) -> Optional[str]:
    """이미지 URL에서 이미지를 다운로드하고 base64로 변환합니다."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = response.content
        base64_image = base64.b64encode(image_data).decode('utf-8')
        return base64_image
    except Exception as e:
        print(f"이미지 다운로드 중 오류 발생: {str(e)}")
        return None

def describe_face_with_claude(image_url: str = None, base64_image: str = None, max_tokens: int = 400) -> Optional[str]:
    """
    Anthropic Claude Vision을 사용한 얼굴 묘사
    
    Args:
        image_url (str): 분석할 이미지의 URL (선택사항)
        base64_image (str): Base64로 인코딩된 이미지 데이터 (선택사항)
        max_tokens (int): 응답의 최대 토큰 수 (기본값: 400)
    
    Returns:
        str: Claude의 얼굴 묘사
        None: 에러가 발생한 경우
    """
    try:
        client = get_claude_client()
        
        # 이미지 데이터 준비
        if image_url:
            image_data = download_image_as_base64(image_url)
            if not image_data:
                return None
        elif base64_image:
            # data:image 접두사 제거
            if base64_image.startswith('data:image'):
                image_data = base64_image.split(',')[1]
            else:
                image_data = base64_image
        else:
            return None
        
        # 이미지 타입 감지 (기본값: jpeg)
        media_type = "image/jpeg"
        if image_url and ('.png' in image_url.lower()):
            media_type = "image/png"
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Please provide a detailed description of this person's facial features. Include:

1. **Eyes**: Color, shape, expression, eyebrows, eyelashes
2. **Facial Structure**: Face shape, jawline, cheekbones, forehead
3. **Nose**: Shape, size, bridge characteristics
4. **Mouth**: Lip shape, smile, overall expression
5. **Hair**: Color, style, length, texture if visible
6. **Skin**: Tone, texture, any distinctive features
7. **Overall Expression**: Mood, personality that comes through
8. **Age and Gender Impression**: Approximate age range, gender presentation
9. **Distinctive Features**: Anything that makes this person unique or memorable
10. **Accessories**: Glasses, jewelry, makeup if visible

Please be thorough, specific, and respectful in your description. Focus on features that would help someone visualize this person clearly."""
                        }
                    ],
                }
            ],
        )
        
        return message.content[0].text.strip()
        
    except Exception as e:
        print(f"Claude를 이용한 이미지 묘사 중 오류 발생: {str(e)}")
        return None

def describe_face_claude_artistic(image_url: str = None, base64_image: str = None, max_tokens: int = 350) -> Optional[str]:
    """
    Claude를 사용한 예술적/문학적 얼굴 묘사
    
    Args:
        image_url (str): 분석할 이미지의 URL (선택사항)
        base64_image (str): Base64로 인코딩된 이미지 데이터 (선택사항)
        max_tokens (int): 응답의 최대 토큰 수 (기본값: 350)
    
    Returns:
        str: Claude의 예술적 얼굴 묘사
        None: 에러가 발생한 경우
    """
    try:
        client = get_claude_client()
        
        # 이미지 데이터 준비
        if image_url:
            image_data = download_image_as_base64(image_url)
            if not image_data:
                return None
        elif base64_image:
            if base64_image.startswith('data:image'):
                image_data = base64_image.split(',')[1]
            else:
                image_data = base64_image
        else:
            return None
        
        media_type = "image/jpeg"
        if image_url and ('.png' in image_url.lower()):
            media_type = "image/png"
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Write a poetic, artistic description of this person's face as if you were a novelist describing a character. Focus on:

- The story told by their eyes - what depth, wisdom, or emotion do you see?
- The character revealed by their facial structure and features
- How light and shadow play across their face
- The personality and spirit that seems to emanate from their expression
- Distinctive qualities that would make them memorable in a story
- The overall aura or presence they project

Write in beautiful, descriptive language that captures both the physical reality and the essence of the person. Be respectful and focus on the human beauty and uniqueness."""
                        }
                    ],
                }
            ],
        )
        
        return message.content[0].text.strip()
        
    except Exception as e:
        print(f"Claude 예술적 묘사 중 오류 발생: {str(e)}")
        return None

# 테스트용 함수
if __name__ == "__main__":
    # 테스트용 이미지 URL (예시)
    test_url = "https://fenienmnafvphqdwlswr.supabase.co/storage/v1/object/public/pictures/photo_74b1a06c-4e1b-4196-939d-672675a628bc_2025-08-07T13-49-55-521Z.jpg"
    
    print("=== Claude 상세 분석 ===")
    claude_description = describe_face_with_claude(image_url=test_url)
    if claude_description:
        print(claude_description)
    
    print("\n=== Claude 예술적 묘사 ===")
    claude_artistic = describe_face_claude_artistic(image_url=test_url)
    if claude_artistic:
        print(claude_artistic)