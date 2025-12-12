#!/bin/bash

echo "=== Face Swap API 배포 스크립트 시작 ==="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 현재 사용자와 홈 디렉토리 확인
USER=$(whoami)
HOME_DIR="/home/$USER"
PROJECT_DIR="$HOME_DIR/face-swap-api"

echo -e "${YELLOW}현재 사용자: $USER${NC}"
echo -e "${YELLOW}프로젝트 디렉토리: $PROJECT_DIR${NC}"

# 1. 시스템 업데이트
echo -e "${GREEN}1. 시스템 업데이트 중...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. 필요한 패키지 설치
echo -e "${GREEN}2. 필요한 패키지 설치 중...${NC}"
sudo apt install -y python3 python3-pip python3-venv nginx supervisor

# 3. 프로젝트 디렉토리 생성
echo -e "${GREEN}3. 프로젝트 디렉토리 설정 중...${NC}"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 4. 가상환경 생성 및 활성화
echo -e "${GREEN}4. Python 가상환경 설정 중...${NC}"
python3 -m venv venv
source venv/bin/activate

# 5. 필요한 Python 패키지 설치
echo -e "${GREEN}5. Python 패키지 설치 중...${NC}"
pip install --upgrade pip
pip install fastapi uvicorn[standard] python-multipart requests openai replicate supabase

# 6. 작업 디렉토리 생성
echo -e "${GREEN}6. 작업 디렉토리 생성 중...${NC}"
mkdir -p source result

# 7. systemd 서비스 파일 설정
echo -e "${GREEN}7. systemd 서비스 설정 중...${NC}"
sudo cp face-swap-api.service /etc/systemd/system/
sudo sed -i "s|/home/ubuntu|$HOME_DIR|g" /etc/systemd/system/face-swap-api.service
sudo sed -i "s|User=ubuntu|User=$USER|g" /etc/systemd/system/face-swap-api.service
sudo systemctl daemon-reload

# 8. Nginx 설정
echo -e "${GREEN}8. Nginx 설정 중...${NC}"
sudo cp nginx.conf /etc/nginx/nginx.conf

# Nginx 설정 테스트
if sudo nginx -t; then
    echo -e "${GREEN}Nginx 설정이 올바릅니다.${NC}"
else
    echo -e "${RED}Nginx 설정에 오류가 있습니다. 확인해주세요.${NC}"
    exit 1
fi

# 9. 서비스 시작
echo -e "${GREEN}9. 서비스 시작 중...${NC}"

# FastAPI 서비스 시작
sudo systemctl enable face-swap-api
sudo systemctl start face-swap-api

# Nginx 재시작
sudo systemctl enable nginx
sudo systemctl restart nginx

# 10. 서비스 상태 확인
echo -e "${GREEN}10. 서비스 상태 확인 중...${NC}"

sleep 5

echo "=== FastAPI 서비스 상태 ==="
sudo systemctl status face-swap-api --no-pager

echo "=== Nginx 서비스 상태 ==="
sudo systemctl status nginx --no-pager

echo "=== 포트 확인 ==="
sudo netstat -tlnp | grep -E ':80|:8000'

# 11. 방화벽 설정 (UFW가 설치된 경우)
if command -v ufw &> /dev/null; then
    echo -e "${GREEN}11. 방화벽 설정 중...${NC}"
    sudo ufw allow 80/tcp
    sudo ufw allow 8000/tcp
    sudo ufw --force enable
fi

# 12. 헬스체크
echo -e "${GREEN}12. 헬스체크 수행 중...${NC}"
sleep 10

if curl -f http://localhost/health; then
    echo -e "${GREEN}✅ 헬스체크 성공! API가 정상적으로 실행되고 있습니다.${NC}"
else
    echo -e "${RED}❌ 헬스체크 실패. 로그를 확인해주세요.${NC}"
    echo "FastAPI 로그:"
    sudo journalctl -u face-swap-api --no-pager -n 20
fi

echo -e "${GREEN}=== 배포 완료 ===${NC}"
echo -e "${YELLOW}API 엔드포인트:${NC}"
echo "- 메인: http://$(curl -s ifconfig.me)/"
echo "- 헬스체크: http://$(curl -s ifconfig.me)/health"
echo "- 얼굴 스왑: http://$(curl -s ifconfig.me)/face-swap"
echo "- 캐리커쳐 얼굴 스왑: http://$(curl -s ifconfig.me)/face-swap-with-cartoon"
echo "- 캐리커쳐만: http://$(curl -s ifconfig.me)/cartoonify-only"

echo -e "${YELLOW}유용한 명령어:${NC}"
echo "- 서비스 상태 확인: sudo systemctl status face-swap-api"
echo "- 서비스 재시작: sudo systemctl restart face-swap-api"
echo "- 로그 확인: sudo journalctl -u face-swap-api -f"
echo "- Nginx 재시작: sudo systemctl restart nginx" 