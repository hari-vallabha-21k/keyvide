# Typing Pattern Analyzer

A Flask web application that monitors user typing patterns to provide insightful feedback on focus, stress, and confidence levels through heuristic-based analysis.

## Features

### Core Functionality
- **Real-time Typing Analysis**: Captures keystroke timing, pauses, corrections, and typing bursts
- **Heuristic Mood Analysis**: Interprets typing patterns into focus, stress, and confidence scores
- **Interactive Dashboard**: Visualizes typing trends and performance metrics with Chart.js
- **Daily Challenges**: Personalized typing challenges based on user performance
- **Data Export**: Export typing history as CSV files
- **Session Persistence**: SQLite database stores all typing sessions

### Heuristic Logic
The application uses sophisticated heuristics to analyze typing patterns:

- **Focus Score**: Based on correction rate, pause frequency, and rhythm consistency
  - High corrections + many pauses = Low focus
  - Consistent rhythm + low corrections = High focus

- **Stress Score**: Derived from pause patterns and typing inconsistency
  - Long pauses + erratic rhythm = High stress
  - Extreme speeds (too fast/slow) = Elevated stress

- **Confidence Score**: Calculated from typing bursts and accuracy
  - Typing bursts + low corrections = High confidence
  - Consistent moderate speed = Good confidence

## Technical Stack

- **Backend**: Flask 2.3.3 with SQLAlchemy
- **Database**: SQLite for session persistence
- **Frontend**: Tailwind CSS for responsive design
- **Visualization**: Chart.js for interactive analytics
- **JavaScript**: Real-time keystroke tracking and analysis

## Installation & Setup

1. **Clone and Navigate**:
   ```bash
   cd /workspace/flask_template
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   python run.py
   ```

4. **Access Application**:
   - Main Interface: http://localhost:5000
   - Dashboard: http://localhost:5000/dashboard

## Project Structure

```
flask_template/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── routes.py                # API endpoints
│   ├── typing_analyzer.py       # Heuristic analysis engine
│   ├── templates/
│   │   ├── index.html          # Main typing interface
│   │   └── dashboard.html      # Analytics dashboard
│   └── static/
│       ├── js/
│       │   └── typing_tracker.js # Frontend typing logic
│       └── css/
│           └── styles.css      # Custom styling
├── config.py                   # Flask configuration
├── requirements.txt            # Python dependencies
├── run.py                     # Application entry point
└── README.md                  # Project documentation
```

## API Endpoints

- `GET /` - Main typing interface
- `GET /dashboard` - Analytics dashboard
- `POST /api/analyze` - Analyze typing session
- `GET /api/sessions` - Get recent sessions
- `GET /api/stats` - Get overall statistics
- `GET /api/challenge` - Get daily challenge
- `GET /api/export` - Export data as CSV
- `GET /health` - Health check

## Usage Guide

### 1. Typing Test
- Navigate to the main page
- Optionally load a daily challenge for guided practice
- Start typing in the text area
- Real-time metrics (WPM, time, corrections) update automatically
- Click "Analyze Typing" to get mood feedback and detailed insights

### 2. Dashboard
- View overall statistics and trends
- Interactive charts show 7-day mood patterns
- Recent sessions table with exportable data
- Performance tracking over time

### 3. Daily Challenges
- Personalized challenges based on recent performance
- Target WPM adjusts to user's skill level
- Difficulty scaling (easy/medium/hard)

## Heuristic Analysis Details

### Keystroke Metrics Captured
- **Timing**: Precise keydown/keyup timestamps
- **Corrections**: Backspace frequency and patterns
- **Pauses**: Intervals between keystrokes
- **Bursts**: Rapid typing sequences
- **Rhythm**: Consistency of typing speed

### Mood Calculation Logic

**Focus Score (0-100)**:
```python
base_score = 70
- correction_penalty = correction_rate * 2
- pause_penalty = min(pause_count * 5, 30)
+ consistency_bonus = rhythm_consistency * 0.3
```

**Stress Score (0-100)**:
```python
base_score = 30
+ pause_stress = avg_pause_duration * 10
+ inconsistency_stress = (100 - rhythm_consistency) * 0.5
+ speed_extremes = 20 if speed < 20 or speed > 120
```

**Confidence Score (0-100)**:
```python
base_score = 50
+ burst_bonus = burst_count * 15
+ accuracy_bonus = max(0, 10 - correction_rate) * 3
+ rhythm_bonus = rhythm_consistency * 0.4
+ speed_bonus = 15 if 40 <= speed <= 80
```

## Database Schema

### TypingSession Table
- Session metadata (date, duration, text content)
- Keystroke metrics (speed, corrections, pauses, bursts)
- Mood analysis results (focus, stress, confidence scores)
- Raw keystroke data (JSON format)

### Challenge Table
- Challenge texts and difficulty levels
- Target WPM and creation dates

## Deployment Notes

The application is designed for easy deployment on platforms like:
- **Heroku**: Use Gunicorn WSGI server
- **Vercel**: Serverless deployment with adaptations
- **Local/VPS**: Direct Flask development server

## Future Enhancements

- Machine learning integration for improved pattern recognition
- Multi-user support with authentication
- Advanced visualization with D3.js
- Mobile app companion
- Integration with productivity tools
- Biometric correlation (heart rate, stress sensors)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create Pull Request

## License

This project is open source and available under the MIT License.

---

**Demo Video**: Create a 60-90 second video showcasing:
1. Typing interface with real-time metrics
2. Analysis results with mood feedback
3. Dashboard with trend visualization
4. Challenge system demonstration

**Live Demo**: Access the running application to test all features and experience the typing pattern analysis in real-time.