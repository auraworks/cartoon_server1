from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from describe_gemini import get_top_3_features_english
import base64
import uuid
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/features', methods=['POST'])
def get_image_features():
    """
    이미지에서 주요 특징 3가지를 영어로 반환하는 API
    
    Request Body:
    {
        "image_url": "http://example.com/image.jpg"  // 이미지 URL (선택)
        또는
        "image_base64": "data:image/jpeg;base64,..."  // Base64 이미지 (선택)
    }
    
    Response:
    {
        "success": true,
        "features": [
            "feature1",
            "feature2", 
            "feature3"
        ],
        "request_id": "uuid"
    }
    """
    try:
        # 요청 ID 생성
        request_id = str(uuid.uuid4())
        
        # 요청 데이터 파싱
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided",
                "request_id": request_id
            }), 400
        
        image_url = data.get('image_url')
        image_base64 = data.get('image_base64')
        
        # 이미지 URL 또는 Base64 중 하나는 필수
        if not image_url and not image_base64:
            return jsonify({
                "success": False,
                "error": "Either image_url or image_base64 is required",
                "request_id": request_id
            }), 400
        
        # 제미니를 통해 특징 추출
        features = get_top_3_features_english(
            image_url=image_url,
            base64_image=image_base64
        )
        
        if features is None:
            return jsonify({
                "success": False,
                "error": "Failed to analyze image features",
                "request_id": request_id
            }), 500
        
        # 정확히 3개의 특징이 없는 경우 처리
        if len(features) < 3:
            # 부족한 경우 "General appearance" 같은 기본값으로 채움
            while len(features) < 3:
                features.append("General appearance")
        
        return jsonify({
            "success": True,
            "features": features[:3],  # 최대 3개만 반환
            "request_id": request_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}",
            "request_id": request_id if 'request_id' in locals() else str(uuid.uuid4())
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    return jsonify({
        "status": "healthy",
        "service": "Gemini Image Features API"
    }), 200

@app.route('/', methods=['GET'])
def home():
    """API 정보 페이지"""
    return jsonify({
        "service": "Gemini Image Features API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/features": "Extract top 3 features from image in English",
            "GET /api/health": "Health check",
            "GET /": "API information"
        },
        "usage": {
            "endpoint": "/api/features",
            "method": "POST",
            "body": {
                "image_url": "http://example.com/image.jpg (optional)",
                "image_base64": "data:image/jpeg;base64,... (optional)"
            },
            "note": "Provide either image_url or image_base64"
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Gemini Image Features API starting on port {port}")
    print(f"📋 API Endpoints:")
    print(f"   POST /api/features - Extract image features")
    print(f"   GET  /api/health   - Health check")
    print(f"   GET  /            - API information")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)