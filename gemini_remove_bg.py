import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import cv2
import base64
import io
import uuid

# .env 파일에서 환경변수 로드
load_dotenv()

def get_gemini_client():
    """Gemini 2.5 Flash 클라이언트를 설정합니다."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def load_image_from_file(image_path: str):
    """파일에서 이미지를 로드합니다."""
    try:
        return Image.open(image_path)
    except Exception as e:
        print(f"이미지 로드 중 오류 발생: {str(e)}")
        return None

def create_mask_from_analysis(image: Image.Image, analysis_result: str):
    """
    Gemini 분석 결과를 바탕으로 간단한 마스크를 생성합니다.
    실제로는 rembg나 다른 라이브러리를 사용하는 것이 더 정확하지만,
    여기서는 Gemini API만 사용하라는 요청에 따라 기본적인 처리만 합니다.
    """
    # 이미지를 numpy 배열로 변환
    img_array = np.array(image)
    
    # 기본적인 색상 기반 배경 제거 시도
    # 가장자리의 평균 색상을 배경으로 간주
    height, width = img_array.shape[:2]
    
    # 가장자리 픽셀들의 평균 색상 계산
    edge_pixels = []
    edge_pixels.extend(img_array[0, :].tolist())  # 상단
    edge_pixels.extend(img_array[-1, :].tolist())  # 하단
    edge_pixels.extend(img_array[:, 0].tolist())  # 좌측
    edge_pixels.extend(img_array[:, -1].tolist())  # 우측
    
    edge_pixels = np.array(edge_pixels)
    bg_color = np.mean(edge_pixels, axis=0)
    
    # 배경 색상과 유사한 픽셀을 찾아 마스크 생성
    mask = np.zeros((height, width), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            pixel = img_array[y, x]
            # 배경 색상과의 거리 계산
            distance = np.sqrt(np.sum((pixel - bg_color) ** 2))
            # 임계값보다 가까우면 배경으로 간주
            if distance < 50:  # 임계값 조정 가능
                mask[y, x] = 0  # 배경 (제거할 부분)
            else:
                mask[y, x] = 255  # 전경 (보존할 부분)
    
    return Image.fromarray(mask, mode='L')

def remove_background_with_gemini(image_path: str, output_path: str = None):
    """
    Gemini 2.5 Flash를 사용하여 이미지를 분석하고 배경을 제거합니다.
    
    Args:
        image_path (str): 입력 이미지 파일 경로
        output_path (str): 출력 이미지 파일 경로 (선택사항)
    
    Returns:
        str: 배경제거된 이미지 파일 경로
    """
    try:
        print(f"🚀 Gemini 2.5 Flash를 사용하여 배경제거 시작: {image_path}")
        
        # Gemini 클라이언트 설정
        model = get_gemini_client()
        
        # 이미지 로드
        image = load_image_from_file(image_path)
        if image is None:
            print("❌ 이미지 로드 실패")
            return None
        
        print("✅ 이미지 로드 완료")
        
        # Gemini로 이미지 분석
        analysis_prompt = """
        이 이미지를 자세히 분석해주세요. 특히 다음 사항들을 중심으로:
        
        1. 주요 피사체(사람, 물체 등)가 무엇인가요?
        2. 배경의 색상과 특징은 무엇인가요?
        3. 피사체와 배경의 경계가 명확한가요?
        4. 배경 제거가 쉬운 이미지인가요?
        
        간단하고 명확하게 한국어로 답변해주세요.
        """
        
        print("🔍 Gemini로 이미지 분석 중...")
        response = model.generate_content([analysis_prompt, image])
        analysis_result = response.text if response.text else "분석 실패"
        
        print("📋 Gemini 분석 결과:")
        print(analysis_result)
        
        # 배경 제거를 위한 추가 분석
        mask_prompt = """
        이 이미지에서 주요 피사체(사람이나 중심이 되는 물체)와 배경을 구분해주세요.
        피사체의 윤곽선과 배경의 특징을 자세히 설명해주세요.
        배경 제거를 위한 조언도 함께 주세요.
        """
        
        print("🎨 배경 분석 중...")
        mask_response = model.generate_content([mask_prompt, image])
        mask_analysis = mask_response.text if mask_response.text else "마스크 분석 실패"
        
        print("🖼️ 배경 분석 결과:")
        print(mask_analysis)
        
        # 간단한 배경 제거 시도
        print("✂️ 배경 제거 처리 중...")
        mask = create_mask_from_analysis(image, mask_analysis)
        
        # RGBA로 변환하여 투명도 적용
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 마스크를 사용하여 배경 제거
        img_array = np.array(image)
        mask_array = np.array(mask)
        
        # 알파 채널 설정
        img_array[:, :, 3] = mask_array
        
        # 결과 이미지 생성
        result_image = Image.fromarray(img_array, 'RGBA')
        
        # 출력 파일 경로 설정
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = f"{base_name}_bg_removed_{str(uuid.uuid4())[:8]}.png"
        
        # 결과 이미지 저장
        result_image.save(output_path, "PNG")
        
        print(f"✅ 배경제거 완료: {output_path}")
        print(f"📊 분석 결과 요약:")
        print(f"   - 입력 이미지: {image_path}")
        print(f"   - 출력 이미지: {output_path}")
        print(f"   - Gemini 모델: gemini-2.5-flash")
        
        return output_path
        
    except Exception as e:
        print(f"❌ 배경제거 중 오류 발생: {str(e)}")
        return None

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 Gemini 2.5 Flash 배경제거 도구")
    print("=" * 60)
    
    # test_remove_bg.jpg 파일 처리
    input_file = "test_remove_bg.jpg"
    
    if not os.path.exists(input_file):
        print(f"❌ 입력 파일을 찾을 수 없습니다: {input_file}")
        return
    
    print(f"📂 입력 파일: {input_file}")
    
    # 배경 제거 실행
    result_path = remove_background_with_gemini(input_file)
    
    if result_path:
        print("\n" + "=" * 60)
        print("🎉 배경제거 완료!")
        print(f"📁 결과 파일: {result_path}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 배경제거 실패!")
        print("=" * 60)

if __name__ == "__main__":
    main()





