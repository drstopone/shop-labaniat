from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI

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
            
            # ایجاد کلید OpenAI با نسخه جدید
            client = OpenAI(api_key=api_key)
            
            # ارسال به OpenAI
            response = client.chat.completions.create(
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
