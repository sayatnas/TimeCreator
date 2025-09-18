#!/usr/bin/env python3
"""
TimeCreator - Simple time tracking inspired by timewarrior
Main launcher with hotkey support and status display
"""

import sys
import argparse
import threading
import time
import signal
from typing import Optional

from tracker import TimeTracker
from status import StatusDisplay
from gui import show_category_picker, quick_switch_category
from overlay import MinimalOverlay

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("keyboard library not available - hotkeys disabled")

class TimeCreatorApp:
    def __init__(self, data_file: str = "data.json"):
        self.tracker = TimeTracker(data_file)
        self.status_display = None
        self.hotkey_thread = None
        self.running = False

    def _setup_hotkeys(self):
        """Setup global hotkeys"""
        if not KEYBOARD_AVAILABLE:
            return

        try:
            # Ctrl+Alt+T to open picker
            keyboard.add_hotkey('ctrl+alt+t', self._hotkey_picker)
            # Ctrl+Alt+S to stop current session
            keyboard.add_hotkey('ctrl+alt+s', self._hotkey_stop)
            print("Hotkeys registered:")
            print("  Ctrl+Alt+T - Open category picker")
            print("  Ctrl+Alt+S - Stop current session")
        except Exception as e:
            print(f"Failed to register hotkeys: {e}")

    def _hotkey_picker(self):
        """Hotkey handler for category picker"""
        def picker_thread():
            try:
                selected = show_category_picker(self.tracker)
                if selected:
                    self.tracker.start_session(selected)
                    print(f"Switched to: {selected}")
            except Exception as e:
                print(f"Error in picker: {e}")

        threading.Thread(target=picker_thread, daemon=True).start()

    def _hotkey_stop(self):
        """Hotkey handler to stop current session"""
        session = self.tracker.stop_session()
        if session:
            duration = self.tracker.get_session_duration(session)
            if duration:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                print(f"Stopped {session['category']} - Duration: {hours:02d}:{minutes:02d}")
            else:
                print(f"Stopped {session['category']}")
        else:
            print("No active session to stop")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down TimeCreator...")
        self.stop()
        sys.exit(0)

    def start_overlay(self):
        """Start the minimal floating overlay (main interface)"""
        if self.running:
            return

        self.running = True
        print("Starting TimeCreator minimal overlay...")

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Show current status
        current = self.tracker.get_current_session()
        if current:
            print(f"Current session: {current['category']}")
        else:
            print("No active session")

        # Start minimal overlay (this will block)
        try:
            overlay = MinimalOverlay(self.tracker)
            overlay.start()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Error starting overlay: {e}")
            self.stop()

    def start_daemon(self):
        """Start the daemon mode with status display and hotkeys"""
        if self.running:
            return

        self.running = True
        print("Starting TimeCreator daemon...")

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Setup hotkeys
        self._setup_hotkeys()

        # Show current status
        current = self.tracker.get_current_session()
        if current:
            duration = self.tracker.get_current_duration()
            if duration:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                print(f"Current session: {current['category']} ({hours:02d}:{minutes:02d})")
            else:
                print(f"Current session: {current['category']}")
        else:
            print("No active session")

        # Start status display (this will block)
        try:
            self.status_display = StatusDisplay(self.tracker)
            self.status_display.start()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Error starting status display: {e}")
            self.stop()

    def stop(self):
        """Stop the daemon"""
        self.running = False

        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all_hotkeys()
            except:
                pass

        if self.status_display:
            self.status_display.stop()

    def cmd_status(self):
        """Show current status"""
        current = self.tracker.get_current_session()
        if current:
            duration = self.tracker.get_current_duration()
            if duration:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                print(f"Active: {current['category']} ({hours:02d}:{minutes:02d})")
            else:
                print(f"Active: {current['category']}")
        else:
            print("No active session")

    def cmd_start(self, category: str):
        """Start a session"""
        if self.tracker.start_session(category):
            print(f"Started: {category}")
        else:
            print(f"Error: Unknown category '{category}'")
            print(f"Available categories: {', '.join(self.tracker.get_categories())}")

    def cmd_stop(self):
        """Stop current session"""
        session = self.tracker.stop_session()
        if session:
            duration = self.tracker.get_session_duration(session)
            if duration:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                print(f"Stopped: {session['category']} - Duration: {hours:02d}:{minutes:02d}")
            else:
                print(f"Stopped: {session['category']}")
        else:
            print("No active session to stop")

    def cmd_picker(self):
        """Show category picker"""
        selected = show_category_picker(self.tracker)
        if selected:
            self.tracker.start_session(selected)
            print(f"Started: {selected}")

    def cmd_categories(self):
        """List available categories"""
        categories = self.tracker.get_categories()
        print("Available categories:")
        for cat in categories:
            print(f"  {cat}")

    def cmd_add_category(self, category: str):
        """Add a new category"""
        if self.tracker.add_category(category):
            print(f"Added category: {category}")
        else:
            print(f"Category '{category}' already exists")

    def cmd_history(self, limit: int = 10):
        """Show session history"""
        sessions = self.tracker.get_sessions(limit)
        if not sessions:
            print("No session history")
            return

        print(f"Last {len(sessions)} sessions:")
        for session in reversed(sessions):  # Show most recent first
            duration = self.tracker.get_session_duration(session)
            start_time = session['start'][:16].replace('T', ' ')  # Remove seconds and timezone

            if duration:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                duration_str = f"{hours:02d}:{minutes:02d}"
            else:
                duration_str = "??:??"

            print(f"  {start_time} - {session['category']} ({duration_str})")

    def cmd_stats(self):
        """Show daily statistics"""
        stats = self.tracker.get_daily_stats()
        if not stats:
            print("No activity today")
            return

        print("Today's activity:")
        total_hours = 0
        for category, hours in sorted(stats.items()):
            print(f"  {category}: {hours:.1f} hours")
            total_hours += hours
        print(f"  Total: {total_hours:.1f} hours")

def main():
    parser = argparse.ArgumentParser(description="TimeCreator - Simple time tracking")
    parser.add_argument('--data', default='data.json', help='Data file path')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Daemon mode
    subparsers.add_parser('daemon', help='Start daemon with status display and hotkeys')
    subparsers.add_parser('overlay', help='Start minimal floating overlay (main interface)')

    # Session commands
    subparsers.add_parser('status', help='Show current session status')
    start_parser = subparsers.add_parser('start', help='Start a session')
    start_parser.add_argument('category', help='Category to start')
    subparsers.add_parser('stop', help='Stop current session')
    subparsers.add_parser('picker', help='Show category picker')

    # Category management
    subparsers.add_parser('categories', help='List categories')
    add_parser = subparsers.add_parser('add', help='Add category')
    add_parser.add_argument('category', help='Category to add')

    # History and stats
    history_parser = subparsers.add_parser('history', help='Show session history')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of sessions to show')
    subparsers.add_parser('stats', help='Show daily statistics')

    args = parser.parse_args()

    app = TimeCreatorApp(args.data)

    if args.command == 'daemon':
        app.start_daemon()
    elif args.command == 'overlay':
        app.start_overlay()
    elif args.command == 'status':
        app.cmd_status()
    elif args.command == 'start':
        app.cmd_start(args.category)
    elif args.command == 'stop':
        app.cmd_stop()
    elif args.command == 'picker':
        app.cmd_picker()
    elif args.command == 'categories':
        app.cmd_categories()
    elif args.command == 'add':
        app.cmd_add_category(args.category)
    elif args.command == 'history':
        app.cmd_history(args.limit)
    elif args.command == 'stats':
        app.cmd_stats()
    else:
        # Default to overlay if no command given
        app.start_overlay()

if __name__ == "__main__":
    main()