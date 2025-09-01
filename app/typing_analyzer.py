import json
from statistics import mean, median
from typing import Dict, List, Tuple


class TypingAnalyzer:
    """
    Heuristic-based typing pattern analyzer that interprets typing behavior
    into focus, stress, and confidence metrics.
    """
    
    def __init__(self):
        # Thresholds for analysis (adjustable based on testing)
        self.FAST_KEYSTROKE_THRESHOLD = 120  # WPM
        self.SLOW_KEYSTROKE_THRESHOLD = 30   # WPM
        self.LONG_PAUSE_THRESHOLD = 2.0      # seconds
        self.BURST_MIN_SPEED = 100           # WPM
        self.BURST_MIN_DURATION = 3          # keystrokes
        
    def analyze_typing_session(self, keystroke_data: List[Dict], text_content: str, total_time: float) -> Dict:
        """
        Main analysis function that processes keystroke data and returns comprehensive metrics.
        
        Args:
            keystroke_data: List of keystroke events with timestamps
            text_content: Final text content
            total_time: Total session time in seconds
            
        Returns:
            Dictionary containing all analysis metrics and mood scores
        """
        if not keystroke_data or total_time <= 0:
            return self._get_default_analysis()
        
        # Basic metrics
        basic_metrics = self._calculate_basic_metrics(keystroke_data, text_content, total_time)
        
        # Advanced pattern analysis
        patterns = self._analyze_typing_patterns(keystroke_data)
        
        # Mood analysis using heuristics
        mood_scores = self._calculate_mood_scores(basic_metrics, patterns)
        
        # Combine all results
        analysis = {
            **basic_metrics,
            **patterns,
            **mood_scores
        }
        
        return analysis
    
    def _calculate_basic_metrics(self, keystroke_data: List[Dict], text_content: str, total_time: float) -> Dict:
        """Calculate basic typing metrics."""
        total_keystrokes = len(keystroke_data)
        backspace_count = sum(1 for event in keystroke_data if event.get('key') == 'Backspace')
        
        # Calculate average keystroke speed (WPM)
        words = len(text_content.split())
        avg_keystroke_speed = (words / total_time) * 60 if total_time > 0 else 0
        
        return {
            'total_keystrokes': total_keystrokes,
            'backspace_count': backspace_count,
            'avg_keystroke_speed': avg_keystroke_speed,
            'correction_rate': (backspace_count / total_keystrokes * 100) if total_keystrokes > 0 else 0
        }
    
    def _analyze_typing_patterns(self, keystroke_data: List[Dict]) -> Dict:
        """Analyze typing patterns for pauses, bursts, and rhythm."""
        if len(keystroke_data) < 2:
            return {'pause_count': 0, 'avg_pause_duration': 0, 'burst_count': 0, 'slow_phases': 0}
        
        intervals = []
        pauses = []
        bursts = []
        current_burst = []
        
        # Calculate intervals between keystrokes
        for i in range(1, len(keystroke_data)):
            if 'timestamp' in keystroke_data[i] and 'timestamp' in keystroke_data[i-1]:
                interval = (keystroke_data[i]['timestamp'] - keystroke_data[i-1]['timestamp']) / 1000  # convert ms to seconds
                intervals.append(interval)
                
                # Identify pauses (long intervals)
                if interval > self.LONG_PAUSE_THRESHOLD:
                    pauses.append(interval)
                
                # Identify bursts (rapid typing sequences)
                current_speed = 60 / interval if interval > 0 else 0  # Convert to WPM
                if current_speed > self.BURST_MIN_SPEED:
                    current_burst.append(current_speed)
                else:
                    if len(current_burst) >= self.BURST_MIN_DURATION:
                        bursts.append(current_burst)
                    current_burst = []
        
        # Finalize last burst if applicable
        if len(current_burst) >= self.BURST_MIN_DURATION:
            bursts.append(current_burst)
        
        # Calculate slow phases
        slow_phases = sum(1 for interval in intervals if (60 / interval if interval > 0 else 0) < self.SLOW_KEYSTROKE_THRESHOLD)
        
        return {
            'pause_count': len(pauses),
            'avg_pause_duration': mean(pauses) if pauses else 0,
            'burst_count': len(bursts),
            'slow_phases': slow_phases,
            'rhythm_consistency': self._calculate_rhythm_consistency(intervals)
        }
    
    def _calculate_rhythm_consistency(self, intervals: List[float]) -> float:
        """Calculate how consistent the typing rhythm is (0-100)."""
        if len(intervals) < 3:
            return 50.0
        
        # Use coefficient of variation (std dev / mean) as consistency measure
        avg_interval = mean(intervals)
        if avg_interval == 0:
            return 0.0
        
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5
        cv = std_dev / avg_interval
        
        # Convert to 0-100 scale (lower CV = higher consistency)
        consistency = max(0, 100 - (cv * 100))
        return min(100, consistency)
    
    def _calculate_mood_scores(self, basic_metrics: Dict, patterns: Dict) -> Dict:
        """
        Apply heuristic rules to calculate mood scores.
        
        Heuristics:
        - High corrections + long pauses = Low focus
        - Many pauses + slow speed = Deep thinking/stress
        - Bursts + consistent rhythm = High confidence
        """
        focus_score = self._calculate_focus_score(basic_metrics, patterns)
        stress_score = self._calculate_stress_score(basic_metrics, patterns)
        confidence_score = self._calculate_confidence_score(basic_metrics, patterns)
        
        # Determine dominant mood
        scores = {'focus': focus_score, 'stress': stress_score, 'confidence': confidence_score}
        dominant_mood = max(scores, key=scores.get)
        
        # Adjust for neutral state
        if max(scores.values()) < 60:
            dominant_mood = 'neutral'
        
        return {
            'focus_score': focus_score,
            'stress_score': stress_score,
            'confidence_score': confidence_score,
            'dominant_mood': dominant_mood
        }
    
    def _calculate_focus_score(self, basic_metrics: Dict, patterns: Dict) -> float:
        """Calculate focus score based on corrections and consistency."""
        base_score = 70.0
        
        # Penalize high correction rate
        correction_penalty = basic_metrics.get('correction_rate', 0) * 2
        base_score -= correction_penalty
        
        # Penalize excessive pauses
        pause_penalty = min(patterns.get('pause_count', 0) * 5, 30)
        base_score -= pause_penalty
        
        # Reward rhythm consistency
        consistency_bonus = patterns.get('rhythm_consistency', 50) * 0.3
        base_score += consistency_bonus - 15  # Normalize
        
        return max(0, min(100, base_score))
    
    def _calculate_stress_score(self, basic_metrics: Dict, patterns: Dict) -> float:
        """Calculate stress score based on pauses and speed variations."""
        base_score = 20.0  # start slightly lower
        
        # Increase score for many long pauses
        pause_stress = min(patterns.get('avg_pause_duration', 0) * 5, 25)  # capped smaller
        base_score += pause_stress
        
        # Increase score for low rhythm consistency
        inconsistency_stress = (100 - patterns.get('rhythm_consistency', 50)) * 0.3  # less weight
        base_score += inconsistency_stress
        
        # Increase score for very slow or very fast typing
        speed = basic_metrics.get('avg_keystroke_speed', 40)
        if speed < 15 or speed > 130:
            base_score += 10  # lower penalty for speed extremes
        
        return max(0, min(100, base_score))
    
    def _calculate_confidence_score(self, basic_metrics: Dict, patterns: Dict) -> float:
        """Calculate confidence score based on bursts and low corrections."""
        base_score = 50.0
        
        # Reward typing bursts
        burst_bonus = patterns.get('burst_count', 0) * 15
        base_score += burst_bonus
        
        # Reward low correction rate
        correction_bonus = max(0, 10 - basic_metrics.get('correction_rate', 0)) * 3
        base_score += correction_bonus
        
        # Reward good rhythm consistency
        rhythm_bonus = patterns.get('rhythm_consistency', 50) * 0.4
        base_score += rhythm_bonus - 20  # Normalize
        
        # Reward moderate to fast speed
        speed = basic_metrics.get('avg_keystroke_speed', 40)
        if 40 <= speed <= 80:
            base_score += 15
        
        return max(0, min(100, base_score))
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis for empty or invalid data."""
        return {
            'total_keystrokes': 0,
            'backspace_count': 0,
            'avg_keystroke_speed': 0,
            'correction_rate': 0,
            'pause_count': 0,
            'avg_pause_duration': 0,
            'burst_count': 0,
            'slow_phases': 0,
            'rhythm_consistency': 50,
            'focus_score': 50,
            'stress_score': 50,
            'confidence_score': 50,
            'dominant_mood': 'neutral'
        }
