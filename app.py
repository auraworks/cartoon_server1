from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import base64
import os
from openai import OpenAI
from pathlib import Path
import uuid
import replicate
import shutil
from supabase import create_client, Client
import asyncio
import concurrent.futures
import threading
import aiohttp
import aiofiles
from bg_remover import remove_background
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()


SUPABASE_URL='https://fenienmnafvphqdwlswr.supabase.co'
SUPABASE_ANON_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlbmllbm1uYWZ2cGhxZHdsc3dyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NTY5MTgsImV4cCI6MjA2MzMzMjkxOH0.IYSC0bwc0ZtOHY9i7IlzihDpELkdYfUXnnQXc3iK-Vw'
app = FastAPI(title="Face Swap API", version="1.0.0")

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[INIT] FastAPI 애플리케이션 초기화 시작")

# Supabase 클라이언트 초기화
try:
    print("[INIT] Supabase 클라이언트 초기화 시작")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("[INIT] Supabase 클라이언트 초기화 완료")
except Exception as e:
    print(f"[ERROR] Supabase 클라이언트 초기화 실패: {str(e)}")

# OpenAI 클라이언트 초기화
try:
    print("[INIT] OpenAI 클라이언트 초기화 시작")
    openai_api_key = os.getenv("OPENAI_ACCESS_KEY")
    if not openai_api_key:
        print("[WARNING] OPENAI_ACCESS_KEY 환경변수가 설정되지 않았습니다.")
        client = None
    else:
        client = OpenAI(api_key=openai_api_key)
        print("[INIT] OpenAI 클라이언트 초기화 완료")
except Exception as e:
    print(f"[ERROR] OpenAI 클라이언트 초기화 실패: {str(e)}")
    client = None

# Replicate 클라이언트 초기화
try:
    print("[INIT] Replicate 클라이언트 초기화 시작")
    replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))
    print("[INIT] Replicate 클라이언트 초기화 완료")
except Exception as e:
    print(f"[ERROR] Replicate 클라이언트 초기화 실패: {str(e)}")

def encode_image(file_path):
    """이미지 파일을 base64로 인코딩"""
    print(f"[ENCODE] 이미지 인코딩 시작: {file_path}")
    try:
        with open(file_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        print(f"[ENCODE] 이미지 인코딩 완료: {file_path}")
        return base64_image
    except Exception as e:
        print(f"[ERROR] 이미지 인코딩 실패: {file_path}, 에러: {str(e)}")
        return None

def create_file(file_path):
    print(f"[FILE_CREATE] OpenAI 파일 생성 시작: {file_path}")
    try:
        with open(file_path, "rb") as file_content:
            result = client.files.create(
                file=file_content,
                purpose="vision",
            )
            print(f"[FILE_CREATE] OpenAI 파일 생성 완료: {file_path}, ID: {result.id}")
            return result.id
    except Exception as e:
        print(f"[ERROR] OpenAI 파일 생성 실패: {file_path}, 에러: {str(e)}")
        return None

async def download_image_from_url_async(url: str, save_path: str):
    """URL에서 이미지를 비동기로 다운로드하여 지정된 경로에 저장"""
    print(f"[DOWNLOAD] 이미지 다운로드 시작: {url} -> {save_path}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as response:
                response.raise_for_status()
                print(f"[DOWNLOAD] 이미지 다운로드 응답 성공: {url}, 상태코드: {response.status}")
                
                async with aiofiles.open(save_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
        
        file_size = os.path.getsize(save_path)
        print(f"[DOWNLOAD] 이미지 다운로드 완료: {save_path}, 파일 크기: {file_size} bytes")
        return True
    except Exception as e:
        print(f"[ERROR] 이미지 다운로드 실패: {url}, 에러: {str(e)}")
        return False

def download_image_from_url(url: str, save_path: str):
    """URL에서 이미지를 다운로드하여 지정된 경로에 저장 (동기 버전)"""
    print(f"[DOWNLOAD] 이미지 다운로드 시작: {url} -> {save_path}")
    try:
        response = requests.get(url, timeout=300)  # 5분으로 증가
        response.raise_for_status()
        print(f"[DOWNLOAD] 이미지 다운로드 응답 성공: {url}, 상태코드: {response.status_code}")
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        file_size = os.path.getsize(save_path)
        print(f"[DOWNLOAD] 이미지 다운로드 완료: {save_path}, 파일 크기: {file_size} bytes")
        return True
    except Exception as e:
        print(f"[ERROR] 이미지 다운로드 실패: {url}, 에러: {str(e)}")
        return False

def cartoonify_image(image_url: str, output_path: str):
    """Replicate를 이용해 이미지를 캐리커쳐로 변환"""
    print(f"[CARTOON] 캐리커쳐 변환 시작: {image_url} -> {output_path}")
    try:
        input_data = {
            "input_image": image_url
        }
        
        print(f"[CARTOON] Replicate API 호출 시작")
        output = replicate_client.run(
            "flux-kontext-apps/cartoonify",
            input=input_data
        )
        print(f"[CARTOON] Replicate API 호출 완료")
        
        print(f"[CARTOON] 결과 이미지 저장 시작: {output_path}")
        with open(output_path, "wb") as file:
            file.write(output.read())
        
        file_size = os.path.getsize(output_path)
        print(f"[CARTOON] 캐리커쳐 변환 완료: {output_path}, 파일 크기: {file_size} bytes")
        return True
    except Exception as e:
        print(f"[ERROR] 캐리커쳐 변환 실패: {image_url}, 에러: {str(e)}")
        return False

def generate_face_swap_with_responses_api(base_image_path: str, face_image_path: str, output_path: str):
    """OpenAI Responses API를 이용해 얼굴 스왑 이미지 생성"""
    print(f"[FACE_SWAP] 얼굴 스왑 시작: {base_image_path} + {face_image_path} -> {output_path}")
    try:
        # base64 인코딩
        print(f"[FACE_SWAP] Base64 인코딩 시작")
        base64_base = encode_image(base_image_path)
        base64_face = encode_image(face_image_path)
        
        if not base64_base or not base64_face:
            print(f"[ERROR] Base64 인코딩 실패")
            return False
        
        print(f"[FACE_SWAP] Base64 인코딩 완료")
        
        # 파일 ID 생성
        print(f"[FACE_SWAP] OpenAI 파일 ID 생성 시작")
        file_id_base = create_file(base_image_path)
        file_id_face = create_file(face_image_path)
        
        if not file_id_base or not file_id_face:
            print(f"[ERROR] OpenAI 파일 ID 생성 실패")
            return False
        
        print(f"[FACE_SWAP] OpenAI 파일 ID 생성 완료: base={file_id_base}, face={file_id_face}")
        
        # /prompt = "Merge the face part of the second image with the face part of the first image, ensuring the result keeps the human facial shape and overall style of the first image. If a human face cannot be clearly detected in either image, leave the original face unchanged. Make the background completely transparent with no background color."
        prompt="""
        안녕 나는 지금 페이스 스왑을 할껀데 아래 조건에 맞춰서 해줘.아래 규칙에 맞게 해줘.
        1.첫번째 이미지를 기반으로해서 두번째 이미지의 얼굴을 첫번째 이미지의 얼굴 부분에다가 넣어줘. 
        2.두번째 이미지의 얼굴 부분은 첫번째 이미지의 얼굴 부분과 똑같은 얼굴 부분이 되어야해.
        3.두번째 이미지의 얼굴의 묘사한 내용이 첫번째 이미지에 잘 부합되게 해줘.
        4.배경 색은 투명한색으로 해줘
        5.얼굴색은 사람 피부색이 되게 해줘. 다른색이나 질감으로로 하면 안돼.
        
        """
        
        
        print(f"[FACE_SWAP] OpenAI Responses API 호출 시작")
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{base64_base}",
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{base64_face}",
                        },
                        {
                            "type": "input_image",
                            "file_id": file_id_base,
                        },
                        {
                            "type": "input_image",
                            "file_id": file_id_face,
                        }
                    ],
                }
            ],
            tools=[{"type": "image_generation"}],
        )
        print(f"[FACE_SWAP] OpenAI Responses API 호출 완료")
        
        # 이미지 생성 결과 추출
        print(f"[FACE_SWAP] 이미지 생성 결과 추출 시작")
        image_generation_calls = [
            output
            for output in response.output
            if output.type == "image_generation_call"
        ]
        
        image_data = [output.result for output in image_generation_calls]
        # print('image_data:', image_data)
        print(f"[FACE_SWAP] 생성된 이미지 개수: {len(image_data)}")
        
        if image_data:
            print(f"[FACE_SWAP] 이미지 디코딩 및 저장 시작: {output_path}")
            image_base64 = image_data[0]
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            
            file_size = os.path.getsize(output_path)
            print(f"[FACE_SWAP] 얼굴 스왑 완료: {output_path}, 파일 크기: {file_size} bytes")
            return True
        
        print(f"[ERROR] 생성된 이미지 데이터가 없음")
        return False
        
    except Exception as e:
        print(f"[ERROR] 얼굴 스왑 실패: {str(e)}")
        return False

def upload_image_to_supabase(image_path: str, filename: str) -> str:
    """이미지를 Supabase Storage의 images 버킷에 업로드하고 공개 URL 반환"""
    print(f"[UPLOAD] Supabase 업로드 시작: {image_path} -> {filename}")
    try:
        # 이미지 파일 읽기
        print(f"[UPLOAD] 파일 읽기 시작: {image_path}")
        with open(image_path, "rb") as file:
            file_data = file.read()
        
        file_size = len(file_data)
        print(f"[UPLOAD] 파일 읽기 완료: {file_size} bytes")
        
        # Supabase Storage에 업로드
        print(f"[UPLOAD] Supabase Storage 업로드 시작")
        result = supabase.storage.from_("images").upload(
            path=filename,
            file=file_data,
            file_options={"content-type": "image/png"}
        )
        
        print(f"[UPLOAD] Supabase 업로드 응답 타입: {type(result)}")
        print(f"[UPLOAD] Supabase 업로드 응답 내용: {result}")
        
        # 업로드 성공 확인 - try/except로 안전하게 처리
        upload_success = False
        try:
            # status_code 속성이 있는 경우
            if hasattr(result, 'status_code'):
                upload_success = result.status_code == 200
                print(f"[UPLOAD] status_code 확인: {result.status_code}")
            # count 속성이 있는 경우 (일부 버전에서 사용)
            elif hasattr(result, 'count'):
                upload_success = result.count is not None
                print(f"[UPLOAD] count 확인: {result.count}")
            # data 속성이 있는 경우
            elif hasattr(result, 'data'):
                upload_success = result.data is not None
                print(f"[UPLOAD] data 확인: {result.data}")
            # 그 외의 경우 - 예외가 발생하지 않았다면 성공으로 간주
            else:
                upload_success = True
                print(f"[UPLOAD] 예외 없음으로 성공 간주")
        except Exception as check_error:
            print(f"[UPLOAD] 업로드 결과 확인 중 에러: {str(check_error)}")
            # 예외가 발생하지 않았다면 업로드는 성공했을 가능성이 높음
            upload_success = True
        
        if upload_success:
            # 공개 URL 생성
            print(f"[UPLOAD] 공개 URL 생성 시작")
            public_url = supabase.storage.from_("images").get_public_url(filename)
            print(f"[UPLOAD] Supabase 업로드 완료: {public_url}")
            return public_url
        else:
            print(f"[ERROR] Supabase 업로드 실패")
            return None
            
    except Exception as e:
        print(f"[ERROR] Supabase 업로드 에러: {str(e)}")
        return None

def create_job_record(job_id: str):
    """Supabase image 테이블에 새로운 job 레코드 생성"""
    print(f"[DB] job 레코드 생성 시작: {job_id}")
    try:
        result = supabase.table("image").insert({
            "job_id": job_id,
            "url": None
        }).execute()
        print(f"[DB] job 레코드 생성 완료: {job_id}")
        return True
    except Exception as e:
        print(f"[ERROR] job 레코드 생성 실패: {job_id}, 에러: {str(e)}")
        return False

def update_job_result(job_id: str, image_url: str):
    """job 완료 후 결과 URL을 데이터베이스에 업데이트"""
    print(f"[DB] job 결과 업데이트 시작: {job_id} -> {image_url}")
    try:
        result = supabase.table("image").update({
            "url": image_url
        }).eq("job_id", job_id).execute()
        print(f"[DB] job 결과 업데이트 완료: {job_id}")
        return True
    except Exception as e:
        print(f"[ERROR] job 결과 업데이트 실패: {job_id}, 에러: {str(e)}")
        return False

# ThreadPoolExecutor 초기화
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def process_face_swap_with_cartoon_sync(job_id: str, base_image_url: str, face_image_url: str):
    """동기적으로 캐리커쳐 얼굴 스왑 작업을 수행 (ThreadPool에서 실행)"""
    print(f"[BACKGROUND] 캐리커쳐 얼굴 스왑 백그라운드 작업 시작: {job_id}")
    
    try:
        # 디렉토리 생성
        print(f"[BACKGROUND] 작업 디렉토리 생성 시작")
        os.makedirs("source", exist_ok=True)
        os.makedirs("result", exist_ok=True)
        print(f"[BACKGROUND] 작업 디렉토리 생성 완료")
        
        # 1. 베이스 이미지 다운로드 (source 폴더에 저장)
        base_image_path = os.path.join("source", f"base_{job_id}.png")
        print(f"[BACKGROUND] 1단계: 베이스 이미지 다운로드 시작")
        if not download_image_from_url(base_image_url, base_image_path):
            print(f"[ERROR] 베이스 이미지 다운로드 실패")
            return
        print(f"[BACKGROUND] 1단계: 베이스 이미지 다운로드 완료")
        
        # 2. 얼굴 이미지를 캐리커쳐로 변환 (result 폴더에 저장)
        cartoon_image_path = os.path.join("result", f"cartoon_{job_id}.png")
        print(f"[BACKGROUND] 2단계: 캐리커쳐 변환 시작")
        if not cartoonify_image(face_image_url, cartoon_image_path):
            print(f"[ERROR] 캐리커쳐 변환 실패")
            return
        print(f"[BACKGROUND] 2단계: 캐리커쳐 변환 완료")
        
        # 3. 얼굴 스왑 수행 (result 폴더에 저장)
        result_image_path = os.path.join("result", f"face_swapped_cartoon_{job_id}.png")
        print(f"[BACKGROUND] 3단계: 얼굴 스왑 시작")
        if not generate_face_swap_with_responses_api(base_image_path, cartoon_image_path, result_image_path):
            print(f"[ERROR] 얼굴 스왑 실패")
            return
        print(f"[BACKGROUND] 3단계: 얼굴 스왑 완료")
        
        # 4. 결과 이미지를 Supabase Storage에 업로드
        filename = f"face_swapped_cartoon_{job_id}.png"
        print(f"[BACKGROUND] 4단계: Supabase 업로드 시작")
        uploaded_url = upload_image_to_supabase(result_image_path, filename)
        
        if not uploaded_url:
            print(f"[ERROR] Supabase 업로드 실패")
            return
        print(f"[BACKGROUND] 4단계: Supabase 업로드 완료")
        
        # 5. 데이터베이스에 결과 URL 업데이트
        print(f"[BACKGROUND] 5단계: 데이터베이스 업데이트 시작")
        if not update_job_result(job_id, uploaded_url):
            print(f"[ERROR] 데이터베이스 업데이트 실패")
            return
        print(f"[BACKGROUND] 5단계: 데이터베이스 업데이트 완료")
        
        print(f"[BACKGROUND] 캐리커쳐 얼굴 스왑 백그라운드 작업 완료: {job_id}")
        
    except Exception as e:
        print(f"[ERROR] 백그라운드 작업 에러: {job_id}, {str(e)}")
    
    finally:
        # 임시 파일들 정리
        print(f"[CLEANUP] 임시 파일 정리 시작: {job_id}")
        # try:
        #     # source 폴더의 파일들 정리
        #     if 'base_image_path' in locals() and os.path.exists(base_image_path):
        #         os.remove(base_image_path)
        #     # result 폴더의 임시 파일들 정리 (업로드 완료 후)
        #     if 'cartoon_image_path' in locals() and os.path.exists(cartoon_image_path):
        #         os.remove(cartoon_image_path)
        #     if 'result_image_path' in locals() and os.path.exists(result_image_path):
        #         os.remove(result_image_path)
        #     print(f"[CLEANUP] 임시 파일 정리 완료: {job_id}")
        # except Exception as e:
        #     print(f"[CLEANUP] 임시 파일 정리 에러: {job_id}, {str(e)}")

async def process_face_swap_with_cartoon_background(job_id: str, base_image_url: str, face_image_url: str):
    """백그라운드에서 캐리커쳐 얼굴 스왑 작업을 비동기로 실행"""
    print(f"[ASYNC] 캐리커쳐 얼굴 스왑 비동기 작업 시작: {job_id}")
    
    # ThreadPoolExecutor를 사용하여 CPU 집약적 작업을 별도 스레드에서 실행
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor, 
        process_face_swap_with_cartoon_sync, 
        job_id, 
        base_image_url, 
        face_image_url
    )
    
    print(f"[ASYNC] 캐리커쳐 얼굴 스왑 비동기 작업 완료: {job_id}")

def process_face_swap_sync(job_id: str, base_image_url: str, face_image_url: str):
    """동기적으로 일반 얼굴 스왑 작업을 수행 (ThreadPool에서 실행)"""
    print(f"[BACKGROUND] 일반 얼굴 스왑 백그라운드 작업 시작: {job_id}")
    
    try:
        # 디렉토리 생성
        print(f"[BACKGROUND] 작업 디렉토리 생성 시작")
        os.makedirs("source", exist_ok=True)
        os.makedirs("result", exist_ok=True)
        print(f"[BACKGROUND] 작업 디렉토리 생성 완료")
        
        # 베이스 이미지 다운로드 (source 폴더에 저장)
        base_image_path = os.path.join("source", f"base_{job_id}.png")
        print(f"[BACKGROUND] 1단계: 베이스 이미지 다운로드 시작")
        if not download_image_from_url(base_image_url, base_image_path):
            print(f"[ERROR] 베이스 이미지 다운로드 실패")
            return
        print(f"[BACKGROUND] 1단계: 베이스 이미지 다운로드 완료")
        
        # 얼굴 이미지 다운로드 (source 폴더에 저장)
        face_image_path = os.path.join("source", f"face_{job_id}.png")
        print(f"[BACKGROUND] 2단계: 얼굴 이미지 다운로드 시작")
        if not download_image_from_url(face_image_url, face_image_path):
            print(f"[ERROR] 얼굴 이미지 다운로드 실패")
            return
        print(f"[BACKGROUND] 2단계: 얼굴 이미지 다운로드 완료")
        
        # 얼굴 스왑 수행 (result 폴더에 저장)
        result_image_path = os.path.join("result", f"face_swapped_result_{job_id}.png")
        print(f"[BACKGROUND] 3단계: 얼굴 스왑 시작")
        if not generate_face_swap_with_responses_api(base_image_path, face_image_path, result_image_path):
            print(f"[ERROR] 얼굴 스왑 실패")
            return
        print(f"[BACKGROUND] 3단계: 얼굴 스왑 완료")
        
        # 결과 이미지를 Supabase Storage에 업로드
        filename = f"face_swapped_result_{job_id}.png"
        print(f"[BACKGROUND] 4단계: Supabase 업로드 시작")
        uploaded_url = upload_image_to_supabase(result_image_path, filename)
        
        if not uploaded_url:
            print(f"[ERROR] Supabase 업로드 실패")
            return
        print(f"[BACKGROUND] 4단계: Supabase 업로드 완료")
        
        # 데이터베이스에 결과 URL 업데이트
        print(f"[BACKGROUND] 5단계: 데이터베이스 업데이트 시작")
        if not update_job_result(job_id, uploaded_url):
            print(f"[ERROR] 데이터베이스 업데이트 실패")
            return
        print(f"[BACKGROUND] 5단계: 데이터베이스 업데이트 완료")
        
        print(f"[BACKGROUND] 일반 얼굴 스왑 백그라운드 작업 완료: {job_id}")
        
    except Exception as e:
        print(f"[ERROR] 백그라운드 작업 에러: {job_id}, {str(e)}")
    
    finally:
        
        print(f"[CLEANUP] 임시 파일 정리 시작: {job_id}")
        # try:
        #     # source 폴더의 파일들 정리
        #     if 'base_image_path' in locals() and os.path.exists(base_image_path):
        #         os.remove(base_image_path)
        #     if 'face_image_path' in locals() and os.path.exists(face_image_path):
        #         os.remove(face_image_path)
        #     # result 폴더의 파일 정리
        #     if 'result_image_path' in locals() and os.path.exists(result_image_path):
        #         os.remove(result_image_path)
        #     print(f"[CLEANUP] 임시 파일 정리 완료: {job_id}")
        # except Exception as e:
        #     print(f"[CLEANUP] 임시 파일 정리 에러: {job_id}, {str(e)}")

async def process_face_swap_background(job_id: str, base_image_url: str, face_image_url: str):
    """백그라운드에서 일반 얼굴 스왑 작업을 비동기로 실행"""
    print(f"[ASYNC] 일반 얼굴 스왑 비동기 작업 시작: {job_id}")
    
    # ThreadPoolExecutor를 사용하여 CPU 집약적 작업을 별도 스레드에서 실행
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor, 
        process_face_swap_sync, 
        job_id, 
        base_image_url, 
        face_image_url
    )
    
    print(f"[ASYNC] 일반 얼굴 스왑 비동기 작업 완료: {job_id}")

def process_cartoonify_sync(job_id: str, image_url: str):
    """동기적으로 캐리커쳐 변환 작업을 수행 (ThreadPool에서 실행)"""
    print(f"[BACKGROUND] 캐리커쳐 변환 백그라운드 작업 시작: {job_id}")
    
    try:
        # 디렉토리 생성
        print(f"[BACKGROUND] 작업 디렉토리 생성 시작")
        os.makedirs("source", exist_ok=True)
        os.makedirs("result", exist_ok=True)
        print(f"[BACKGROUND] 작업 디렉토리 생성 완료")
        
        # 캐리커쳐 변환 (result 폴더에 저장)
        result_image_path = os.path.join("result", f"cartoon_only_{job_id}.png")
        print(f"[BACKGROUND] 1단계: 캐리커쳐 변환 시작")
        if not cartoonify_image(image_url, result_image_path):
            print(f"[ERROR] 캐리커쳐 변환 실패")
            return
        print(f"[BACKGROUND] 1단계: 캐리커쳐 변환 완료")
        
        # 결과 이미지를 Supabase Storage에 업로드
        filename = f"cartoon_only_{job_id}.png"
        print(f"[BACKGROUND] 2단계: Supabase 업로드 시작")
        uploaded_url = upload_image_to_supabase(result_image_path, filename)
        
        if not uploaded_url:
            print(f"[ERROR] Supabase 업로드 실패")
            return
        print(f"[BACKGROUND] 2단계: Supabase 업로드 완료")
        
        # 데이터베이스에 결과 URL 업데이트
        print(f"[BACKGROUND] 3단계: 데이터베이스 업데이트 시작")
        if not update_job_result(job_id, uploaded_url):
            print(f"[ERROR] 데이터베이스 업데이트 실패")
            return
        print(f"[BACKGROUND] 3단계: 데이터베이스 업데이트 완료")
        
        print(f"[BACKGROUND] 캐리커쳐 변환 백그라운드 작업 완료: {job_id}")
        
    except Exception as e:
        print(f"[ERROR] 백그라운드 작업 에러: {job_id}, {str(e)}")
    
    finally:
        # result 폴더의 파일 정리
        print(f"[CLEANUP] 로컬 파일 정리 시작: {job_id}")
        # try:
        #     if 'result_image_path' in locals() and os.path.exists(result_image_path):
        #         os.remove(result_image_path)
        #     print(f"[CLEANUP] 로컬 파일 정리 완료: {job_id}")
        # except Exception as e:
        #     print(f"[CLEANUP] 로컬 파일 정리 에러: {job_id}, {str(e)}")

async def process_cartoonify_background(job_id: str, image_url: str):
    """백그라운드에서 캐리커쳐 변환 작업을 비동기로 실행"""
    print(f"[ASYNC] 캐리커쳐 변환 비동기 작업 시작: {job_id}")
    
    # ThreadPoolExecutor를 사용하여 CPU 집약적 작업을 별도 스레드에서 실행
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor, 
        process_cartoonify_sync, 
        job_id, 
        image_url
    )
    
    print(f"[ASYNC] 캐리커쳐 변환 비동기 작업 완료: {job_id}")

# Pydantic 모델 정의
class FaceSwapRequest(BaseModel):
    base_image_url: str
    face_image_url: str

class CartoonifyRequest(BaseModel):
    image_url: str

@app.post("/face-swap-with-cartoon")
async def face_swap_with_cartoon(request: FaceSwapRequest):
    print(f"[API] /face-swap-with-cartoon 요청 받음")
    print(f"[REQUEST] base_image_url: {request.base_image_url}")
    print(f"[REQUEST] face_image_url: {request.face_image_url}")
    
    """
    캐리커쳐 변환 후 얼굴 스왑 API (진정한 비동기 처리)
    1. job_id 생성하여 즉시 반환
    2. 백그라운드에서 캐리커쳐 변환 및 얼굴 스왑 수행
    """
    
    job_id = str(uuid.uuid4())
    print(f"[API] job_id 생성: {job_id}")
    
    try:
        # 1. 데이터베이스에 job 레코드 생성
        print(f"[API] 데이터베이스에 job 레코드 생성 시작")
        if not create_job_record(job_id):
            print(f"[ERROR] job 레코드 생성 실패")
            raise HTTPException(status_code=500, detail="작업 생성에 실패했습니다.")
        print(f"[API] 데이터베이스에 job 레코드 생성 완료")
        
        # 2. 비동기 태스크 생성 (fire-and-forget)
        print(f"[API] 비동기 태스크 생성")
        asyncio.create_task(process_face_swap_with_cartoon_background(
            job_id, 
            request.base_image_url, 
            request.face_image_url
        ))
        
        # 3. job_id 즉시 반환
        print(f"[API] /face-swap-with-cartoon job_id 반환: {job_id}")
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "message": "캐리커쳐 얼굴 스왑 작업이 시작되었습니다. job_id로 결과를 확인하세요."
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] API 처리 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/face-swap")
async def face_swap(request: FaceSwapRequest):
    """
    기본 얼굴 스왑 API (진정한 비동기 처리)
    """
    
    job_id = str(uuid.uuid4())
    print(f"[API] /face-swap 요청 시작: job_id={job_id}")
    print(f"[API] base_image_url: {request.base_image_url}")
    print(f"[API] face_image_url: {request.face_image_url}")
    
    try:
        # 1. 데이터베이스에 job 레코드 생성
        print(f"[API] 데이터베이스에 job 레코드 생성 시작")
        if not create_job_record(job_id):
            print(f"[ERROR] job 레코드 생성 실패")
            raise HTTPException(status_code=500, detail="작업 생성에 실패했습니다.")
        print(f"[API] 데이터베이스에 job 레코드 생성 완료")
        
        # 2. 비동기 태스크 생성 (fire-and-forget)
        print(f"[API] 비동기 태스크 생성")
        asyncio.create_task(process_face_swap_background(
            job_id, 
            request.base_image_url, 
            request.face_image_url
        ))
        
        # 3. job_id 즉시 반환
        print(f"[API] /face-swap job_id 반환: {job_id}")
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "message": "얼굴 스왑 작업이 시작되었습니다. job_id로 결과를 확인하세요."
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] API 처리 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/cartoonify-only")
async def cartoonify_only(request: CartoonifyRequest):
    """
    이미지를 캐리커쳐로만 변환하는 API (진정한 비동기 처리)
    """
    
    job_id = str(uuid.uuid4())
    print(f"[API] /cartoonify-only 요청 시작: job_id={job_id}")
    print(f"[API] image_url: {request.image_url}")
    
    try:
        # 1. 데이터베이스에 job 레코드 생성
        print(f"[API] 데이터베이스에 job 레코드 생성 시작")
        if not create_job_record(job_id):
            print(f"[ERROR] job 레코드 생성 실패")
            raise HTTPException(status_code=500, detail="작업 생성에 실패했습니다.")
        print(f"[API] 데이터베이스에 job 레코드 생성 완료")
        
        # 2. 비동기 태스크 생성 (fire-and-forget)
        print(f"[API] 비동기 태스크 생성")
        asyncio.create_task(process_cartoonify_background(
            job_id, 
            request.image_url
        ))
        
        # 3. job_id 즉시 반환
        print(f"[API] /cartoonify-only job_id 반환: {job_id}")
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "message": "캐리커쳐 변환 작업이 시작되었습니다. job_id로 결과를 확인하세요."
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] API 처리 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """
    job_id로 작업 상태 및 결과 조회
    """
    print(f"[API] /job/{job_id} 상태 조회 요청")
    
    try:
        # 데이터베이스에서 job 정보 조회
        result = supabase.table("image").select("*").eq("job_id", job_id).execute()
        
        if not result.data or len(result.data) == 0:
            print(f"[ERROR] job을 찾을 수 없음: {job_id}")
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
        
        job_data = result.data[0]
        print(f"[API] job 데이터 조회 완료: {job_data}")
        
        # url이 없으면 처리 중, 있으면 완료
        if job_data["url"] is None:
            return JSONResponse(content={
                "success": True,
                "job_id": job_id,
                "status": "processing",
                "message": "작업 처리 중입니다.",
                "image_url": None
            })
        else:
            return JSONResponse(content={
                "success": True,
                "job_id": job_id,
                "status": "completed",
                "message": "작업이 완료되었습니다.",
                "image_url": job_data["url"]
            })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] job 상태 조회 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상태 조회 중 오류가 발생했습니다: {str(e)}")

@app.post("/remove-background")
async def remove_background_api(file: UploadFile = File(...)):
    """
    이미지 파일의 배경을 제거하고 '_post'가 붙은 파일명으로 저장합니다.
    """
    print(f"[API] /remove-background 요청 - 파일명: {file.filename}")
    
    try:
        # 1. 업로드된 파일 검증
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다. PNG, JPG, JPEG 파일만 업로드하세요.")
        
        # 2. 고유한 파일명 생성
        file_id = str(uuid.uuid4())[:8]
        original_name = Path(file.filename).stem
        file_extension = Path(file.filename).suffix
        temp_filename = f"{original_name}_{file_id}{file_extension}"
        temp_filepath = f"temp/{temp_filename}"
        
        # 3. temp 폴더 생성
        os.makedirs("temp", exist_ok=True)
        
        # 4. 업로드된 파일 저장
        print(f"[INFO] 임시 파일 저장: {temp_filepath}")
        async with aiofiles.open(temp_filepath, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # 5. 배경 제거 처리
        print(f"[INFO] 배경 제거 시작: {temp_filename}")
        result_filename = remove_background(temp_filepath)
        
        if result_filename.startswith("오류") or result_filename.startswith("배경 제거 중 오류"):
            raise HTTPException(status_code=500, detail=result_filename)
        
        result_filepath = f"temp/{result_filename}"
        
        # 6. 결과 파일을 Supabase에 업로드
        print(f"[INFO] Supabase 업로드 시작: {result_filename}")
        with open(result_filepath, 'rb') as f:
            file_data = f.read()
        
        upload_result = supabase.storage.from_("image").upload(result_filename, file_data)
        
        if hasattr(upload_result, 'error') and upload_result.error:
            raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {upload_result.error}")
        
        # 7. 공개 URL 생성
        public_url = supabase.storage.from_("image").get_public_url(result_filename)
        
        # 8. 데이터베이스에 저장
        job_id = str(uuid.uuid4())
        insert_data = {
            "job_id": job_id,
            "original_filename": file.filename,
            "result_filename": result_filename,
            "url": public_url.data.get('publicUrl') if hasattr(public_url, 'data') else public_url,
            "type": "background_removal"
        }
        
        db_result = supabase.table("image").insert(insert_data).execute()
        
        # 9. 임시 파일들 정리
        try:
            os.remove(temp_filepath)
            os.remove(result_filepath)
        except:
            pass
        
        print(f"[SUCCESS] 배경 제거 완료: {result_filename}")
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "original_filename": file.filename,
            "result_filename": result_filename,
            "image_url": insert_data["url"],
            "message": "배경 제거가 완료되었습니다."
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 배경 제거 API 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"배경 제거 중 오류가 발생했습니다: {str(e)}")

@app.post("/remove-background-async")
async def remove_background_async_api(file: UploadFile = File(...)):
    """
    이미지 파일의 배경을 비동기로 제거합니다. job_id를 반환하여 나중에 결과를 확인할 수 있습니다.
    """
    print(f"[API] /remove-background-async 요청 - 파일명: {file.filename}")
    
    try:
        # 1. 업로드된 파일 검증
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다. PNG, JPG, JPEG 파일만 업로드하세요.")
        
        # 2. job_id 생성 및 데이터베이스에 초기 상태 저장
        job_id = str(uuid.uuid4())
        print(f"[API] job_id 생성: {job_id}")
        
        insert_data = {
            "job_id": job_id,
            "original_filename": file.filename,
            "result_filename": None,
            "url": None,
            "type": "background_removal"
        }
        
        db_result = supabase.table("image").insert(insert_data).execute()
        print(f"[API] 데이터베이스 초기 상태 저장 완료")
        
        # 3. 업로드된 파일을 Supabase에 임시 저장
        file_content = await file.read()
        file_id = str(uuid.uuid4())[:8]
        original_name = Path(file.filename).stem
        file_extension = Path(file.filename).suffix
        temp_filename = f"temp_{original_name}_{file_id}{file_extension}"
        
        upload_result = supabase.storage.from_("image").upload(temp_filename, file_content)
        temp_url = supabase.storage.from_("image").get_public_url(temp_filename)
        
        # 4. 백그라운드 작업 시작
        asyncio.create_task(process_background_removal_background(
            job_id, 
            temp_url.data.get('publicUrl') if hasattr(temp_url, 'data') else temp_url,
            temp_filename,
            file.filename
        ))
        
        # 5. job_id 즉시 반환
        print(f"[API] /remove-background-async job_id 반환: {job_id}")
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "message": "배경 제거 작업이 시작되었습니다. job_id로 결과를 확인하세요."
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 비동기 배경 제거 API 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"배경 제거 작업 시작 중 오류가 발생했습니다: {str(e)}")

async def process_background_removal_background(job_id: str, image_url: str, temp_filename: str, original_filename: str):
    """
    배경 제거를 백그라운드에서 처리하는 함수
    """
    try:
        print(f"[BACKGROUND] 배경 제거 백그라운드 작업 시작: {job_id}")
        
        # 1. 작업 디렉토리 생성
        work_dir = f"work/{job_id}"
        os.makedirs(work_dir, exist_ok=True)
        print(f"[BACKGROUND] 작업 디렉토리 생성 완료")
        
        # 2. 이미지 다운로드
        print(f"[BACKGROUND] 이미지 다운로드 시작")
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    input_path = f"{work_dir}/input{Path(original_filename).suffix}"
                    async with aiofiles.open(input_path, 'wb') as f:
                        await f.write(image_data)
        print(f"[BACKGROUND] 이미지 다운로드 완료")
        
        # 3. 배경 제거
        print(f"[BACKGROUND] 배경 제거 시작")
        result_filename = remove_background(input_path)
        
        if result_filename.startswith("오류") or result_filename.startswith("배경 제거 중 오류"):
            raise Exception(result_filename)
        
        result_path = f"{work_dir}/{result_filename}"
        print(f"[BACKGROUND] 배경 제거 완료")
        
        # 4. 결과를 Supabase에 업로드
        print(f"[BACKGROUND] Supabase 업로드 시작")
        with open(result_path, 'rb') as f:
            result_data = f.read()
        
        final_filename = f"bg_removed_{job_id}_{result_filename}"
        upload_result = supabase.storage.from_("image").upload(final_filename, result_data)
        public_url = supabase.storage.from_("image").get_public_url(final_filename)
        print(f"[BACKGROUND] Supabase 업로드 완료")
        
        # 5. 데이터베이스 업데이트
        print(f"[BACKGROUND] 데이터베이스 업데이트 시작")
        update_data = {
            "result_filename": final_filename,
            "url": public_url.data.get('publicUrl') if hasattr(public_url, 'data') else public_url
        }
        supabase.table("image").update(update_data).eq("job_id", job_id).execute()
        print(f"[BACKGROUND] 데이터베이스 업데이트 완료")
        
        # 6. 임시 파일들 정리
        try:
            supabase.storage.from_("image").remove([temp_filename])
            shutil.rmtree(work_dir)
        except:
            pass
        
        print(f"[BACKGROUND] 배경 제거 백그라운드 작업 완료: {job_id}")
        
    except Exception as e:
        print(f"[BACKGROUND] 배경 제거 백그라운드 작업 실패: {job_id}, 오류: {str(e)}")
        # 오류 상태를 데이터베이스에 기록할 수 있음

@app.get("/")
async def root():
    print(f"[API] / 엔드포인트 호출")
    return {"message": "Face Swap API", "version": "2.0.0", "endpoints": ["/face-swap-with-cartoon", "/face-swap", "/cartoonify-only", "/remove-background", "/remove-background-async", "/job/{job_id}"]}

@app.get("/health")
async def health_check():
    print(f"[API] /health 엔드포인트 호출")
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 ThreadPoolExecutor 정리"""
    print("[SHUTDOWN] ThreadPoolExecutor 종료 시작")
    executor.shutdown(wait=True)
    print("[SHUTDOWN] ThreadPoolExecutor 종료 완료")

