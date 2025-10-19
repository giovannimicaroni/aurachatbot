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

// Navigation
const navButtons = document.querySelectorAll('.nav-btn');
const pages = document.querySelectorAll('.page-content');
const menuToggle = document.getElementById('menuToggle');
const nav = document.getElementById('nav');

function navigateTo(pageId) {
    pages.forEach(page => page.classList.remove('active'));
    navButtons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(pageId).classList.add('active');
    document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
    
    if (nav.classList.contains('active')) {
        nav.classList.remove('active');
    }
}

navButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const page = btn.getAttribute('data-page');
        navigateTo(page);
    });
});

menuToggle.addEventListener('click', () => {
    nav.classList.toggle('active');
});

// Search functionality
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');

async function performSearch(query) {
    if (!query.trim()) {
        alert('Por favor, digite uma pergunta.');
        return;
    }

    sessionStorage.setItem('initialQuery', query);
    window.location.href = '/chat';
}

searchButton.addEventListener('click', () => {
    performSearch(searchInput.value);
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch(searchInput.value);
    }
});

// Contact form
document.getElementById('contactForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        message: document.getElementById('message').value
    };

    try {
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Erro ao enviar mensagem');
        }

        const data = await response.json();
        alert(data.message);
        e.target.reset();
        
    } catch (error) {
        console.error('Erro:', error);
        alert('Ocorreu um erro ao enviar sua mensagem. Tente novamente.');
    }
});

// Chatbot functionality (popup version on home page)
const chatButton = document.querySelector('.chat-button');
const chatContainer = document.getElementById('chatContainer');
const chatClose = document.getElementById('chatClose');
const chatInput = document.getElementById('chatInput');
const chatSend = document.getElementById('chatSend');
const chatMessages = document.getElementById('chatMessages');

chatButton.addEventListener('click', (e) => {
    e.preventDefault();
    chatContainer.classList.toggle('active');
    if (chatContainer.classList.contains('active')) {
        chatInput.focus();
    }
});

chatClose.addEventListener('click', () => {
    chatContainer.classList.remove('active');
});

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

// === Upload de Arquivos (popup) ===
const chatFileInput_popup = document.getElementById('chatFileInput');
const chatUploadBtn_popup = document.getElementById('chatUploadBtn');
const saveToDefaultCheckbox_popup = document.getElementById('saveToDefaultCheckbox');

if (chatUploadBtn_popup && chatFileInput_popup) {
    chatUploadBtn_popup.addEventListener('click', (e) => {
        e.preventDefault();
        chatFileInput_popup.click();
    });

    chatFileInput_popup.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        addMessage(`Enviando arquivo: ${file.name} ...`, true);

        const form = new FormData();
        form.append('file', file);
        form.append('save_to_default', saveToDefaultCheckbox_popup.checked ? '1' : '0');

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
            chatFileInput_popup.value = '';
        }
    });
}