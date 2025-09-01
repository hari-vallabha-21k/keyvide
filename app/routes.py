from flask import Blueprint, jsonify, request, render_template, send_file
from app import db
from app.models import TypingSession, Challenge
from app.typing_analyzer import TypingAnalyzer
import json
import csv
import io
from datetime import datetime, timedelta
import random

main_bp = Blueprint('main', __name__)
analyzer = TypingAnalyzer()

@main_bp.route('/')
def index():
    """Main typing interface."""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Analytics dashboard."""
    return render_template('dashboard.html')

@main_bp.route('/api/analyze', methods=['POST'])
def analyze_typing():
    """Analyze typing session and store results."""
    try:
        data = request.get_json()
        
        # Extract data from request
        text_content = data.get('text', '')
        total_time = data.get('totalTime', 0)
        keystroke_data = data.get('keystrokeData', [])
        
        if not text_content or total_time <= 0:
            return jsonify({'error': 'Invalid data provided'}), 400
        
        # Perform analysis
        analysis = analyzer.analyze_typing_session(keystroke_data, text_content, total_time)
        
        # Create new typing session record
        session = TypingSession(
            text_content=text_content,
            total_time=total_time,
            total_keystrokes=analysis['total_keystrokes'],
            backspace_count=analysis['backspace_count'],
            avg_keystroke_speed=analysis['avg_keystroke_speed'],
            pause_count=analysis['pause_count'],
            avg_pause_duration=analysis['avg_pause_duration'],
            burst_count=analysis['burst_count'],
            slow_phases=analysis['slow_phases'],
            focus_score=analysis['focus_score'],
            stress_score=analysis['stress_score'],
            confidence_score=analysis['confidence_score'],
            dominant_mood=analysis['dominant_mood'],
            keystroke_data=json.dumps(keystroke_data)
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Return analysis results
        return jsonify({
            'success': True,
            'sessionId': session.id,
            'analysis': analysis,
            'moodFeedback': _generate_mood_feedback(analysis)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/sessions')
def get_sessions():
    """Get recent typing sessions."""
    try:
        limit = request.args.get('limit', 10, type=int)
        sessions = TypingSession.query.order_by(TypingSession.session_date.desc()).limit(limit).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/stats')
def get_stats():
    """Get overall typing statistics."""
    try:
        # Get sessions from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sessions = TypingSession.query.filter(
            TypingSession.session_date >= thirty_days_ago
        ).all()
        
        if not recent_sessions:
            return jsonify({
                'totalSessions': 0,
                'avgSpeed': 0,
                'avgFocus': 50,
                'avgStress': 50,
                'avgConfidence': 50,
                'moodTrends': []
            })
        
        # Calculate averages
        total_sessions = len(recent_sessions)
        avg_speed = sum(s.avg_keystroke_speed for s in recent_sessions) / total_sessions
        avg_focus = sum(s.focus_score for s in recent_sessions) / total_sessions
        avg_stress = sum(s.stress_score for s in recent_sessions) / total_sessions
        avg_confidence = sum(s.confidence_score for s in recent_sessions) / total_sessions
        
        # Generate mood trends (last 7 days)
        mood_trends = []
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=i)
            day_sessions = [s for s in recent_sessions if s.session_date.date() == date.date()]
            
            if day_sessions:
                avg_day_focus = sum(s.focus_score for s in day_sessions) / len(day_sessions)
                avg_day_stress = sum(s.stress_score for s in day_sessions) / len(day_sessions)
                avg_day_confidence = sum(s.confidence_score for s in day_sessions) / len(day_sessions)
            else:
                avg_day_focus = avg_day_stress = avg_day_confidence = 0
            
            mood_trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'focus': round(avg_day_focus, 1),
                'stress': round(avg_day_stress, 1),
                'confidence': round(avg_day_confidence, 1)
            })
        
        return jsonify({
            'totalSessions': total_sessions,
            'avgSpeed': round(avg_speed, 1),
            'avgFocus': round(avg_focus, 1),
            'avgStress': round(avg_stress, 1),
            'avgConfidence': round(avg_confidence, 1),
            'moodTrends': list(reversed(mood_trends))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/export')
def export_data():
    """Export typing history as CSV."""
    try:
        sessions = TypingSession.query.order_by(TypingSession.session_date.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Text Length', 'Total Time (s)', 'Keystrokes', 'Backspaces',
            'Speed (WPM)', 'Pauses', 'Avg Pause (s)', 'Bursts', 'Slow Phases',
            'Focus Score', 'Stress Score', 'Confidence Score', 'Dominant Mood'
        ])
        
        # Write data
        for session in sessions:
            writer.writerow([
                session.session_date.strftime('%Y-%m-%d %H:%M:%S'),
                len(session.text_content),
                session.total_time,
                session.total_keystrokes,
                session.backspace_count,
                session.avg_keystroke_speed,
                session.pause_count,
                session.avg_pause_duration,
                session.burst_count,
                session.slow_phases,
                session.focus_score,
                session.stress_score,
                session.confidence_score,
                session.dominant_mood
            ])
        
        # Prepare file for download
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'typing_history_{datetime.now().strftime("%Y%m%d")}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/challenge')
def get_challenge():
    """Get a daily typing challenge."""
    try:
        # Simple challenge generation based on user's recent performance
        recent_sessions = TypingSession.query.order_by(
            TypingSession.session_date.desc()
        ).limit(5).all()
        
        if recent_sessions:
            avg_speed = sum(s.avg_keystroke_speed for s in recent_sessions) / len(recent_sessions)
            target_wpm = max(30, int(avg_speed * 1.1))  # 10% improvement target
        else:
            target_wpm = 40  # Default target
        
        # Sample challenge texts
        challenge_texts = [
            "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet and is perfect for typing practice.",
            "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole filled with the ends of worms and an oozy smell.",
            "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness.",
            "To be or not to be, that is the question. Whether 'tis nobler in the mind to suffer the slings and arrows of outrageous fortune.",
            "All happy families are alike; each unhappy family is unhappy in its own way. Everything was in confusion in the Oblonskys' house."
        ]
        
        challenge_text = random.choice(challenge_texts)
        difficulty = 'easy' if target_wpm < 40 else 'medium' if target_wpm < 60 else 'hard'
        
        return jsonify({
            'challengeText': challenge_text,
            'targetWpm': target_wpm,
            'difficulty': difficulty,
            'date': datetime.now().strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _generate_mood_feedback(analysis):
    """Generate personalized feedback based on analysis results."""
    dominant_mood = analysis['dominant_mood']
    focus_score = analysis['focus_score']
    stress_score = analysis['stress_score']
    confidence_score = analysis['confidence_score']
    
    feedback = {
        'title': '',
        'message': '',
        'suggestions': []
    }
    
    if dominant_mood == 'focus':
        feedback['title'] = '🎯 Great Focus!'
        feedback['message'] = f'You\'re showing excellent concentration with a focus score of {focus_score:.0f}/100.'
        feedback['suggestions'] = [
            'Keep up the consistent typing rhythm',
            'Your low correction rate shows good accuracy',
            'Consider taking short breaks to maintain this level'
        ]
    elif dominant_mood == 'confidence':
        feedback['title'] = '💪 High Confidence!'
        feedback['message'] = f'Your typing shows strong confidence with a score of {confidence_score:.0f}/100.'
        feedback['suggestions'] = [
            'Your typing bursts indicate good flow',
            'Low correction rate shows self-assurance',
            'Try challenging yourself with faster targets'
        ]
    elif dominant_mood == 'stress':
        feedback['title'] = '😰 Elevated Stress Detected'
        feedback['message'] = f'Your typing patterns suggest some stress (score: {stress_score:.0f}/100).'
        feedback['suggestions'] = [
            'Take a few deep breaths before typing',
            'Try to maintain a steady rhythm',
            'Consider shorter typing sessions'
        ]
    else:
        feedback['title'] = '😌 Balanced State'
        feedback['message'] = 'Your typing shows a balanced emotional state.'
        feedback['suggestions'] = [
            'Good overall typing balance',
            'Consider focusing on speed or accuracy',
            'Regular practice will help improve consistency'
        ]
    
    return feedback

@main_bp.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})