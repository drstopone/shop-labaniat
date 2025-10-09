async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    addMessage(message, 'user');
    userInput.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error(`خطای سرور: ${response.status}`);
        }
        
        const data = await response.json();
        addMessage(data.reply, 'bot');
        
    } catch (error) {
        addMessage('⚠️ خطا در ارتباط با سرور', 'bot');
        console.error('Error:', error);
    }
}

function addMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ${sender}-message';
    
    // همیشه از innerHTML استفاده کن - مهم!
    messageDiv.innerHTML = text;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // ذخیره در تاریخچه
    //setTimeout(saveChatHistory, 100);
    
    return messageDiv;
}

// اضافه کردن event listener برای دکمه‌های کپی
document.addEventListener('DOMContentLoaded', function() {
    // این تابع رو به صورت global تعریف کن
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
    };
});


document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('چت‌بات آماده است!');
});

// اضافه کردن event listener به دکمه ارسال
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    console.log('چت‌بات آماده است!');
});
