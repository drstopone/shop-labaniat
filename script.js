'<div class="code-container"><button class="copy-btn" onclick="copyCode(this)">📋</button><pre><code data-language="$1">$2</code></pre></div>'
        );
    }
    
    return processedContent;
}

// تابع global برای کپی کردن کد
window.copyCode = async function(button) {
    const codeContainer = button.parentElement;
    const codeElement = codeContainer.querySelector('code, pre');
    
    if (codeElement) {
        const textToCopy = codeElement.textContent || codeElement.innerText;
        
        try {
            await navigator.clipboard.writeText(textToCopy);
            
            // نمایش تأیید
            button.textContent = '✅';
            button.style.background = '#10b981';
            
            setTimeout(() => {
                button.textContent = '📋';
                button.style.background = '';
            }, 2000);
            
        } catch (err) {
            // روش fallback برای مرورگرهای قدیمی
            const textArea = document.createElement('textarea');
            textArea.value = textToCopy;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            button.textContent = '✅';
            setTimeout(() => {
                button.textContent = '📋';
            }, 2000);
        }
    }
}

// =============================================
// 💾 مدیریت تاریخچه ساده در localStorage
// =============================================

function saveChatHistory() {
    const chatContainer = document.getElementById('chatContainer');
    const messages = [];
    
    // جمع‌آوری تمام پیام‌ها
    document.querySelectorAll('.message').forEach(msg => {
        messages.push({
            text: msg.innerHTML,
            sender: msg.classList.contains('user-message') ? 'user' : 'bot',
            time: new Date().toISOString()
        });
    });
    
    localStorage.setItem('chatHistory', JSON.stringify(messages));
}

function loadChatHistory() {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
        const messages = JSON.parse(saved);
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.innerHTML = '';
        
        messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            
            // 🔥 اصلاح: استفاده از رشته معمولی
            messageDiv.className = 'message ' + msg.sender + '-message';
            messageDiv.innerHTML = msg.text;
            chatContainer.appendChild(messageDiv);
        });
        
        chatContainer.scrollTop = chatContainer.scrollHeight;
        console.log('📂 چت بازیابی شد');
    }
}

// =============================================
// 🧹 پاک کردن تاریخچه چت
// =============================================

function clearChatHistory() {
    if (confirm('آیا از پاک کردن تاریخچه چت مطمئن هستید؟')) {
        localStorage.removeItem('chatHistory');
        document.getElementById('chatContainer').innerHTML = '';
        console.log('🗑️ تاریخچه چت پاک شد');
    }
}
