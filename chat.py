from http.server import BaseHTTPRequestHandler
import json
import openai

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # خواندن داده‌های ورودی
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data)
            
            user_message = request_data.get('message', '')
            
            # جایگزین کن با API Key واقعی
            openai.api_key = "sk-کلید-API-شما-اینجا"
            
            # ارسال به OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150
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
            self.wfile.write(json.dumps({"reply": "خطا در پردازش درخواست"}).encode())
