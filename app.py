import os
import requests
from flask import Flask, request, jsonify

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

@app.before_request
def handle_options_request():
    """CORS OPTIONS (pre-flight) अनुरोधों को संभालता है"""
    if request.method == 'OPTIONS':
        # CORS हेडर सेट करें
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        # [फिक्स] सुनिश्चित करें कि CORS प्री-फ़्लाइट अनुरोधों को सही ढंग से संभाला जाए
        return response

# 👇 फिक्स: methods=['GET'] को methods=['GET', 'OPTIONS'] से बदल दिया गया
@app.route('/', defaults={'path': ''}, methods=['GET', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'OPTIONS'])
def proxy_tmdb_api(path):
    """आने वाले अनुरोधों को TMDB API तक प्रॉक्सी करता है"""
    
    # 🛑 यदि अनुरोध OPTIONS है, तो इसे @app.before_request ने पहले ही संभाल लिया होगा।
    # हमें यहां दोबारा कुछ करने की आवश्यकता नहीं है, लेकिन सुनिश्चित करें कि GET ही प्रॉसेस हो।
    if request.method == 'OPTIONS':
        # यह लाइन तकनीकी रूप से अनावश्यक है क्योंकि @app.before_request ने इसे पहले ही संभाल लिया होगा,
        # लेकिन यह एक सुरक्षात्मक उपाय है यदि कोई OPTIONS अनुरोध @app.before_request से चूक जाता है।
        res = jsonify({'status': 'ok'})
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res, 204 # 204 No Content भेजना CORS OPTIONS के लिए मानक है
    
    # 1. CORS हेडर सेट करें (GET अनुरोधों के लिए)
    res = jsonify({}) # एक डमी रिस्पॉन्स ऑब्जेक्ट
    res.headers['Access-Control-Allow-Origin'] = '*'

    # 2. TMDB के लिए पूरा URL बनाएँ
    full_tmdb_url = f"{TMDB_BASE_URL}/{path}"
    
    # 3. सभी query parameters प्राप्त करें और API Key जोड़ें
    params = request.args.to_dict()
    params['api_key'] = TMDB_KEY
    
    try:
        # 4. TMDB API को अनुरोध भेजें
        response = requests.get(full_tmdb_url, params=params, timeout=10)
        response.raise_for_status() # HTTP एरर के लिए रेज़ करें (4xx/5xx)

        # 5. TMDB का डेटा और स्टेटस कोड वापस भेजें
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        # 6. Errors को हैंडल करें
        status_code = e.response.status_code if e.response is not None else 500
        error_message = e.response.json().get('status_message', str(e)) if e.response is not None else str(e)

        return jsonify({
            "error": "Proxy Request Failed",
            "details": error_message,
            "status_code": status_code
        }), status_code

# Koyeb Gunicorn/Buildpack को पोर्ट पर सुनो
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
