from http.server import BaseHTTPRequestHandler
import json
import requests
import re
import html

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def markdown_to_html(self, text):
    """تبدیل Markdown ساده به HTML"""
    if not text:
        return text
    
    # امن‌سازی HTML - مهم!
    text = html.escape(text)
    
    # متن به <strong>متن</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # *متن* به <em>متن</em>
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # کد به <code>کد</code>
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    
    # خطوط جدید به <br>
    text = text.replace('\n', '<br>')
    
    return text
    
    def do_POST(self):
        try:
            # خواندن پیام کاربر
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data)
            
            user_message = request_data.get('message', '')
            print(f"📨 پیام کاربر: {user_message}")
            
            # استفاده از Google Gemini 2.0 Flash - با مستندات درست
            api_key = "AIzaSyBmGVicWfMWTjkxuMjgJuB-bDbLexFttHs"
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': api_key
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": user_message
                            }
                        ]
                    }
                ]
            }
            
            print("🔧 در حال ارسال درخواست به Gemini...")
            response = requests.post(url, headers=headers, json=data)
            print(f"🔧 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"🔧 پاسخ کامل: {result}")
                
                # استخراج پاسخ از ساختار JSON
                if 'candidates' in result and len(result['candidates']) > 0:
                    bot_reply = result['candidates'][0]['content']['parts'][0]['text']
                    print("✅ پاسخ از Gemini دریافت شد")
                else:
                    bot_reply = "⚠️ ساختار پاسخ غیرمنتظره از Gemini"
                    
            else:
                error_msg = response.text
                print(f"❌ خطا: {error_msg}")
                bot_reply = f"⚠️ خطا از سمت Gemini (کد: {response.status_code})"
            
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
