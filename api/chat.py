from http.server import BaseHTTPRequestHandler
import json
import os
import openai

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # تنظیم API Key از متغیر محیطی
            openai.api_key = os.environ.get('OPENAI_API_KEY')
            
            if not openai.api_key:
                raise ValueError("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")
            
            # خواندن داده‌های ورودی
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data)
            
            user_message = request_data.get('message', '')
            
            # ارسال به OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500
            )
            
            bot_reply = response.choices[0].message['content'].strip()
            
            # ارسال پاسخ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": bot_reply}).encode())
            
        except Exception as e:
            # مدیریت خطا
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = f"خطا در پردازش: {str(e)}"
            self.wfile.write(json.dumps({"reply": error_msg}).encode())
