// =============================================
// ✉️ مدیریت ارسال و دریافت پیام
// =============================================

let lastMessageTime = 0;
const MESSAGE_DELAY = 2000; // 2 ثانیه تأخیر بین پیام‌ها

// 🔥 ترکیب هر دو روش: sessionStorage + متغیر موقت
let temporaryHistory = [];

function getTemporaryHistory() {
    // اول از sessionStorage چک کن، اگر نبود از متغیر موقت
    const sessionHistory = sessionStorage.getItem('temporaryHistory');
    if (sessionHistory) {
        temporaryHistory = JSON.parse(sessionHistory);
    }
    return temporaryHistory;
}

function addToTemporaryHistory(role, text) {
    temporaryHistory.push({ role, text, time: new Date().toISOString() });
    
    // همزمان در sessionStorage هم ذخیره کن
    sessionStorage.setItem('temporaryHistory', JSON.stringify(temporaryHistory));
    
    console.log(`📚 تاریخچه موقت: ${temporaryHistory.length} پیام`);
}

function clearTemporaryHistory() {
    temporaryHistory = [];
    sessionStorage.removeItem('temporaryHistory');
    localStorage.removeItem('chatHistory'); // 🔥 پاک کردن تاریخچه نمایش هم
    console.log('🗑️ تاریخچه موقت و نمایش پاک شد');
}

// 🔥 پاک کردن تاریخچه هنگام لود صفحه (رفرش)
function clearOnRefresh() {
    // پاک کردن تاریخچه موقت
    temporaryHistory = [];
    sessionStorage.removeItem('temporaryHistory');
    
    // پاک کردن تاریخچه نمایش از localStorage
    localStorage.removeItem('chatHistory');
    
    // پاک کردن پیام‌ها از صفحه
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer) {
        chatContainer.innerHTML = '';
    }
    
    console.log('🔄 تاریخچه با رفرش صفحه پاک شد');
}

document.addEventListener('DOMContentLoaded', function() {
    // رویدادهای چت
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    document.getElementById('userInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    
    // 🔥 پاک کردن تاریخچه هنگام لود صفحه (رفرش)
    clearOnRefresh();
    
    console.log('✅ چت‌بات آماده است!');
    console.log(`📊 تاریخچه موقت: ${getTemporaryHistory().length} پیام`);
});

async function sendMessage() {
    const now = Date.now();
    const timeSinceLastMessage = now - lastMessageTime;
    
    // بررسی تأخیر
    if (timeSinceLastMessage < MESSAGE_DELAY) {
        const remainingTime = (MESSAGE_DELAY - timeSinceLastMessage) / 1000;
        addMessage(`لطفاً ${remainingTime.toFixed(1)} ثانیه صبر کن... ⏳`, 'bot');
        return;
    }
    
    lastMessageTime = now;
    
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // غیرفعال کردن دکمه و اینپوت
    userInput.disabled = true;
    document.getElementById('sendButton').disabled = true;
    
    addMessage(message, 'user');
    userInput.value = '';
    
    try {
        // 🔥 اضافه کردن پیام کاربر به تاریخچه موقت
        addToTemporaryHistory('user', message);
        
        // نمایش حالت "در حال تایپ"
        const typingIndicator = addMessage('... در حال تایپ', 'bot');
        
        // 🔥 ارسال تاریخچه به سرور
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: message,
                history: getTemporaryHistory()
            })
        });
        
        // حذف نشانگر "در حال تایپ"
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        if (!response.ok) {
            throw new Error(`خطای سرور: ${response.status}`);
        }
        
        const data = await response.json();
        addMessage(data.reply, 'bot');
        
        // 🔥 اضافه کردن پاسخ ربات به تاریخچه موقت
        addToTemporaryHistory('assistant', data.reply);
        
    } catch (error) {
        addMessage('⚠️ خطا در ارتباط با سرور', 'bot');
        console.error('Error:', error);
    } finally {
        // فعال کردن مجدد
        userInput.disabled = false;
        document.getElementById('sendButton').disabled = false;
        
        // 🔥 برگرداندن focus به input (مهم!)
        userInput.focus();
        
        console.log('✅ آماده دریافت پیام جدید');
    }
}

// =============================================
// 🎨 مدیریت نمایش پیام‌ها
// =============================================

// در JS این رو برگردون به حالت ساده
function addMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = 'message ${sender}-message';
    
    if (typeof text === 'string' && (text.includes('<pre')  text.includes('code-container')  text.includes('inline-code'))) {
        messageDiv.innerHTML = addCopyButtonToCode(text);
    } else {
        messageDiv.innerHTML = text;
    }
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    saveChatHistory();
    
    return messageDiv;
}


// تابع کپی کردن کل پیام ربات
window.copyBotMessage = async function(button) {
    const messageDiv = button.parentElement;
    const messageContent = messageDiv.querySelector('.message-content');
    
    if (messageContent) {
        const textToCopy = messageContent.textContent || messageContent.innerText;
        
        try {
            await navigator.clipboard.writeText(textToCopy);
            
            // نمایش تأیید
            button.textContent = '✅';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.textContent = '📋';
                button.classList.remove('copied');
            }, 2000);
            
        } catch (err) {
            // روش fallback
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
// 📋 مدیریت کپی کردن کد
// =============================================

function addCopyButtonToCode(htmlContent) {
    let processedContent = htmlContent;
    
    // اگر قبلاً دکمه کپی ندارد، اضافه کن
    if (!processedContent.includes('copy-btn')) {
        // اضافه کردن دکمه کپی به کدهای بلوک
        processedContent = processedContent.replace(
            /<pre>([\s\S]*?)<\/pre>/g, 
            '<div class="code-container"><button class="copy-btn" onclick="copyCode(this)">📋</button><pre>$1</pre></div>'
        );
        
        // اضافه کردن دکمه کپی به کدهای با language
        processedContent = processedContent.replace(
            /<pre><code data-language="([^"]*)">([\s\S]*?)<\/code><\/pre>/g, 
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
        
        messages.forEach(msg => {const messageDiv = document.createElement('div');
            messageDiv.className = 'message ${msg.sender}-message';
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
        clearTemporaryHistory(); // 🔥 پاک کردن کامل تاریخچه
        document.getElementById('chatContainer').innerHTML = '';
        console.log('🗑️ تاریخچه چت پاک شد');
    }
}

// 🔥 پاک کردن تاریخچه موقت هنگام بستن تب/مرورگر
window.addEventListener('beforeunload', function() {
    console.log('🔄 پاک کردن تاریخچه موقت به دلیل بستن تب');
    // اینجا فقط sessionStorage پاک میشه، متغیر موقت خودبخود پاک میشه
    sessionStorage.removeItem('temporaryHistory');
});
