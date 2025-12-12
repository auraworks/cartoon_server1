from rembg import remove
from PIL import Image
import os

def remove_background(input_path: str) -> str:
    """
    이미지의 배경을 제거하고 '_post'가 붙은 파일명으로 저장합니다.
    
    Args:
        input_path: 입력 이미지 파일 경로
        
    Returns:
        str: 성공 시 결과 파일명, 실패 시 오류 메시지
    """
    try:
        print(f"[BG_REMOVER] 배경 제거 시작: {input_path}")
        
        # 파일 존재 확인
        if not os.path.exists(input_path):
            error_msg = f"오류: 파일을 찾을 수 없습니다 - {input_path}"
            print(f"[BG_REMOVER] {error_msg}")
            return error_msg
        
        # 이미지 열기
        input_image = Image.open(input_path)
        print(f"[BG_REMOVER] 이미지 로드 완료: {input_image.size}")
        
        # 배경 제거
        output_image = remove(input_image)
        print(f"[BG_REMOVER] 배경 제거 완료")
        
        # 출력 파일명 생성 (확장자 앞에 _post 추가)
        base_name = os.path.splitext(input_path)[0]
        extension = os.path.splitext(input_path)[1]
        output_path = f"{base_name}_post{extension}"
        
        # 결과 저장
        output_image.save(output_path)
        print(f"[BG_REMOVER] 결과 저장 완료: {output_path}")
        
        # 파일명만 반환 (경로 제외)
        result_filename = os.path.basename(output_path)
        print(f"[BG_REMOVER] 배경 제거 성공: {result_filename}")
        
        return result_filename
        
    except Exception as e:
        error_msg = f"배경 제거 중 오류 발생: {str(e)}"
        print(f"[BG_REMOVER] {error_msg}")
        return error_msg
