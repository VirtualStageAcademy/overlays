class ChatOverlay extends OverlayClient {
    constructor(accessToken) {
        super('chat', accessToken);
        this.messageContainer = document.querySelector('.messages-wrapper');
    }

    handleMessage(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'chat') {
            this.addChatMessage(data);
        }
    }

    addChatMessage(data) {
        const messageEl = document.createElement('div');
        messageEl.classList.add('chat-message');
        messageEl.innerHTML = `
            <span class="sender">${this.escapeHtml(data.sender)}</span>
            <span class="content">${this.escapeHtml(data.content)}</span>
        `;
        
        this.messageContainer.appendChild(messageEl);
        this.cleanupOldMessages();
    }

    cleanupOldMessages() {
        const messages = this.messageContainer.children;
        while (messages.length > 5) {
            messages[0].remove();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('token');
    
    if (accessToken) {
        const chat = new ChatOverlay(accessToken);
        chat.connect();
    }
}); 