from app import db
from datetime import datetime
import json

class TypingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.DateTime, default=datetime.utcnow)
    text_content = db.Column(db.Text, nullable=False)
    total_time = db.Column(db.Float, nullable=False)  # in seconds
    total_keystrokes = db.Column(db.Integer, nullable=False)
    backspace_count = db.Column(db.Integer, default=0)
    avg_keystroke_speed = db.Column(db.Float, nullable=False)  # keystrokes per minute
    pause_count = db.Column(db.Integer, default=0)
    avg_pause_duration = db.Column(db.Float, default=0.0)  # in seconds
    burst_count = db.Column(db.Integer, default=0)
    slow_phases = db.Column(db.Integer, default=0)
    
    # Mood analysis results
    focus_score = db.Column(db.Float, default=0.0)  # 0-100
    stress_score = db.Column(db.Float, default=0.0)  # 0-100
    confidence_score = db.Column(db.Float, default=0.0)  # 0-100
    dominant_mood = db.Column(db.String(50), default='neutral')
    
    # Raw keystroke data as JSON
    keystroke_data = db.Column(db.Text)  # JSON string of timing data

    def __repr__(self):
        return f'<TypingSession {self.id} - {self.session_date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_date': self.session_date.isoformat(),
            'text_content': self.text_content,
            'total_time': self.total_time,
            'total_keystrokes': self.total_keystrokes,
            'backspace_count': self.backspace_count,
            'avg_keystroke_speed': self.avg_keystroke_speed,
            'pause_count': self.pause_count,
            'avg_pause_duration': self.avg_pause_duration,
            'burst_count': self.burst_count,
            'slow_phases': self.slow_phases,
            'focus_score': self.focus_score,
            'stress_score': self.stress_score,
            'confidence_score': self.confidence_score,
            'dominant_mood': self.dominant_mood
        }

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    target_wpm = db.Column(db.Integer, default=40)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Challenge {self.id} - {self.difficulty}>'