// Typing Pattern Tracker
class TypingTracker {
    constructor() {
        this.keystrokeData = [];
        this.startTime = null;
        this.isTracking = false;
        this.correctionCount = 0;
        this.lastKeyTime = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        const typingArea = document.getElementById('typingArea');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const clearBtn = document.getElementById('clearBtn');
        const loadChallengeBtn = document.getElementById('loadChallenge');

        // Typing area events
        typingArea.addEventListener('keydown', (e) => this.handleKeyDown(e));
        typingArea.addEventListener('keyup', (e) => this.handleKeyUp(e));
        typingArea.addEventListener('input', (e) => this.handleInput(e));

        // Button events
        analyzeBtn.addEventListener('click', () => this.analyzeTyping());
        clearBtn.addEventListener('click', () => this.clearAll());
        loadChallengeBtn.addEventListener('click', () => this.loadChallenge());

        // Start timer and tracking when user starts typing
        typingArea.addEventListener('input', () => {
            if (!this.isTracking && typingArea.value.length > 0) {
                this.startTracking();
            }
            this.updateLiveStats();
        });
    }

    handleKeyDown(event) {
        if (!this.isTracking) return;

        const timestamp = Date.now();
        const key = event.key;

        // Track backspace for corrections
        if (key === 'Backspace') {
            this.correctionCount++;
        }

        // Record keystroke data
        this.keystrokeData.push({
            key: key,
            timestamp: timestamp,
            type: 'keydown'
        });

        this.lastKeyTime = timestamp;
    }

    handleKeyUp(event) {
        if (!this.isTracking) return;

        const timestamp = Date.now();
        this.keystrokeData.push({
            key: event.key,
            timestamp: timestamp,
            type: 'keyup'
        });
    }

    handleInput(event) {
        this.updateLiveStats();
        
        // Enable analyze button if there's content
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.disabled = event.target.value.trim().length === 0;
    }

    startTracking() {
        this.startTime = Date.now();
        this.isTracking = true;
        this.keystrokeData = [];
        this.correctionCount = 0;
        
        // Start timer display
        this.startTimer();
    }

    startTimer() {
        const timerElement = document.getElementById('timer');
        const updateTimer = () => {
            if (!this.isTracking) return;
            
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            setTimeout(updateTimer, 1000);
        };
        updateTimer();
    }

    updateLiveStats() {
        const typingArea = document.getElementById('typingArea');
        const text = typingArea.value;
        
        // Update character and word counts
        document.getElementById('charCount').textContent = text.length;
        document.getElementById('wordCount').textContent = text.trim() ? text.trim().split(/\s+/).length : 0;
        document.getElementById('correctionCount').textContent = this.correctionCount;

        // Calculate and display live WPM
        if (this.startTime && text.trim().length > 0) {
            const elapsed = (Date.now() - this.startTime) / 1000 / 60; // minutes
            const words = text.trim().split(/\s+/).length;
            const wpm = Math.round(words / elapsed);
            document.getElementById('liveWpm').textContent = isFinite(wpm) ? wpm : 0;
        }
    }

    async analyzeTyping() {
        const typingArea = document.getElementById('typingArea');
        const text = typingArea.value.trim();
        
        if (!text || !this.isTracking) {
            alert('Please type some text first!');
            return;
        }

        this.isTracking = false;
        const totalTime = (Date.now() - this.startTime) / 1000; // seconds

        // Prepare data for analysis
        const analysisData = {
            text: text,
            totalTime: totalTime,
            keystrokeData: this.keystrokeData
        };

        try {
            // Show loading state
            const analyzeBtn = document.getElementById('analyzeBtn');
            analyzeBtn.textContent = 'Analyzing...';
            analyzeBtn.disabled = true;

            // Send data to backend for analysis
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(analysisData)
            });

            const result = await response.json();
            
            if (result.success) {
                this.displayResults(result.analysis, result.moodFeedback);
            } else {
                throw new Error(result.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            alert('Error analyzing typing patterns. Please try again.');
        } finally {
            // Reset button
            const analyzeBtn = document.getElementById('analyzeBtn');
            analyzeBtn.textContent = 'Analyze Typing';
            analyzeBtn.disabled = false;
        }
    }

    displayResults(analysis, moodFeedback) {
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Display mood feedback
        document.getElementById('moodTitle').textContent = moodFeedback.title;
        document.getElementById('moodMessage').textContent = moodFeedback.message;
        
        const suggestionsContainer = document.getElementById('moodSuggestions');
        suggestionsContainer.innerHTML = '';
        moodFeedback.suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'flex items-start space-x-2';
            div.innerHTML = `
                <span class="text-green-500 mt-1">✓</span>
                <span class="text-gray-700">${suggestion}</span>
            `;
            suggestionsContainer.appendChild(div);
        });

        // Display mood scores
        this.updateScoreDisplay('focus', analysis.focus_score);
        this.updateScoreDisplay('stress', analysis.stress_score);
        this.updateScoreDisplay('confidence', analysis.confidence_score);

        // Display detailed metrics
        document.getElementById('avgSpeed').textContent = `${Math.round(analysis.avg_keystroke_speed)} WPM`;
        document.getElementById('corrections').textContent = analysis.backspace_count;
        document.getElementById('pauses').textContent = analysis.pause_count;
        document.getElementById('bursts').textContent = analysis.burst_count;
    }

    updateScoreDisplay(type, score) {
        const scoreElement = document.getElementById(`${type}Score`);
        const barElement = document.getElementById(`${type}Bar`);
        
        scoreElement.textContent = Math.round(score);
        barElement.style.width = `${score}%`;
        
        // Add animation
        barElement.style.transition = 'width 1s ease-in-out';
    }

    async loadChallenge() {
        try {
            const response = await fetch('/api/challenge');
            const challenge = await response.json();
            
            // Display challenge
            document.getElementById('challengeContent').classList.remove('hidden');
            document.getElementById('challengeText').textContent = challenge.challengeText;
            document.getElementById('targetWpm').textContent = `${challenge.targetWpm} WPM`;
            
            const difficultyElement = document.getElementById('difficulty');
            difficultyElement.textContent = challenge.difficulty.charAt(0).toUpperCase() + challenge.difficulty.slice(1);
            
            // Update difficulty styling
            const difficultyColors = {
                'easy': 'bg-green-100 text-green-800',
                'medium': 'bg-yellow-100 text-yellow-800',
                'hard': 'bg-red-100 text-red-800'
            };
            difficultyElement.className = `px-2 py-1 rounded-full text-xs font-medium ${difficultyColors[challenge.difficulty]}`;
            
        } catch (error) {
            console.error('Error loading challenge:', error);
            alert('Error loading challenge. Please try again.');
        }
    }

    clearAll() {
        // Reset all data
        document.getElementById('typingArea').value = '';
        document.getElementById('timer').textContent = '00:00';
        document.getElementById('liveWpm').textContent = '0';
        document.getElementById('charCount').textContent = '0';
        document.getElementById('wordCount').textContent = '0';
        document.getElementById('correctionCount').textContent = '0';
        
        // Hide results
        document.getElementById('resultsSection').classList.add('hidden');
        
        // Reset tracking
        this.keystrokeData = [];
        this.startTime = null;
        this.isTracking = false;
        this.correctionCount = 0;
        
        // Disable analyze button
        document.getElementById('analyzeBtn').disabled = true;
    }
}

// Initialize tracker when page loads
document.addEventListener('DOMContentLoaded', function() {
    new TypingTracker();
});