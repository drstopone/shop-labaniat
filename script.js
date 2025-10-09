async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // نمایش پیام کاربر
    addMessage(message, 'user');
    userInput.value = '';
    
    // نمایش حالت "در حال تایپ..."
    const typingIndicator = addMessage('... در حال تایپ', 'bot');
    
    try {
        // ارسال به سرور - استفاده از آدرس کامل
        const response = await fetch('https://' + window.location.hostname + '/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        // حذف نشانگر "در حال تایپ"
        typingIndicator.remove();
        
        if (!response.ok) {
            throw new Error(`خطای سرور: ${response.status}`);
        }
        
        const data = await response.json();
        
        // نمایش پاسخ ربات
        addMessage(data.reply, 'bot');
        
    } catch (error) {
        // حذف نشانگر "در حال تایپ" در صورت خطا
        typingIndicator.remove();
        addMessage('⚠️ خطا در ارتباط با سرور: ' + error.message, 'bot');
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
    
    return messageDiv; // بازگشت عنصر برای مدیریت بهتر
}

// ارسال با دکمه Enter
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// همچنین مطمئن شو المنت‌ها در DOM موجود هستند
document.addEventListener('DOMContentLoaded', function() {
    console.log('صفحه آماده است!');
});
