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
        #"""تبدیل هوشمند - فقط کدهای واقعی رو تبدیل کن"""
        if not text:
            return text
        
        try:
            # امن‌سازی HTML
            text = html.escape(text)
            
            # بولد و ایتالیک
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            
            # 🔥 فقط کدهای واقعی رو تبدیل کن
            
            # ۱. کدهای بلوک کامل:        
            text = re.sub(
                r'```(\w+)?\s*([^`]+)```', 
                lambda m: f'<div class="code-container"><button class="copy-btn" onclick="copyCode(this)">📋</button><pre><code data-language="{m.group(1)}">{m.group(2)}</code></pre></div>' 
                if self.is_real_code(m.group(2)) 
                else f'<pre>{m.group(2)}</pre>',
                text, 
                flags=re.DOTALL
            )
            
            # ۲. کدهای inline: print("hello")
            text = re.sub(
                r'`([^`\n]+)`', 
                lambda m: f'<code class="inline-code">{m.group(1)}</code>' 
                if self.is_real_code(m.group(1)) 
                else f'<span class="quoted-text">{m.group(1)}</span>',
                text
            )
            
            # خطوط جدید به <br>
            text = text.replace('\n', '<br>')
            
            return text
        
    except Exception as e:
        print(f"⚠️ خطا در تبدیل Markdown: {e}")
        return text
    
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
