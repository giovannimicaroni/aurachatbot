// Background animation
document.addEventListener('mousemove', function(e) {
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;
    
    const angle = Math.atan2(y - 0.5, x - 0.5) * (180 / Math.PI) + 180;
    
    const blue1 = Math.floor(0 + (x * 30));
    const blue2 = Math.floor(31 + (y * 40));
    const blue3 = Math.floor(63 + (x * 30));
    
    const red1 = Math.floor(255 - (x * 50));
    const red2 = Math.floor(0 + (y * 40));
    const red3 = Math.floor(0 + (x * 20));
    
    document.body.style.background = `linear-gradient(${angle}deg, 
        rgb(${blue1}, ${blue2}, ${blue3}) 0%, 
        rgb(${red1}, ${red2}, ${red3}) 100%)`;
});

const chatInput = document.getElementById('chatInput');
const chatSend = document.getElementById('chatSend');
const chatMessages = document.getElementById('chatMessages');
const clearBtn = document.getElementById('clearBtn');

function addMessage(text, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function sendChatMessage(message) {
    if (!message.trim()) return;

    addMessage(message, true);
    chatInput.value = '';
    chatSend.disabled = true;

    showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error('Erro ao enviar mensagem');
        }

        const data = await response.json();
        
        removeTypingIndicator();
        addMessage(data.response, false);
        
    } catch (error) {
        console.error('Erro:', error);
        removeTypingIndicator();
        addMessage('Desculpe, ocorreu um erro. Tente novamente.', false);
    } finally {
        chatSend.disabled = false;
        chatInput.focus();
    }
}

chatSend.addEventListener('click', () => {
    sendChatMessage(chatInput.value);
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendChatMessage(chatInput.value);
    }
});

clearBtn.addEventListener('click', async () => {
    if (confirm('Tem certeza que deseja limpar o histórico?')) {
        try {
            const response = await fetch('/api/clear-history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                chatMessages.innerHTML = '<div class="message bot">Olá! Bem-vindo ao Aura. Como posso ajudar você hoje? 😊</div>';
            }
        } catch (error) {
            console.error('Erro ao limpar histórico:', error);
        }
    }
});

window.addEventListener('DOMContentLoaded', () => {
    const initialQuery = sessionStorage.getItem('initialQuery');
    if (initialQuery) {
        sessionStorage.removeItem('initialQuery');
        sendChatMessage(initialQuery);
    } else {
        chatInput.focus();
    }
});

// === Upload de Arquivos ===
const chatFileInput = document.getElementById('chatFileInput');
const chatUploadBtn = document.getElementById('chatUploadBtn');
const saveToDefaultCheckbox = document.getElementById('saveToDefaultCheckbox');

chatUploadBtn.addEventListener('click', (e) => {
    e.preventDefault();
    chatFileInput.click();
});

chatFileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    addMessage(`Enviando arquivo: ${file.name} ...`, true);

    const form = new FormData();
    form.append('file', file);
    form.append('save_to_default', saveToDefaultCheckbox.checked ? '1' : '0');

    try {
        const resp = await fetch('/api/upload', {
            method: 'POST',
            body: form
        });

        if (!resp.ok) throw new Error('Falha no upload');

        const data = await resp.json();
        addMessage(data.message || `Arquivo ${file.name} enviado.`, false);
    } catch (err) {
        console.error('Erro upload:', err);
        addMessage(`Erro ao enviar ${file.name}.`, false);
    } finally {
        chatFileInput.value = '';
    }
});