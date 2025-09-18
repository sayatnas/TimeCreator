#!/usr/bin/env python3
"""
Daily file-based time tracker
Stores data in individual JSON files per day for better organization
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pathlib import Path

class DailyTracker:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Global config file
        self.config_file = self.data_dir / "config.json"
        self.config = self._load_config()

        # Current session tracking
        self.current_session_file = self.data_dir / "current_session.json"
        self.current_session = self._load_current_session()

    def _load_config(self) -> Dict[str, Any]:
        """Load global configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Default config
        default_config = {
            "categories": ["programming", "wasted", "stop"],
            "version": "2.0"
        }
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save global configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _load_current_session(self) -> Optional[Dict[str, Any]]:
        """Load current active session - but discard incomplete sessions on startup"""
        if self.current_session_file.exists():
            try:
                with open(self.current_session_file, 'r') as f:
                    session = json.load(f)

                # If session doesn't have an end time, it's incomplete - discard it
                if session and 'end' not in session:
                    print(f"Discarding incomplete session: {session.get('category', 'unknown')}")
                    self._save_current_session(None)  # Clear the incomplete session
                    return None

                return session
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return None

    def _save_current_session(self, session: Optional[Dict[str, Any]]) -> None:
        """Save current active session"""
        if session is None:
            if self.current_session_file.exists():
                self.current_session_file.unlink()
        else:
            with open(self.current_session_file, 'w') as f:
                json.dump(session, f, indent=2)

    def _get_daily_file(self, date: str) -> Path:
        """Get file path for a specific date (YYYY-MM-DD)"""
        year, month, day = date.split('-')
        year_dir = self.data_dir / year
        year_dir.mkdir(exist_ok=True)

        month_dir = year_dir / month
        month_dir.mkdir(exist_ok=True)

        return month_dir / f"{day}.json"

    def _load_daily_data(self, date: str) -> Dict[str, Any]:
        """Load data for a specific date"""
        daily_file = self._get_daily_file(date)

        if daily_file.exists():
            try:
                with open(daily_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Default daily structure
        return {
            "date": date,
            "sessions": [],
            "total_by_category": {},
            "created": datetime.now(timezone.utc).isoformat(),
            "modified": datetime.now(timezone.utc).isoformat()
        }

    def _save_daily_data(self, date: str, data: Dict[str, Any]) -> None:
        """Save data for a specific date"""
        data["modified"] = datetime.now(timezone.utc).isoformat()
        daily_file = self._get_daily_file(date)

        with open(daily_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat()

    def _get_date_str(self, timestamp: str = None) -> str:
        """Get date string (YYYY-MM-DD) from timestamp or current time"""
        if timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = datetime.now(timezone.utc)
        return dt.strftime('%Y-%m-%d')

    def get_categories(self) -> List[str]:
        """Get available categories"""
        return self.config["categories"]

    def add_category(self, category: str) -> bool:
        """Add a new category"""
        if category not in self.config["categories"]:
            self.config["categories"].append(category)
            self._save_config(self.config)
            return True
        return False

    def remove_category(self, category: str) -> bool:
        """Remove a category"""
        if category in self.config["categories"] and len(self.config["categories"]) > 1:
            self.config["categories"].remove(category)
            self._save_config(self.config)
            return True
        return False

    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get current active session"""
        return self.current_session

    def start_session(self, category: str) -> bool:
        """Start a new session, stopping any current session"""
        if category not in self.config["categories"]:
            return False

        # Stop current session if exists
        if self.current_session:
            self.stop_session()

        # Handle special 'stop' category
        if category == "stop":
            self.current_session = None
            self._save_current_session(None)
            return True

        # Start new session
        timestamp = self._get_timestamp()
        self.current_session = {
            "category": category,
            "start": timestamp
        }
        self._save_current_session(self.current_session)
        return True

    def stop_session(self) -> Optional[Dict[str, Any]]:
        """Stop current session and save to daily file"""
        if not self.current_session:
            return None

        current = self.current_session
        timestamp = self._get_timestamp()

        # Create completed session
        completed_session = {
            "category": current["category"],
            "start": current["start"],
            "end": timestamp,
            "duration": self._calculate_duration(current["start"], timestamp)
        }

        # Save to daily file
        start_date = self._get_date_str(current["start"])
        daily_data = self._load_daily_data(start_date)
        daily_data["sessions"].append(completed_session)

        # Update category totals
        category = completed_session["category"]
        if category not in daily_data["total_by_category"]:
            daily_data["total_by_category"][category] = 0
        daily_data["total_by_category"][category] += completed_session["duration"]

        self._save_daily_data(start_date, daily_data)

        # Clear current session
        self.current_session = None
        self._save_current_session(None)

        return completed_session

    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calculate duration between two timestamps in seconds"""
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        return (end - start).total_seconds()

    def get_current_duration(self) -> Optional[float]:
        """Get duration of current session in seconds"""
        if not self.current_session:
            return None

        start = datetime.fromisoformat(self.current_session["start"].replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (now - start).total_seconds()

    def get_daily_stats(self, date: str) -> Dict[str, float]:
        """Get statistics for a specific date (hours by category)"""
        daily_data = self._load_daily_data(date)
        return {cat: hours / 3600 for cat, hours in daily_data["total_by_category"].items()}

    def get_daily_sessions(self, date: str) -> List[Dict[str, Any]]:
        """Get all sessions for a specific date"""
        daily_data = self._load_daily_data(date)
        return daily_data["sessions"]

    def get_date_range_stats(self, start_date: str, end_date: str) -> Dict[str, Dict[str, float]]:
        """Get stats for a range of dates"""
        from datetime import datetime, timedelta

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        stats = {}
        current = start

        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            stats[date_str] = self.get_daily_stats(date_str)
            current += timedelta(days=1)

        return stats

    def get_category_totals(self, days_back: int = 365) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive stats per category for the last N days"""
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        category_stats = {}
        for category in self.config["categories"]:
            if category == "stop":
                continue
            category_stats[category] = {
                'total_hours': 0,
                'days_active': 0,
                'average_per_day': 0,
                'max_day_hours': 0
            }

        # Scan through date range
        current = start_date
        days_scanned = 0

        while current <= end_date:
            date_str = current.strftime('%Y-%m-%d')
            daily_stats = self.get_daily_stats(date_str)
            days_scanned += 1

            for category, hours in daily_stats.items():
                if category in category_stats:
                    category_stats[category]['total_hours'] += hours
                    if hours > 0:
                        category_stats[category]['days_active'] += 1
                        category_stats[category]['max_day_hours'] = max(
                            category_stats[category]['max_day_hours'], hours
                        )

            current += timedelta(days=1)

        # Calculate averages
        for category in category_stats:
            if days_scanned > 0:
                category_stats[category]['average_per_day'] = (
                    category_stats[category]['total_hours'] / days_scanned
                )

        return category_stats

    def migrate_from_old_format(self, old_data_file: str) -> bool:
        """Migrate data from old single-file format"""
        if not os.path.exists(old_data_file):
            return False

        try:
            with open(old_data_file, 'r') as f:
                old_data = json.load(f)

            # Migrate categories
            if "categories" in old_data:
                self.config["categories"] = old_data["categories"]
                self._save_config(self.config)

            # Migrate sessions
            if "sessions" in old_data:
                sessions_by_date = {}

                for session in old_data["sessions"]:
                    if "start" not in session or "end" not in session:
                        continue

                    start_date = self._get_date_str(session["start"])

                    if start_date not in sessions_by_date:
                        sessions_by_date[start_date] = []

                    # Calculate duration
                    duration = self._calculate_duration(session["start"], session["end"])
                    session["duration"] = duration

                    sessions_by_date[start_date].append(session)

                # Save to daily files
                for date_str, sessions in sessions_by_date.items():
                    daily_data = self._load_daily_data(date_str)
                    daily_data["sessions"] = sessions

                    # Calculate totals
                    for session in sessions:
                        category = session["category"]
                        if category not in daily_data["total_by_category"]:
                            daily_data["total_by_category"][category] = 0
                        daily_data["total_by_category"][category] += session["duration"]

                    self._save_daily_data(date_str, daily_data)

            # Migrate current session
            if "current" in old_data and old_data["current"]:
                self.current_session = old_data["current"]
                self._save_current_session(self.current_session)

            return True

        except Exception as e:
            print(f"Migration failed: {e}")
            return False

    def list_available_dates(self) -> List[str]:
        """List all dates that have data"""
        dates = []

        if not self.data_dir.exists():
            return dates

        for year_dir in self.data_dir.iterdir():
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue

            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir() or not month_dir.name.isdigit():
                    continue

                for day_file in month_dir.iterdir():
                    if day_file.suffix == '.json' and day_file.stem.isdigit():
                        date_str = f"{year_dir.name}-{month_dir.name.zfill(2)}-{day_file.stem.zfill(2)}"
                        dates.append(date_str)

        return sorted(dates)

# Compatibility wrapper for existing code
class TimeTracker(DailyTracker):
    """Compatibility wrapper that maintains old API while using new daily storage"""

    def __init__(self, data_file: str = "data.json"):
        # Initialize daily tracker
        super().__init__()

        # Auto-migrate if old file exists
        if os.path.exists(data_file):
            print("Migrating from old data format...")
            if self.migrate_from_old_format(data_file):
                print("Migration successful!")
                # Backup old file
                backup_file = f"{data_file}.backup"
                import shutil
                shutil.copy2(data_file, backup_file)
                print(f"Old data backed up to {backup_file}")
            else:
                print("Migration failed, keeping both formats")

    def get_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all sessions (for compatibility)"""
        all_sessions = []

        for date_str in self.list_available_dates():
            sessions = self.get_daily_sessions(date_str)
            all_sessions.extend(sessions)

        # Sort by start time
        all_sessions.sort(key=lambda x: x["start"])

        if limit:
            return all_sessions[-limit:]
        return all_sessions

    def get_session_duration(self, session: Dict[str, Any]) -> Optional[float]:
        """Get duration of a session in seconds (for compatibility)"""
        if "duration" in session:
            return session["duration"]

        if "end" not in session or not session["end"]:
            return None

        return self._calculate_duration(session["start"], session["end"])

if __name__ == "__main__":
    # Test the new daily tracker
    tracker = TimeTracker()
    print("Available dates:", tracker.list_available_dates())
    print("Categories:", tracker.get_categories())
    print("Current session:", tracker.get_current_session())