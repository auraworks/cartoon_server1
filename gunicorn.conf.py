# Gunicorn 설정 파일 (프로덕션 환경용)

# 서버 소켓
bind = "0.0.0.0:8000"
backlog = 2048

# 워커 프로세스
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 0  # 무제한
max_requests_jitter = 0

# 타임아웃 설정 (매우 길게 설정)
timeout = 3600  # 1시간
keepalive = 30
graceful_timeout = 600  # 10분

# 로깅
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 이름
proc_name = "face_swap_api"

# 보안
limit_request_line = 8190
limit_request_fields = 200
limit_request_field_size = 8190

# 성능 최적화
preload_app = False
sendfile = True
reuse_port = True

# SSL (필요시)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# 재시작 설정
max_requests_jitter = 100
preload_app = False

# 디버깅
capture_output = True
enable_stdio_inheritance = True 