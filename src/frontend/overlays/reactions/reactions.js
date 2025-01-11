class ReactionsOverlay extends OverlayClient {
    constructor(accessToken) {
        super('reactions', accessToken);
        this.container = document.getElementById('reactions-container');
        this.animations = ['float', 'spin'];
    }

    handleMessage(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'reaction') {
            this.showReaction(data.content);
        }
    }

    showReaction(emoji) {
        const reaction = document.createElement('div');
        reaction.classList.add('reaction');
        reaction.classList.add(this.getRandomAnimation());
        reaction.style.right = `${this.getRandomPosition()}px`;
        reaction.textContent = emoji;
        
        this.container.appendChild(reaction);
        
        // Remove after animation
        setTimeout(() => reaction.remove(), 3000);
    }

    getRandomAnimation() {
        return this.animations[Math.floor(Math.random() * this.animations.length)];
    }

    getRandomPosition() {
        return Math.floor(Math.random() * 80) + 20;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('token');
    
    if (accessToken) {
        const reactions = new ReactionsOverlay(accessToken);
        reactions.connect();
    }
}); 