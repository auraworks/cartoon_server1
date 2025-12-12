"""
모든 얼굴 묘사 방법을 테스트하는 통합 스크립트

사용 가능한 방법들:
1. OpenAI GPT-4o (기존 버전)
2. OpenAI GPT-4o (개선된 상세 버전)
3. OpenAI GPT-4o (예술적 버전)
4. Anthropic Claude Vision (상세 버전)
5. Anthropic Claude Vision (예술적 버전)
6. HuggingFace BLIP/GIT 모델들
"""

import asyncio
from describe import describe_image_from_url as describe_original
from describe_gemini import describe_face_detailed_v2, describe_face_artistic_v2
from describe_claude import describe_face_with_claude, describe_face_claude_artistic
from describe_huggingface import describe_face_with_huggingface

async def test_all_methods(image_url: str):
    """모든 방법으로 얼굴을 묘사하고 결과를 비교합니다."""
    
    print("=" * 80)
    print("얼굴 묘사 비교 테스트")
    print("=" * 80)
    print(f"테스트 이미지: {image_url}")
    print("=" * 80)
    
    # 1. 기존 OpenAI 방법
    print("\n🔹 1. 기존 OpenAI 방법 (간단)")
    print("-" * 50)
    try:
        result1 = describe_original(image_url)
        print(result1 if result1 else "실패")
    except Exception as e:
        print(f"오류: {e}")
    
    # 2. OpenAI 상세 버전
    print("\n🔹 2. OpenAI 상세 분석")
    print("-" * 50)
    try:
        result2 = describe_face_detailed_v2(image_url=image_url)
        print(result2 if result2 else "실패")
    except Exception as e:
        print(f"오류: {e}")
    
    # 3. OpenAI 예술적 버전
    print("\n🔹 3. OpenAI 예술적 묘사")
    print("-" * 50)
    try:
        result3 = describe_face_artistic_v2(image_url=image_url)
        print(result3 if result3 else "실패")
    except Exception as e:
        print(f"오류: {e}")
    
    # 4. Claude 상세 버전
    print("\n🔹 4. Claude 상세 분석")
    print("-" * 50)
    try:
        result4 = describe_face_with_claude(image_url=image_url)
        print(result4 if result4 else "실패")
    except Exception as e:
        print(f"오류: {e}")
    
    # 5. Claude 예술적 버전
    print("\n🔹 5. Claude 예술적 묘사")
    print("-" * 50)
    try:
        result5 = describe_face_claude_artistic(image_url=image_url)
        print(result5 if result5 else "실패")
    except Exception as e:
        print(f"오류: {e}")
    
    # 6. HuggingFace 모델들
    print("\n🔹 6. HuggingFace 모델들")
    print("-" * 50)
    try:
        hf_results = describe_face_with_huggingface(image_url=image_url)
        if hf_results:
            for model_name, description in hf_results.items():
                print(f"\n📍 {model_name}:")
                print(description)
        else:
            print("실패")
    except Exception as e:
        print(f"오류: {e}")
    
    print("\n" + "=" * 80)
    print("테스트 완료")
    print("=" * 80)

def compare_methods_simple(image_url: str):
    """간단한 비교 (동기식)"""
    
    print("🚀 빠른 비교 테스트")
    print("=" * 50)
    
    methods = [
        ("기존 방법", lambda: describe_original(image_url)),
        ("상세 분석", lambda: describe_face_detailed_v2(image_url=image_url, max_tokens=200)),
        ("예술적 묘사", lambda: describe_face_artistic_v2(image_url=image_url, max_tokens=200)),
    ]
    
    for name, func in methods:
        print(f"\n📍 {name}:")
        print("-" * 30)
        try:
            result = func()
            print(result[:200] + "..." if result and len(result) > 200 else result)
        except Exception as e:
            print(f"오류: {e}")

if __name__ == "__main__":
    # 테스트할 이미지 URL
    test_url = "https://fenienmnafvphqdwlswr.supabase.co/storage/v1/object/public/pictures/photo_74b1a06c-4e1b-4196-939d-672675a628bc_2025-08-07T13-49-55-521Z.jpg"
    
    print("어떤 테스트를 실행하시겠습니까?")
    print("1. 모든 방법 테스트 (시간 오래 걸림)")
    print("2. 빠른 비교 테스트 (OpenAI만)")
    
    choice = input("선택 (1 또는 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_all_methods(test_url))
    elif choice == "2":
        compare_methods_simple(test_url)
    else:
        print("기본값으로 빠른 테스트를 실행합니다.")
        compare_methods_simple(test_url)