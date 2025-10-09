from http.server import BaseHTTPRequestHandler
import json
import os

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
            
            # بررسی API Key
            api_key = os.environ.get('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')
            if not api_key:
                raise ValueError("API Key پیدا نشد")
            
            # ایمپورت openai - سازگار با نسخه‌های مختلف
            try:
                # روش جدید (نسخه >=1.0.0)
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=150
                )
                bot_reply = response.choices[0].message.content
                
            except ImportError:
                # روش قدیمی (نسخه <1.0.0)
                import openai
                openai.api_key = api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=150
                )
                bot_reply = response.choices[0].message.content
            
            print(f"🤖 پاسخ: {bot_reply}")
            
            # ارسال پاسخ موفق
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": bot_reply}).encode())
            
            print("✅ درخواست با موفقیت پردازش شد")
            
        except Exception as e:
            error_msg = f"خطا: {str(e)}"
            print(f"❌ {error_msg}")
            
            # پاسخ خطا به کاربر
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": "خطا در پردازش درخواست: " + str(e)}).encode())
