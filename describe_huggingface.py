import os
import requests
from PIL import Image
from io import BytesIO
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, GitProcessor, GitForCausalLM
from typing import Optional
import base64

class HuggingFaceImageDescriber:
    def __init__(self):
        """HuggingFace 모델들을 초기화합니다."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # BLIP 모델 (이미지 캡셔닝)
        self.blip_processor = None
        self.blip_model = None
        
        # GIT 모델 (더 상세한 캡셔닝)
        self.git_processor = None
        self.git_model = None
    
    def load_blip_model(self):
        """BLIP 모델을 로드합니다."""
        if self.blip_processor is None:
            print("BLIP 모델을 로드 중...")
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
            self.blip_model.to(self.device)
            print("BLIP 모델 로드 완료")
    
    def load_git_model(self):
        """GIT 모델을 로드합니다."""
        if self.git_processor is None:
            print("GIT 모델을 로드 중...")
            self.git_processor = GitProcessor.from_pretrained("microsoft/git-large-coco")
            self.git_model = GitForCausalLM.from_pretrained("microsoft/git-large-coco")
            self.git_model.to(self.device)
            print("GIT 모델 로드 완료")
    
    def load_image_from_url(self, image_url: str) -> Optional[Image.Image]:
        """URL에서 이미지를 로드합니다."""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert('RGB')
            return image
        except Exception as e:
            print(f"이미지 로드 중 오류 발생: {str(e)}")
            return None
    
    def load_image_from_base64(self, base64_image: str) -> Optional[Image.Image]:
        """Base64에서 이미지를 로드합니다."""
        try:
            if base64_image.startswith('data:image'):
                base64_image = base64_image.split(',')[1]
            
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data)).convert('RGB')
            return image
        except Exception as e:
            print(f"Base64 이미지 로드 중 오류 발생: {str(e)}")
            return None
    
    def describe_with_blip(self, image_url: str = None, base64_image: str = None, 
                          custom_prompt: str = None) -> Optional[str]:
        """
        BLIP 모델을 사용한 이미지 묘사
        
        Args:
            image_url (str): 이미지 URL
            base64_image (str): Base64 이미지
            custom_prompt (str): 커스텀 프롬프트
        
        Returns:
            str: 이미지 묘사
        """
        try:
            self.load_blip_model()
            
            # 이미지 로드
            if image_url:
                image = self.load_image_from_url(image_url)
            elif base64_image:
                image = self.load_image_from_base64(base64_image)
            else:
                return None
            
            if image is None:
                return None
            
            # 기본 캡셔닝
            if custom_prompt is None:
                inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
                out = self.blip_model.generate(**inputs, max_length=100, num_beams=5)
                caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            else:
                # 조건부 캡셔닝 (프롬프트 사용)
                inputs = self.blip_processor(image, custom_prompt, return_tensors="pt").to(self.device)
                out = self.blip_model.generate(**inputs, max_length=100, num_beams=5)
                caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
                # 프롬프트 부분 제거
                if custom_prompt.lower() in caption.lower():
                    caption = caption.replace(custom_prompt, "").strip()
            
            return caption
            
        except Exception as e:
            print(f"BLIP 묘사 중 오류 발생: {str(e)}")
            return None
    
    def describe_with_git(self, image_url: str = None, base64_image: str = None) -> Optional[str]:
        """
        GIT 모델을 사용한 이미지 묘사
        
        Args:
            image_url (str): 이미지 URL
            base64_image (str): Base64 이미지
        
        Returns:
            str: 이미지 묘사
        """
        try:
            self.load_git_model()
            
            # 이미지 로드
            if image_url:
                image = self.load_image_from_url(image_url)
            elif base64_image:
                image = self.load_image_from_base64(base64_image)
            else:
                return None
            
            if image is None:
                return None
            
            # GIT 모델로 캡셔닝
            pixel_values = self.git_processor(images=image, return_tensors="pt").pixel_values.to(self.device)
            generated_ids = self.git_model.generate(pixel_values=pixel_values, max_length=100)
            generated_caption = self.git_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return generated_caption.strip()
            
        except Exception as e:
            print(f"GIT 묘사 중 오류 발생: {str(e)}")
            return None
    
    def describe_face_multiple_models(self, image_url: str = None, base64_image: str = None) -> Optional[dict]:
        """
        여러 모델을 사용한 종합적인 얼굴 묘사
        
        Args:
            image_url (str): 이미지 URL
            base64_image (str): Base64 이미지
        
        Returns:
            dict: 각 모델의 묘사 결과
        """
        results = {}
        
        # BLIP 기본 캡셔닝
        blip_basic = self.describe_with_blip(image_url, base64_image)
        if blip_basic:
            results["blip_basic"] = blip_basic
        
        # BLIP 얼굴 특화 프롬프트
        face_prompts = [
            "describe the person's facial features",
            "what does this person look like",
            "describe the person's appearance",
        ]
        
        for i, prompt in enumerate(face_prompts):
            description = self.describe_with_blip(image_url, base64_image, prompt)
            if description:
                results[f"blip_face_{i+1}"] = description
        
        # GIT 모델
        git_description = self.describe_with_git(image_url, base64_image)
        if git_description:
            results["git_model"] = git_description
        
        return results if results else None

# 글로벌 인스턴스
describer = HuggingFaceImageDescriber()

def describe_face_with_huggingface(image_url: str = None, base64_image: str = None) -> Optional[dict]:
    """
    HuggingFace 모델들을 사용한 얼굴 묘사
    
    Args:
        image_url (str): 이미지 URL
        base64_image (str): Base64 이미지
    
    Returns:
        dict: 각 모델의 묘사 결과
    """
    return describer.describe_face_multiple_models(image_url, base64_image)

# 테스트용 함수
if __name__ == "__main__":
    # 테스트용 이미지 URL (예시)
    test_url = "https://fenienmnafvphqdwlswr.supabase.co/storage/v1/object/public/pictures/photo_74b1a06c-4e1b-4196-939d-672675a628bc_2025-08-07T13-49-55-521Z.jpg"
    
    print("=== HuggingFace 모델들을 사용한 묘사 ===")
    descriptions = describe_face_with_huggingface(image_url=test_url)
    
    if descriptions:
        for model_name, description in descriptions.items():
            print(f"\n{model_name}:")
            print(description)
    else:
        print("묘사 실패")