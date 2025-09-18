import json
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

class TimeTracker:
    def __init__(self, data_file: str = "data.json"):
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file or create default structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return {
            "sessions": [],
            "categories": ["programming", "wasted", "stop"],
            "current": None
        }

    def _save_data(self) -> None:
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat()

    def get_categories(self) -> List[str]:
        """Get available categories"""
        return self.data["categories"]

    def add_category(self, category: str) -> bool:
        """Add a new category"""
        if category not in self.data["categories"]:
            self.data["categories"].append(category)
            self._save_data()
            return True
        return False

    def remove_category(self, category: str) -> bool:
        """Remove a category"""
        if category in self.data["categories"] and len(self.data["categories"]) > 1:
            self.data["categories"].remove(category)
            self._save_data()
            return True
        return False

    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get current active session"""
        return self.data["current"]

    def start_session(self, category: str) -> bool:
        """Start a new session, stopping any current session"""
        if category not in self.data["categories"]:
            return False

        # Stop current session if exists
        if self.data["current"]:
            self.stop_session()

        # Handle special 'stop' category
        if category == "stop":
            self.data["current"] = None
            self._save_data()
            return True

        # Start new session
        timestamp = self._get_timestamp()
        self.data["current"] = {
            "category": category,
            "start": timestamp
        }
        self._save_data()
        return True

    def stop_session(self) -> Optional[Dict[str, Any]]:
        """Stop current session and save to history"""
        if not self.data["current"]:
            return None

        current = self.data["current"]
        timestamp = self._get_timestamp()

        # Create completed session
        completed_session = {
            "category": current["category"],
            "start": current["start"],
            "end": timestamp
        }

        self.data["sessions"].append(completed_session)
        self.data["current"] = None
        self._save_data()

        return completed_session

    def get_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get session history"""
        sessions = self.data["sessions"]
        if limit:
            return sessions[-limit:]
        return sessions

    def get_session_duration(self, session: Dict[str, Any]) -> Optional[float]:
        """Get duration of a session in seconds"""
        if "end" not in session or not session["end"]:
            return None

        start = datetime.fromisoformat(session["start"])
        end = datetime.fromisoformat(session["end"])
        return (end - start).total_seconds()

    def get_current_duration(self) -> Optional[float]:
        """Get duration of current session in seconds"""
        if not self.data["current"]:
            return None

        start = datetime.fromisoformat(self.data["current"]["start"])
        now = datetime.now(timezone.utc)
        return (now - start).total_seconds()

    def get_daily_stats(self, date: Optional[str] = None) -> Dict[str, float]:
        """Get daily time statistics by category (in hours)"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        stats = {}
        for session in self.data["sessions"]:
            session_date = session["start"][:10]  # Extract YYYY-MM-DD
            if session_date == date:
                category = session["category"]
                duration = self.get_session_duration(session)
                if duration:
                    stats[category] = stats.get(category, 0) + duration / 3600

        return stats

    def export_data(self) -> Dict[str, Any]:
        """Export all data for backup"""
        return self.data.copy()

    def import_data(self, data: Dict[str, Any]) -> bool:
        """Import data from backup"""
        try:
            # Validate data structure
            required_keys = ["sessions", "categories", "current"]
            if all(key in data for key in required_keys):
                self.data = data
                self._save_data()
                return True
        except Exception:
            pass
        return False