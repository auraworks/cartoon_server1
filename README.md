# Face Swap API

AI를 활용한 고품질 얼굴 스왑 및 캐리커쳐 변환 API입니다. OpenAI, Replicate, Supabase를 활용하여 실시간 이미지 처리 서비스를 제공합니다.

## 🎯 주요 기능

- **🔄 얼굴 스왑**: 두 이미지 간의 자연스러운 얼굴 교체
- **🎨 캐리커쳐 얼굴 스왑**: 얼굴을 캐리커쳐로 변환 후 얼굴 교체  
- **🖼️ 캐리커쳐 변환**: 이미지를 캐리커쳐 스타일로만 변환
- **⚡ 비동기 처리**: 대용량 이미지 처리를 위한 백그라운드 작업
- **📊 작업 상태 추적**: Job ID를 통한 실시간 처리 상태 확인
- **☁️ 클라우드 스토리지**: Supabase 연동으로 안정적인 이미지 관리

## 🛠️ 기술 스택

- **Backend**: FastAPI (Python 3.11)
- **AI Services**: OpenAI GPT-4 Vision, Replicate Cartoonify
- **Database & Storage**: Supabase
- **Web Server**: Nginx (리버스 프록시)
- **Containerization**: Docker & Docker Compose
- **Deployment**: EC2 배포 지원

## 📡 API 엔드포인트

### 1. 캐리커쳐 얼굴 스왑 (동기)
```http
POST /face-swap-with-cartoon
Content-Type: application/json

{
  "base_image_url": "https://example.com/base.jpg",
  "face_image_url": "https://example.com/face.jpg"
}
```

**응답:**
```json
{
  "success": true,
  "result_url": "https://supabase.co/storage/v1/object/public/pictures/result.jpg",
  "processing_time": "45.2s"
}
```

### 2. 기본 얼굴 스왑 (비동기)
```http
POST /face-swap
Content-Type: application/json

{
  "base_image_url": "https://example.com/base.jpg",
  "face_image_url": "https://example.com/face.jpg"
}
```

**응답:**
```json
{
  "success": true,
  "job_id": "uuid-job-id",
  "message": "얼굴 스왑 작업이 시작되었습니다. job_id로 결과를 확인하세요."
}
```

### 3. 캐리커쳐 변환만
```http
POST /cartoonify-only
Content-Type: application/json

{
  "image_url": "https://example.com/image.jpg"
}
```

### 4. 작업 상태 조회
```http
GET /job/{job_id}
```

**응답 (진행중):**
```json
{
  "job_id": "uuid-job-id",
  "status": "processing",
  "message": "작업이 진행 중입니다..."
}
```

**응답 (완료):**
```json
{
  "job_id": "uuid-job-id",
  "status": "completed",
  "result_url": "https://supabase.co/storage/v1/object/public/pictures/result.jpg"
}
```

### 5. 헬스체크
```http
GET /health
```

### 6. API 정보
```http
GET /
```

## 🚀 로컬 개발 환경 설정

### 사전 요구사항
- Python 3.11+
- Docker & Docker Compose (선택사항)
- API 키들 (OpenAI, Replicate, Supabase)

### 1. 저장소 클론
```bash
git clone <repository-url>
cd 102.image_upload_and_swap
```

### 2. 가상환경 생성 및 활성화
```bash
python3 -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
필요한 API 키들을 `app.py` 파일에서 설정하거나 환경변수로 관리하세요:

```bash
# 예시 - 환경변수로 관리하는 경우
export OPENAI_API_KEY="your-openai-api-key"
export REPLICATE_API_TOKEN="your-replicate-token"
export SUPABASE_URL="your-supabase-url"
export SUPABASE_ANON_KEY="your-supabase-anon-key"
```

### 5. 애플리케이션 실행
```bash
# 직접 실행
python app.py

# 또는 Uvicorn 사용
uvicorn app:app --host 0.0.0.0 --port 8000
```

애플리케이션이 http://localhost:8000 에서 실행됩니다.

## 🐳 Docker로 실행

### Docker Compose 사용 (권장)
```bash
# 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 개별 Docker 빌드
```bash
# 이미지 빌드
docker build -t face-swap-api .

# 컨테이너 실행
docker run -p 8000:8000 face-swap-api
```

## ☁️ EC2 배포

### 자동 배포 (권장)
```bash
# 파일들을 EC2에 업로드한 후
chmod +x deploy.sh
./deploy.sh
```

### 수동 배포

#### 1. 시스템 패키지 설치
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx docker.io docker-compose
```

#### 2. Docker Compose로 배포
```bash
# 프로젝트 디렉토리에서
sudo docker-compose up -d --build
```

#### 3. Nginx 설정 (선택사항)
```bash
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔧 설정 및 최적화

### 타임아웃 설정
AI 모델 처리로 인해 **최대 2-5분**의 응답 시간이 소요될 수 있습니다.

#### FastAPI (Uvicorn) 설정
- `timeout_keep_alive=0`: Keep-alive 타임아웃 무한정
- `timeout_graceful_shutdown=300`: Graceful shutdown 5분

#### Nginx 설정
- `proxy_connect_timeout 0`: 연결 타임아웃 무한정
- `proxy_send_timeout 0`: 송신 타임아웃 무한정  
- `proxy_read_timeout 0`: 수신 타임아웃 무한정
- `client_body_timeout 0`: 클라이언트 요청 타임아웃 무한정

#### 클라이언트 측 권장사항
```javascript
// JavaScript fetch 예시
const response = await fetch('/face-swap-with-cartoon', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(requestData),
  // 충분한 타임아웃 설정
});
```

```python
# Python requests 예시
import requests

response = requests.post(
    'http://your-api/face-swap-with-cartoon',
    json=request_data,
    timeout=300  # 5분 타임아웃
)
```

### 리소스 요구사항
- **최소**: 2GB RAM, 2 CPU cores
- **권장**: 4GB RAM, 4 CPU cores  
- **스토리지**: 최소 10GB (이미지 임시 저장용)

## 📁 프로젝트 구조

```
102.image_upload_and_swap/
├── app.py                    # 메인 FastAPI 애플리케이션
├── main.py                   # 개별 테스트 스크립트
├── requirements.txt          # Python 의존성
├── Dockerfile               # Docker 이미지 빌드 설정
├── docker-compose.yml       # Docker Compose 설정
├── nginx.conf               # Nginx 설정
├── deploy.sh                # 자동 배포 스크립트
├── face-swap-api.service    # Systemd 서비스 설정
├── source/                  # 원본 이미지 저장소
├── result/                  # 처리 결과 이미지 저장소
└── pair/                    # 테스트 이미지 쌍
```

## 🛠️ 서비스 관리 명령어

```bash
# Docker Compose 서비스
docker-compose ps              # 서비스 상태 확인
docker-compose logs -f         # 실시간 로그 확인
docker-compose restart         # 서비스 재시작
docker-compose down            # 서비스 중지

# Systemd 서비스 (수동 배포 시)
sudo systemctl status face-swap-api    # 서비스 상태 확인
sudo systemctl restart face-swap-api   # 서비스 재시작
sudo systemctl stop face-swap-api      # 서비스 중지
sudo journalctl -u face-swap-api -f    # 실시간 로그

# Nginx 관리
sudo systemctl status nginx     # Nginx 상태 확인
sudo systemctl restart nginx    # Nginx 재시작
sudo nginx -t                   # 설정 파일 검증
```

## 🔍 문제해결

### 1. Service Unavailable 오류
- Docker 컨테이너가 실행 중인지 확인: `docker-compose ps`
- 로그 확인: `docker-compose logs face-swap-api`
- 포트 충돌 확인: `netstat -tlnp | grep :8000`

### 2. 메모리 부족 오류
- EC2 인스턴스 타입 확인 (최소 t3.medium 권장)
- Docker 메모리 제한 확인: `docker stats`
- 스왑 메모리 설정 검토

### 3. API 키 관련 오류
- OpenAI API 키 유효성 및 크레딧 확인
- Replicate API 토큰 권한 확인
- Supabase 프로젝트 설정 및 스토리지 권한 확인

### 4. 이미지 처리 시간 초과
- 이미지 파일 크기 확인 (권장: 10MB 이하)
- 네트워크 연결 상태 확인
- Replicate API 상태 확인

### 5. Docker 관련 이슈
```bash
# Docker 시스템 정리
docker system prune -a

# 이미지 재빌드
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🏗️ 아키텍처

```
Client Request → Nginx (Port 80) → FastAPI (Port 8000) → AI Services
                                                      ↓
                                             Supabase Storage
                                                      ↓
                                              Result Images
```

### 워크플로우
1. **이미지 입력**: URL을 통한 이미지 접수
2. **전처리**: 이미지 다운로드 및 검증
3. **AI 처리**: OpenAI/Replicate API를 통한 얼굴 스왑/캐리커쳐 변환
4. **후처리**: 결과 이미지 최적화 및 Supabase 업로드
5. **응답**: 처리된 이미지 URL 반환

## 🔒 보안 고려사항

- **API 키 관리**: 환경변수 또는 보안 볼트 사용
- **리버스 프록시**: Nginx를 통한 FastAPI 직접 노출 방지
- **파일 검증**: 업로드 이미지 타입 및 크기 제한
- **임시 파일 정리**: 처리 완료 후 로컬 파일 자동 삭제
- **CORS 정책**: 필요에 따라 허용 도메인 제한
- **Rate Limiting**: API 호출 빈도 제한 (필요시 구현)

## 📊 모니터링

### 로그 레벨
- `[INIT]`: 초기화 관련 로그
- `[API]`: API 호출 관련 로그  
- `[DOWNLOAD]`: 이미지 다운로드 로그
- `[CARTOON]`: 캐리커쳐 변환 로그
- `[FACE_SWAP]`: 얼굴 스왑 로그
- `[ERROR]`: 오류 관련 로그

### 성능 메트릭
- 이미지 처리 시간
- API 응답 시간
- 메모리 사용량
- 디스크 I/O

## 🔄 업데이트 및 배포

### 무중단 배포
```bash
# 새 버전 빌드
docker-compose build

# 롤링 업데이트
docker-compose up -d --no-deps --build face-swap-api
```

### 백업 및 복원
```bash
# 데이터 백업
docker-compose exec postgres pg_dump -U user database > backup.sql

# 이미지 백업
tar -czf images_backup.tar.gz source/ result/
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request

## 📄 라이센스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원 및 문의

- **이슈 리포트**: GitHub Issues 탭 활용
- **기능 요청**: GitHub Discussions 활용
- **보안 이슈**: 이메일로 직접 연락

---

> **Note**: 이 API는 AI 모델을 사용하므로 처리 시간이 다소 길 수 있습니다. 대용량 이미지나 복잡한 처리가 필요한 경우 비동기 엔드포인트(`/face-swap`)를 사용하는 것을 권장합니다.