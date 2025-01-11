class CountdownOverlay {
    constructor() {
        this.minutesEl = document.getElementById('minutes');
        this.secondsEl = document.getElementById('seconds');
        this.timerEl = document.querySelector('.timer');
        this.beepSound = document.getElementById('beep');
        this.timeLeft = 0;
        this.originalTime = 0;
        this.interval = null;
        this.isPaused = false;
        this.soundEnabled = true;
        this.initialize();
    }

    initialize() {
        const params = new URLSearchParams(window.location.search);
        
        // Get duration
        let duration = params.get('duration') || '5';
        if (duration === '30s') duration = '0.5';
        if (duration === '10s') duration = '0.167';
        
        // Get theme
        const theme = params.get('theme') || 'default';
        this.timerEl.classList.add(theme);
        
        // Get sound preference
        this.soundEnabled = params.get('sound') !== 'off';
        
        // Convert to milliseconds
        this.timeLeft = Math.floor(parseFloat(duration) * 60);
        this.originalTime = this.timeLeft;
        
        // Validate duration
        if (this.timeLeft > 5400) this.timeLeft = 5400;
        if (this.timeLeft < 10) this.timeLeft = 10;

        this.setupKeyboardControls();
        this.updateDisplay();
        this.startCountdown();
    }

    setupKeyboardControls() {
        document.addEventListener('keypress', (e) => {
            switch(e.key.toLowerCase()) {
                case ' ':
                    this.togglePause();
                    break;
                case 'r':
                    this.reset();
                    break;
                case 's':
                    this.toggleSound();
                    break;
            }
        });
    }

    togglePause() {
        this.isPaused = !this.isPaused;
        this.timerEl.classList.toggle('paused', this.isPaused);
        
        if (this.isPaused) {
            clearInterval(this.interval);
        } else {
            this.startCountdown();
        }
    }

    reset() {
        this.timeLeft = this.originalTime;
        this.updateDisplay();
        if (!this.isPaused) {
            clearInterval(this.interval);
            this.startCountdown();
        }
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
    }

    startCountdown() {
        if (this.interval) clearInterval(this.interval);
        
        this.interval = setInterval(() => {
            if (!this.isPaused) {
                this.timeLeft--;
                this.updateDisplay();

                if (this.timeLeft <= 0) {
                    this.endCountdown();
                } else if (this.timeLeft <= 10 && this.soundEnabled) {
                    this.beepSound.play().catch(() => {});
                }
            }
        }, 1000);
    }

    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;

        this.minutesEl.textContent = minutes.toString().padStart(2, '0');
        this.secondsEl.textContent = seconds.toString().padStart(2, '0');

        // Update styles based on time remaining
        this.updateStyles();
    }

    updateStyles() {
        this.timerEl.classList.remove('warning', 'danger');

        if (this.timeLeft <= 10) {
            this.timerEl.classList.add('danger');
            this.pulseAnimation();
        } else if (this.timeLeft <= 30) {
            this.timerEl.classList.add('warning');
        }
    }

    pulseAnimation() {
        if (!this.timerEl.classList.contains('ending')) {
            this.timerEl.classList.add('ending');
            setTimeout(() => {
                this.timerEl.classList.remove('ending');
            }, 500);
        }
    }

    endCountdown() {
        clearInterval(this.interval);
        this.timerEl.style.animation = 'fadeOut 1s forwards';
        
        // Optional: Notify OBS that countdown is complete
        if (window.obsstudio) {
            setTimeout(() => {
                window.obsstudio.hideOverlay();
            }, 1000);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new CountdownOverlay();
}); 