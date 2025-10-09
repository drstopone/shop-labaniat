from http.server import BaseHTTPRequestHandler
import json
import requests
import re
import html
import os

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def markdown_to_html(self, text):
        """تبدیل هوشمند متن به HTML با تشخیص خودکار کد"""
        if not text:
            return text
        
        # امن‌سازی HTML
        text = html.escape(text)
        
        # بولد و ایتالیک
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # 🔥 تشخیص خودکار کدهای برنامه‌نویسی
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            # اگر خط شبیه کد باشه
            if self.looks_like_code(line):
                formatted_lines.append(f'<code>{line}</code>')
            else:
                formatted_lines.append(line)
        
        text = '<br>'.join(formatted_lines)
        
        # تبدیل backtickهای باقی‌مانده
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # تبدیل لیست‌های bullet point
        text = re.sub(r'^\* (.*?)$', r'• \1', text, flags=re.MULTILINE)
        
        return text

    def looks_like_code(self, line):
        """تشخیص اینکه آیا خط شبیه کد برنامه‌نویسی هست"""
        line_clean = line.strip()
        
        # الگوهای کد
        code_patterns = [
            # پایتون
            r'^python\s*$',
            r'^print\(.*\)\s*$',
            r'^def\s+\w+',
            r'^import\s+\w+',
            r'^from\s+\w+',
            r'^class\s+\w+',
            
            # جاوااسکریپت/باش
            r'^bash\s*$',
            r'^console\.log\(.*\)\s*$',
            r'^function\s+\w+',
            r'^const\s+\w+',
            r'^let\s+\w+',
            r'^var\s+\w+',
            
            # دستورات ترمینال
            r'^\w+\.py\s*$',
            r'^python\s+\w+\.py\s*$',
            r'^\.\/\w+',
            
            # کدهای واضح
            r'^[\w]+\.[\w]+\(.*\)\s*$',  # متد call
            r'^[\w]+\(.*\)\s*$',         # تابع call
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, line_clean, re.IGNORECASE):
                return True
        
        return False
    
    def do_POST(self):
        try:
            # خواندن پیام کاربر
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data)
            
            user_message = request_data.get('message', '')
            print(f"📨 پیام کاربر: {user_message}")
            
            # استفاده از Google Gemini
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
                    
                    # تبدیل Markdown به HTML
                    bot_reply_html = self.markdown_to_html(bot_reply)
                    print("✅ پاسخ از Gemini دریافت و تبدیل شد")
                else:
                    bot_reply_html = "⚠️ ساختار پاسخ غیرمنتظره از Gemini"
                    
            else:
                error_msg = response.text
                print(f"❌ خطا: {error_msg}")
                bot_reply_html = f"⚠️ خطا از سمت Gemini (کد: {response.status_code})"
            
            # ارسال پاسخ
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": bot_reply_html}).encode())
            
            print("✅ پاسخ ارسال شد")
            
        except Exception as e:
            error_msg = f"خطا: {str(e)}"
            print(f"❌ {error_msg}")
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": "خطا در سرور: " + str(e)}).encode())
