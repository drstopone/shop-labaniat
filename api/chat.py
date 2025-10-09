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
            
            # پاسخ تستی - بدون وابستگی به OpenAI
            if "سلام" in user_message:
                bot_reply = "سلام! چطور می‌تونم کمک کنم؟ 😊"
            elif "چطوری" in user_message:
                bot_reply = "خوبم ممنون! شما چطوری؟"
            else:
                bot_reply = f"پیام شما: '{user_message}' رو دریافت کردم. این یک پاسخ تستی است."
            
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
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": "خطا در پردازش درخواست"}).encode())
