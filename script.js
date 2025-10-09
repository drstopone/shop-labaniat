async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // نمایش پیام کاربر
    addMessage(message, 'user');
    userInput.value = '';
    
    try {
        // نمایش حالت "در حال تایپ" (اختیاری)
        const typingIndicator = addMessage('... در حال تایپ', 'bot');
        
        // ارسال به سرور
        const response = await fetch('https://' + window.location.hostname + '/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        // حذف نشانگر "در حال تایپ" اگر وجود دارد
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        if (!response.ok) {
            throw new Error(`خطای سرور: ${response.status}`);
        }
        
        const data = await response.json();
        
        // نمایش پاسخ ربات
        addMessage(data.reply, 'bot');
        
    } catch (error) {
        addMessage('⚠️ خطا در ارتباط با سرور: ' + error.toString(), 'bot');
        console.error('Error:', error);
    }
}

function addMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = message ${sender}-message;
    messageDiv.textContent = text;
    chatContainer.appendChild(messageDiv);
    
    // اسکرول به پایین
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// ارسال با دکمه Enter
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// وقتی صفحه کاملاً لود شد
document.addEventListener('DOMContentLoaded', function() {
    console.log('چت‌بات آماده است!');
    addMessage('سلام! من چت‌بات هوش مصنوعی شما هستم. چطور می‌تونم کمک کنم؟', 'bot');
});
