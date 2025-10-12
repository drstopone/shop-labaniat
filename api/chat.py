from http.server import BaseHTTPRequestHandler
import json
import requests
import re
import html

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def is_real_code(self, text):
        """تشخیص اینکه آیا متن واقعاً کد برنامه‌نویسی است"""
        if not text or not text.strip():
            return False
        
        text = text.strip()
        
        # نشانگرهای کد برنامه‌نویسی
        code_indicators = [
            'function', 'def ', 'class ', 'import ', 'export ', 'const ', 'let ', 'var ',
            'if ', 'for ', 'while ', 'return ', 'print', 'console.log',
            '#include', 'using ', 'namespace ', 'public ', 'private ', 'protected ',
            '<html', '<div', '<script', '<style', '<?php', '<?=', '<?',
            'SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'CREATE ', 'ALTER ',
            'FROM ', 'WHERE ', 'JOIN ', 'GROUP BY ', 'ORDER BY '
        ]
        
        # کاراکترهای خاص کد
        code_chars = ['{', '}', ';', '=', '(', ')', '[', ']', '<', '>', '$', '@']
        
        # ساختارهای کد
        code_patterns = [
            r'^\s*\w+\s*\(.*\)\s*\{',
            r'^\s*\w+\s+[\w_]+\s*=',
            r'^\s*#',
            r'^\s*//',
            r'^\s*/\*',
        ]
        
        # بررسی نشانگرها
        text_lower = text.lower()
        for indicator in code_indicators:
            if indicator in text_lower:
                return True
        
        # بررسی کاراکترهای خاص
        code_char_count = sum(1 for char in code_chars if char in text)
        if code_char_count >= 2:
            return True
        
        # بررسی الگوها
        for pattern in code_patterns:
            if re.search(pattern, text):
                return True
        
        if len(text) < 10:
            return False
        
        return False
    
    def markdown_to_html(self, text):
        """تبدیل مارک‌داون به HTML"""
        if not text:
            return text
        
        try:
            # امن‌سازی HTML
            text = html.escape(text)
            
            # بولد و ایتالیک
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            
            # تبدیل کدهای بلوک
            def process_code_block(match):
                language = match.group(1) or 'text'
                code_content = match.group(2).strip()
                return f'<div class="code-container"><button class="copy-btn" onclick="copyCode(this)">📋</button><pre><code data-language="{language}">{code_content}</code></pre></div>'
            
            text = re.sub(
                r'```(\w+)?\s*([^`]+)```', 
                process_code_block,
                text, 
                flags=re.DOTALL
            )
            
            # تبدیل کدهای inline
            def process_inline_code(match):
                code_content = match.group(1)
                if self.is_real_code(code_content):
                    return f'<code class="inline-code">{code_content}</code>'
                else:
                    return f'<span class="quoted-text">`{code_content}`</span>'
            
            text = re.sub(
                r'`([^`\n]+)`', 
                process_inline_code,
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
                content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' in content_type:
                # پردازش فرم داده با عکس
                import cgi
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST',
                            'CONTENT_TYPE': self.headers['Content-Type']}
                )
                
                user_message = form.getvalue('message', '')
                history_json = form.getvalue('history', '[]')
                client_history = json.loads(history_json)
                
                image_file = form['image'] if 'image' in form else None
                
                print(f"📨 پیام کاربر: {user_message}")
                print(f"📸 عکس آپلود شده: {'بله' if image_file else 'خیر'}")
                
            else:
                # پردازش JSON معمولی
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data)
                
                user_message = request_data.get('message', '')
                client_history = request_data.get('history', [])
                image_file = None

            # خواندن پیام کاربر و تاریخچه
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data)
            
            user_message = request_data.get('message', '')
            client_history = request_data.get('history', [])  # 🔥 دریافت تاریخچه از کلاینت
            
            print(f"📨 پیام کاربر: {user_message}")
            print(f"📚 تاریخچه از کلاینت: {len(client_history)} پیام")
            
            # 🔥 نمایش تاریخچه برای دیباگ
            for i, msg in enumerate(client_history):
                role = "کاربر" if msg.get("role") == "user" else "ربات"
                text_preview = msg.get("text", "")[:50] + "..." if len(msg.get("text", "")) > 50 else msg.get("text", "")
                print(f"   {i+1}. {role}: {text_preview}")
            
            # استفاده از Google Gemini
            api_key = "AIzaSyBmGVicWfMWTjkxuMjgJuB-bDbLexFttHs"
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': api_key
            }
            
            # 🔥 ساختاردهی به تاریخچه برای Gemini
            contents = []
            
            if client_history:
                # اگر تاریخچه داریم، تمامش رو به فرمت Gemini تبدیل می‌کنیم
                for msg in client_history:
                    role = "user" if msg.get("role") == "user" else "model"
                    text = msg.get("text", "")
                    if text:  # فقط پیام‌های غیرخالی رو اضافه کن
                        contents.append({
                            "role": role,
                            "parts": [{"text": text}]
                        })
            
            # اضافه کردن پیام جدید کاربر
            contents.append({
                "role": "user",
                "parts": [{"text": user_message}]
            })
            
            data = {
                "contents": contents
            }
            
            print(f"🔧 ارسال {len(contents)} پیام به Gemini...")
            
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
