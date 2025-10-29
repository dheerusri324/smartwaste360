# backend/utils/log_capture.py
"""
In-memory log capture for debugging without Render's professional plan
"""

from collections import deque
from datetime import datetime
import threading

class LogCapture:
    """Thread-safe in-memory log storage"""
    
    def __init__(self, max_logs=100):
        self.logs = deque(maxlen=max_logs)
        self.lock = threading.Lock()
    
    def add(self, level, message, **kwargs):
        """Add a log entry"""
        with self.lock:
            entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': level,
                'message': message,
                **kwargs
            }
            self.logs.append(entry)
    
    def get_all(self):
        """Get all logs"""
        with self.lock:
            return list(self.logs)
    
    def clear(self):
        """Clear all logs"""
        with self.lock:
            self.logs.clear()

# Global instance
log_capture = LogCapture(max_logs=100)
