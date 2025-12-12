# EC2 배포 및 실행 가이드

## 타임아웃 문제 해결 방법

### 1. 기본 실행 (개발용)
```bash
python app.py
```

### 2. 최적화된 실행 (EC2 권장)
```bash
python run_server.py
```

### 3. Gunicorn을 이용한 프로덕션 실행 (가장 안정적)
```bash
# gunicorn 설치
pip install gunicorn

# 실행
gunicorn -c gunicorn.conf.py app:app
```

## 변경된 타임아웃 설정

### 애플리케이션 레벨
- `timeout_keep_alive`: 0 (무제한)
- `timeout_graceful_shutdown`: 600초 (10분)
- `timeout_worker`: 3600초 (1시간)
- `timeout_notify`: 30-60초

### 네트워크 레벨
- `requests.get()` 타임아웃: 300초 (5분)
- HTTP 요청 크기 제한: 16MB

### 워커 설정
- 단일 워커 사용 (메모리 최적화)
- 최대 동시 연결: 1000개
- 요청 수 제한: 무제한

## 추가 최적화 팁

### 1. EC2 인스턴스 설정
```bash
# 메모리 스왑 설정 (필요시)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 시스템 한계 증가
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
```

### 2. 로드 밸런서 설정 (필요시)
- ALB 타임아웃: 900초 (15분)
- 헬스체크 간격 조정

### 3. CloudWatch 모니터링
- 메모리 사용률 모니터링
- 응답 시간 모니터링
- 에러 로그 확인

## 문제 해결

### Service Unavailable 에러가 계속 발생하는 경우:
1. `run_server.py` 사용
2. EC2 인스턴스 타입 업그레이드 (더 많은 메모리/CPU)
3. Gunicorn 사용으로 전환
4. 로드 밸런서 타임아웃 설정 확인

### 메모리 부족 에러:
1. 스왑 파일 설정
2. 인스턴스 타입 업그레이드
3. 이미지 처리 후 메모리 정리 확인

### 실행 명령어 순서대로 시도:
```bash
# 1단계: 기본 최적화 실행
python run_server.py

# 2단계: Gunicorn 실행 (권장)
pip install gunicorn
gunicorn -c gunicorn.conf.py app:app

# 3단계: 백그라운드 실행
nohup gunicorn -c gunicorn.conf.py app:app > app.log 2>&1 &
``` 