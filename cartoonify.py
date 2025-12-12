import replicate
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid
# .env 파일 로드
load_dotenv()

# 환경변수 가져오기
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')

input = {
    "prompt": """
1. Do not modify hat, clothes, shoes, weapons, accessories, or any existing items. 
2. Show the full body and both hands completely visible. 
3. Do not change the character's proportions.
4. make him raise hand
    """,
    "input_image": "https://fenienmnafvphqdwlswr.supabase.co/storage/v1/object/public/kiosk/test2.png",
    "output_format": "jpg"
}

output = replicate.run(
    "black-forest-labs/flux-kontext-pro",
    input=input
)

# To access the file URL:
# print(output.url())
#=> "https://replicate.delivery/.../output.jpg"



timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
unique_id = str(uuid.uuid4())[:10]
filename = f"output_{timestamp}_{unique_id}.jpg"

# 파일 저장
with open(filename, "wb") as file:
    file.write(output.read())
print(f"{filename}이 성공적으로 저장되었습니다.")