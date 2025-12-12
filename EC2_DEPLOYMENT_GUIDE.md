# EC2 Face Swap API 배포 가이드

## 1. EC2 인스턴스 준비

### 권장 인스턴스 타입
- **최소**: t3.large (2 vCPU, 8GB RAM)
- **권장**: t3.xlarge (4 vCPU, 16GB RAM) 또는 m5.xlarge
- **스토리지**: 최소 20GB 이상

### 보안 그룹 설정
```bash
# 인바운드 규칙
22/tcp (SSH)
80/tcp (HTTP)
443/tcp (HTTPS)
8000/tcp (FastAPI - 선택사항, 개발 목적)
```

## 2. 서버 초기 설정

```bash
# 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3 python3-pip python3-venv nginx git htop

# 방화벽 설정 (UFW)
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## 3. 프로젝트 배포

```bash
# 프로젝트 디렉토리 생성
mkdir -p /home/ubuntu/face-swap-api
cd /home/ubuntu/face-swap-api

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 프로젝트 파일 복사
# app.py, requirements.txt 등 업로드
```

## 4. Systemd 서비스 설정

```bash
# 서비스 파일 복사
sudo cp face-swap-api.service /etc/systemd/system/

# 서비스 파일 권한 설정
sudo chmod 644 /etc/systemd/system/face-swap-api.service

# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 활성화 및 시작
sudo systemctl enable face-swap-api
sudo systemctl start face-swap-api

# 서비스 상태 확인
sudo systemctl status face-swap-api
```

## 5. Nginx 설정

```bash
# 기본 설정 비활성화
sudo rm /etc/nginx/sites-enabled/default

# 새 설정 파일 생성
sudo cp nginx.conf /etc/nginx/sites-available/face-swap-api

# 설정 활성화
sudo ln -s /etc/nginx/sites-available/face-swap-api /etc/nginx/sites-enabled/

# Nginx 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

## 6. 타임아웃 문제 해결 체크리스트

### 애플리케이션 레벨
- ✅ OpenAI 클라이언트 타임아웃: 600초 (10분)
- ✅ Requests 타임아웃: 600초 (10분)
- ✅ Uvicorn graceful shutdown: 1200초 (20분)

### Nginx 레벨
- ✅ proxy_connect_timeout: 1200초 (20분)
- ✅ proxy_send_timeout: 1200초 (20분)
- ✅ proxy_read_timeout: 1200초 (20분)
- ✅ proxy_buffering: off (실시간 응답)

### 시스템 레벨
- ✅ Systemd 서비스 재시작 정책: always
- ✅ 메모리/CPU 제한 없음 (또는 충분한 할당)

## 7. 모니터링 및 로그

```bash
# 서비스 로그 확인
sudo journalctl -u face-swap-api -f

# Nginx 로그 확인
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 시스템 리소스 모니터링
htop
df -h
free -h
```

## 8. 문제 해결

### Face Swap이 여전히 실패하는 경우

1. **메모리 부족 확인**
```bash
free -h
dmesg | grep -i "killed process"  # OOM 킬러 확인
```

2. **CPU 사용률 확인**
```bash
top
htop
```

3. **네트워크 연결 확인**
```bash
curl -I https://api.openai.com
curl -I https://api.replicate.com
```

4. **디스크 공간 확인**
```bash
df -h
ls -la /tmp  # 임시 파일 확인
```

### 로그에서 확인할 내용
- `[ERROR]` 태그가 붙은 에러 메시지
- `timeout` 관련 메시지
- `connection` 관련 에러
- 메모리 부족 관련 메시지

## 9. 성능 최적화 팁

### EC2 인스턴스 최적화
```bash
# 스왑 파일 생성 (메모리 부족 대비)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 임시 파일 정리 자동화
```bash
# crontab 추가
echo "0 */6 * * * find /tmp -name '*.png' -mtime +1 -delete" | crontab -
```

## 10. 테스트

```bash
# 서비스 상태 확인
curl http://localhost/health

# Face Swap API 테스트
curl -X POST http://localhost/face-swap \
  -H "Content-Type: application/json" \
  -d '{
    "base_image_url": "https://example.com/base.jpg",
    "face_image_url": "https://example.com/face.jpg"
  }'
```

## 주요 변경사항 요약

1. **OpenAI 클라이언트**: 600초 타임아웃 추가
2. **Requests 호출**: 600초 타임아웃으로 증가 
3. **Uvicorn 설정**: graceful shutdown 1200초로 증가
4. **Nginx 프록시**: 모든 타임아웃을 1200초로 설정
5. **버퍼링 비활성화**: 실시간 응답을 위해 proxy_buffering off

이 설정들로 Face Swap API의 긴 처리 시간을 견딜 수 있게 됩니다. 