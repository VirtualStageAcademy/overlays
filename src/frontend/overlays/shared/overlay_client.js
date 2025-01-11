class OverlayClient {
    /**
     * Handles overlay WebSocket connections and events
     * 1. Connects to WebSocket server
     * 2. Handles Zoom events
     * 3. Updates overlay UI
     */
    constructor(overlayType, accessToken) {
        this.overlayType = overlayType;
        this.accessToken = accessToken;
        this.ws = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    async connect() {
        try {
            // Connect to WebSocket with auth token
            const wsUrl = `${WS_BASE_URL}/overlay/${this.overlayType}`;
            this.ws = new WebSocket(wsUrl);
            
            // Add auth header
            this.ws.addListener('open', () => {
                this.ws.send(JSON.stringify({
                    type: 'auth',
                    token: this.accessToken
                }));
            });

            // Setup event handlers
            this.ws.addEventListener('message', this.handleMessage.bind(this));
            this.ws.addEventListener('close', this.handleDisconnect.bind(this));
            this.ws.addEventListener('error', this.handleError.bind(this));

            this.connected = true;
            console.log(`Connected to ${this.overlayType} overlay`);

        } catch (error) {
            console.error('Connection failed:', error);
            this.handleDisconnect();
        }
    }

    async handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'chat':
                    this.updateChatOverlay(data);
                    break;
                case 'reaction':
                    this.updateReactionOverlay(data);
                    break;
                case 'participants':
                    this.updateParticipantsOverlay(data);
                    break;
                case 'initial_state':
                    this.initializeOverlay(data);
                    break;
                default:
                    console.log('Unknown event type:', data.type);
            }

        } catch (error) {
            console.error('Error handling message:', error);
        }
    }

    updateChatOverlay(data) {
        if (this.overlayType !== 'chat') return;
        
        const chatContainer = document.getElementById('chat-container');
        const messageEl = document.createElement('div');
        messageEl.classList.add('chat-message');
        messageEl.innerHTML = `
            <span class="sender">${data.sender}</span>
            <span class="content">${data.content}</span>
        `;
        chatContainer.appendChild(messageEl);
    }

    updateReactionOverlay(data) {
        if (this.overlayType !== 'reaction') return;
        
        const reactionEl = document.createElement('div');
        reactionEl.classList.add('reaction');
        reactionEl.innerHTML = data.content;
        
        document.body.appendChild(reactionEl);
        
        // Animate and remove after animation
        setTimeout(() => reactionEl.remove(), 3000);
    }

    updateParticipantsOverlay(data) {
        if (this.overlayType !== 'participants') return;
        
        const participantsList = document.getElementById('participants-list');
        participantsList.innerHTML = data.participants
            .map(p => `<div class="participant">${p.name}</div>`)
            .join('');
    }

    initializeOverlay(data) {
        console.log('Initializing overlay with:', data);
        // Set initial state based on overlay type
    }

    async handleDisconnect() {
        this.connected = false;
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
            setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    handleError(error) {
        console.error('WebSocket error:', error);
    }

    cleanup() {
        if (this.ws) {
            this.ws.close();
        }
        this.connected = false;
    }
}

// Usage example:
const initOverlay = async () => {
    const params = new URLSearchParams(window.location.search);
    const overlayType = params.get('type');
    const accessToken = params.get('token');

    if (!overlayType || !accessToken) {
        console.error('Missing required parameters');
        return;
    }

    const overlay = new OverlayClient(overlayType, accessToken);
    await overlay.connect();
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initOverlay); 