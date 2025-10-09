from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            # خواندن پیام کاربر
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data)
            
            user_message = request_data.get('message', '')
            print(f"📨 پیام کاربر: {user_message}")
            
            # استفاده از Google Gemini
            api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBmGVicWfMWTjkxuMjgJuB-bDbLexFttHs')
            
            # ارسال به Google Gemini - با مدل درست
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            data = {
                "contents": [{
                    "parts": [{"text": user_message}]
                }]
            }
            
            response = requests.post(url, json=data)
            result = response.json()
            
            print(f"🔧 وضعیت پاسخ: {response.status_code}")
            print(f"🔧 پاسخ کامل: {result}")
            
            if response.status_code == 200:
                if 'candidates' in result and len(result['candidates']) > 0:
                    bot_reply = result['candidates'][0]['content']['parts'][0]['text']
                    print("✅ پاسخ از Gemini دریافت شد")
                else:
                    bot_reply = "⚠️ ساختار پاسخ غیرمنتظره از Gemini"
            else:
                error_msg = result.get('error', {}).get('message', 'خطای ناشناخته')
                bot_reply = f"⚠️ خطا از سمت Gemini: {error_msg}"
                print(f"❌ خطای Gemini: {error_msg}")
            
            # ارسال پاسخ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": bot_reply}).encode())
            
            print("✅ پاسخ ارسال شد")
            
        except Exception as e:
            error_msg = f"خطا: {str(e)}"
            print(f"❌ {error_msg}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": "خطا در سرور: " + str(e)}).encode())
