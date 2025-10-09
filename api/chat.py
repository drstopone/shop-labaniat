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
            api_key = os.environ.get('AIzaSyBmGVicWfMWTjkxuMjgJuB-bDbLexFttHs')
            
            if not api_key:
                # اگر API Key نیست، پاسخ تستی بده
                bot_reply = f"سلام! پیام '{user_message}' رو دریافت کردم. (در حال تست - API Key تنظیم نشده)"
            else:
                # ارسال به Google Gemini
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
                
                data = {
                    "contents": [{
                        "parts": [{"text": user_message}]
                    }]
                }
                
                response = requests.post(url, json=data)
                result = response.json()
                
                if response.status_code == 200:
                    bot_reply = result['candidates'][0]['content']['parts'][0]['text']
                    print("✅ پاسخ از Gemini دریافت شد")
                else:
                    bot_reply = f"خطا از سمت Gemini: {result.get('error', {}).get('message', 'خطای ناشناخته')}"
                    print(f"❌ خطای Gemini: {bot_reply}")
            
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
