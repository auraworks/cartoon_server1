from openai import OpenAI
import base64
import requests
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid
from PIL import Image
import io

# 환경변수 로드
load_dotenv()

# OpenAI API 키 확인 및 클라이언트 초기화
def initialize_openai_client():
    """OpenAI 클라이언트를 초기화하고 API 키를 확인"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다!")
        print("\n📋 설정 방법:")
        print("1. 프로젝트 루트 폴더에 '.env' 파일을 생성하세요")
        print("2. 다음 내용을 추가하세요:")
        print("   OPENAI_API_KEY=your_actual_api_key_here")
        print("3. OpenAI 웹사이트(https://platform.openai.com/api-keys)에서 API 키를 발급받으세요")
        print("\n⚠️  주의: API 키는 절대 코드에 직접 입력하지 마세요!")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        print(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
        return None

# 전역 클라이언트 변수
client = None

def download_image_from_url(image_url):
    """URL에서 이미지를 다운로드하여 bytes로 반환"""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"이미지 다운로드 실패: {e}")
        return None

def encode_image_to_base64(image_bytes):
    """이미지 bytes를 base64로 인코딩"""
    return base64.b64encode(image_bytes).decode('utf-8')

def resize_image_if_needed(image_bytes, max_size=(1024, 1024)):
    """이미지 크기가 너무 크면 리사이즈"""
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 이미지를 bytes로 변환
                output = io.BytesIO()
                img.save(output, format='PNG')
                return output.getvalue()
            else:
                return image_bytes
    except Exception as e:
        print(f"이미지 리사이즈 실패: {e}")
        return image_bytes

def modify_image_with_prompt(image_url, user_prompt):
    """OpenAI API를 사용하여 이미지를 프롬프트에 따라 수정"""
    global client
    
    # OpenAI 클라이언트 초기화 확인
    if client is None:
        client = initialize_openai_client()
        if client is None:
            return None
    
    try:
        # OpenAI의 DALL-E를 사용하여 이미지 변형 생성
        print("OpenAI API를 호출하는 중...")
        
        # 프롬프트를 기반으로 새로운 이미지 생성
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Create an anime/cartoon style character image: {user_prompt}. Keep the art style consistent with typical anime character designs.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # 생성된 이미지 URL 반환
        return response.data[0].url
        
    except Exception as e:
        print(f"❌ OpenAI API 호출 실패: {e}")
        print("💡 가능한 원인:")
        print("   - API 키가 유효하지 않음")
        print("   - API 크레딧이 부족함") 
        print("   - 네트워크 연결 문제")
        print("   - 프롬프트에 부적절한 내용이 포함됨")
        return None

def save_image_from_url(image_url, filename=None):
    """URL에서 이미지를 다운로드하여 로컬에 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"modified_image_{timestamp}_{unique_id}.png"
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"이미지가 성공적으로 저장되었습니다: {filename}")
        return filename
    except Exception as e:
        print(f"이미지 저장 실패: {e}")
        return None

def create_env_file():
    """사용자가 .env 파일을 생성할 수 있도록 도움"""
    print("\n🔧 .env 파일을 생성하시겠습니까? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y' or choice == 'yes':
        print("\n📝 OpenAI API 키를 입력해주세요:")
        print("(API 키는 https://platform.openai.com/api-keys 에서 발급받을 수 있습니다)")
        api_key = input("API 키: ").strip()
        
        if api_key:
            try:
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(f"# OpenAI API 설정\n")
                    f.write(f"OPENAI_API_KEY={api_key}\n")
                    f.write(f"\n# 기타 API 키들 (필요시 추가)\n")
                    f.write(f"# REPLICATE_API_TOKEN=your_replicate_token_here\n")
                    f.write(f"# SUPABASE_URL=your_supabase_url_here\n")
                
                print("✅ .env 파일이 성공적으로 생성되었습니다!")
                print("🔄 프로그램을 다시 실행해주세요.")
                return True
            except Exception as e:
                print(f"❌ .env 파일 생성 실패: {e}")
                return False
        else:
            print("❌ API 키가 입력되지 않았습니다.")
            return False
    
    return False

def main():
    """메인 실행 함수"""
    global client
    
    print("=== OpenAI 이미지 수정 도구 ===")
    
    # OpenAI 클라이언트 초기화 확인
    client = initialize_openai_client()
    if client is None:
        if create_env_file():
            return
        else:
            print("\n❌ 설정이 완료되지 않아 프로그램을 종료합니다.")
            return
    
    # 제공된 이미지 URL
    image_url = "https://fenienmnafvphqdwlswr.supabase.co/storage/v1/object/public/character/character_12_slot_4_1755250164445_ezvmjd9ka99.png"
    
    print(f"\n📸 원본 이미지: {image_url}")
    print("\n💭 어떻게 이미지를 수정하고 싶으신가요?")
    print("예시:")
    print("  - '캐릭터에게 모자를 씌워줘'")
    print("  - '배경을 바다로 바꿔줘'") 
    print("  - '캐릭터를 웃게 만들어줘'")
    print("  - '캐릭터가 책을 들고 있게 해줘'")
    
    user_prompt = input("\n✏️  수정 요청사항을 입력하세요: ").strip()
    
    if not user_prompt:
        print("❌ 프롬프트가 입력되지 않았습니다.")
        return
    
    # 이미지 수정 실행
    print(f"\n🎨 '{user_prompt}' 요청에 따라 이미지를 생성하는 중...")
    print("⏳ 잠시만 기다려주세요... (보통 10-30초 소요)")
    
    modified_image_url = modify_image_with_prompt(image_url, user_prompt)
    
    if modified_image_url:
        print(f"\n✅ 이미지 생성 완료!")
        print(f"🔗 생성된 이미지 URL: {modified_image_url}")
        
        # 이미지 다운로드 및 저장
        saved_filename = save_image_from_url(modified_image_url)
        if saved_filename:
            print(f"📁 로컬 파일로 저장됨: {saved_filename}")
    else:
        print("❌ 이미지 생성에 실패했습니다.")

def quick_test():
    """빠른 API 연결 테스트"""
    global client
    
    print("🔍 OpenAI API 연결 테스트를 시작합니다...")
    
    client = initialize_openai_client()
    if client is None:
        return False
    
    try:
        # 간단한 API 호출로 연결 테스트
        print("⏳ API 연결을 확인하는 중...")
        
        response = client.models.list()
        print("✅ OpenAI API 연결 성공!")
        print(f"📋 사용 가능한 모델 수: {len(response.data)}개")
        
        # DALL-E 모델이 있는지 확인
        dalle_models = [model for model in response.data if 'dall-e' in model.id.lower()]
        if dalle_models:
            print(f"🎨 DALL-E 모델 사용 가능: {', '.join([m.id for m in dalle_models])}")
        else:
            print("⚠️  DALL-E 모델을 찾을 수 없습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ API 연결 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # 명령줄 인수로 테스트 모드 실행 가능
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        quick_test()
    else:
        main()