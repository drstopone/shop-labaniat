async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // نمایش پیام کاربر
    addMessage(message, 'user');
    userInput.value = '';
    
    try {
        // ارسال به سرور
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // نمایش پاسخ ربات
        addMessage(data.reply, 'bot');
        
    } catch (error) {
        addMessage('⚠️ خطا در ارتباط با سرور', 'bot');
    }
}

function addMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = message + {sender}-message;
    messageDiv.textContent = text;
    chatContainer.appendChild(messageDiv);
    
    // اسکرول به پایین
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ارسال با دکمه Enter
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
