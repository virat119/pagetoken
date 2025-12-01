import os
import requests
from flask import Flask, request, jsonify, make_response

# Flask एप्लिकेशन को इनिशियलाइज़ करें
app = Flask(__name__)

# Environment Variable से TMDB Key लें
TMDB_KEY = os.environ.get('TMDB_KEY')

# यदि Key नहीं मिली, तो ऐप शुरू करने से पहले एरर दें
if not TMDB_KEY:
    print("FATAL ERROR: TMDB_KEY environment variable is not set.")
    exit(1)

# TMDB का बेस URL
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

# ========== FIX: CORS Middleware Function ==========
@app.after_request
def add_cors_headers(response):
    """सभी responses में CORS headers add करता है"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
    return response

@app.before_request
def handle_options_request():
    """CORS OPTIONS (pre-flight) अनुरोधों को संभालता है"""
    if request.method == 'OPTIONS':
        # CORS pre-flight request के लिए response
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        return response, 200

@app.route('/', defaults={'path': ''}, methods=['GET', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'OPTIONS'])
def proxy_tmdb_api(path):
    """आने वाले अनुरोधों को TMDB API तक प्रॉक्सी करता है"""
    
    # OPTIONS request handle करें (pre-flight CORS)
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200

    # 2. TMDB के लिए पूरा URL बनाएँ
    full_tmdb_url = f"{TMDB_BASE_URL}/{path}"
    
    # 3. सभी query parameters प्राप्त करें और API Key जोड़ें
    params = request.args.to_dict()
    params['api_key'] = TMDB_KEY
    
    # लैंग्वेज पैरामीटर जोड़ें (अगर नहीं है तो)
    if 'language' not in params:
        params['language'] = 'hi-IN'
    
    try:
        # 4. TMDB API को अनुरोध भेजें
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(full_tmdb_url, params=params, headers=headers, timeout=15)
        response.raise_for_status() # HTTP एरर के लिए रेज़ करें (4xx/5xx)

        # 5. TMDB का डेटा और स्टेटस कोड वापस भेजें
        return jsonify(response.json()), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Request Timeout",
            "details": "TMDB API took too long to respond",
            "status_code": 504
        }), 504
        
    except requests.exceptions.RequestException as e:
        # 6. Errors को हैंडल करें
        status_code = e.response.status_code if e.response is not None else 500
        
        if e.response is not None and e.response.text:
            try:
                error_message = e.response.json().get('status_message', str(e))
            except:
                error_message = e.response.text
        else:
            error_message = str(e)

        return jsonify({
            "error": "Proxy Request Failed",
            "details": error_message,
            "status_code": status_code,
            "tmdb_url": full_tmdb_url
        }), status_code

# Health Check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "TMDB Proxy",
        "tmdb_key_set": bool(TMDB_KEY)
    }), 200

# Koyeb Gunicorn/Buildpack को पोर्ट पर सुनो
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 TMDB Proxy Server starting on port {port}")
    print(f"🔑 TMDB Key: {'Set' if TMDB_KEY else 'Not Set'}")
    app.run(host='0.0.0.0', port=port, debug=False)
