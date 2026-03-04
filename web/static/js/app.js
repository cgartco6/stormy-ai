document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const moodIndicator = document.getElementById('mood-indicator');

    let sessionId = generateSessionId();
    let isTyping = false;

    // Check for Web Speech API support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceBtn.disabled = true;
        voiceBtn.title = 'Voice input not supported in this browser';
    }

    // Generate a random session ID (or use stored)
    function generateSessionId() {
        let id = localStorage.getItem('stormy_session');
        if (!id) {
            id = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('stormy_session', id);
        }
        return id;
    }

    // Add a message to the chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? '👤' : '⛈️';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = text;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Show typing indicator
    function showTyping() {
        if (isTyping) return;
        isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message stormy typing';
        typingDiv.id = 'typing-indicator';
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = '⛈️';
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = 'Stormy is thinking...';
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(bubble);
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Remove typing indicator
    function hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
        isTyping = false;
    }

    // Send message to backend
    async function sendMessage(message) {
        showTyping();
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, session_id: sessionId })
            });
            const data = await response.json();
            hideTyping();
            addMessage(data.response, 'stormy');
            // Update mood indicator based on response? (optional)
            // For now, just rotate through some emojis
            const moods = ['😏', '😈', '😘', '😤', '🤬', '😇'];
            moodIndicator.textContent = moods[Math.floor(Math.random() * moods.length)];
        } catch (error) {
            hideTyping();
            addMessage('Oops, something went wrong. Try again.', 'stormy');
        }
    }

    // Handle send button click
    sendBtn.addEventListener('click', () => {
        const message = messageInput.value.trim();
        if (message === '') return;
        addMessage(message, 'user');
        messageInput.value = '';
        sendMessage(message);
    });

    // Handle Enter key
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });

    // Voice input
    voiceBtn.addEventListener('click', () => {
        if (!SpeechRecognition) return;
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.start();

        recognition.onresult = (event) => {
            const speechText = event.results[0][0].transcript;
            messageInput.value = speechText;
            // Optionally auto-send
            // sendBtn.click();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
        };
    });

    // Initial welcome message already in HTML
});
