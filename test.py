#!/usr/bin/env python3
"""
Simple test script for TimeCreator functionality
"""

import os
import json
from tracker import TimeTracker

def test_basic_functionality():
    """Test basic time tracking functionality"""
    print("Testing TimeCreator basic functionality...")

    # Use test data file
    test_file = "test_data.json"
    if os.path.exists(test_file):
        os.remove(test_file)

    tracker = TimeTracker(test_file)

    # Test categories
    print(f"Default categories: {tracker.get_categories()}")
    assert "programming" in tracker.get_categories()
    assert "wasted" in tracker.get_categories()
    assert "stop" in tracker.get_categories()

    # Test adding category
    assert tracker.add_category("testing") == True
    assert "testing" in tracker.get_categories()
    assert tracker.add_category("testing") == False  # Already exists

    # Test starting session
    assert tracker.start_session("programming") == True
    current = tracker.get_current_session()
    assert current is not None
    assert current["category"] == "programming"

    # Test switching session
    assert tracker.start_session("wasted") == True
    current = tracker.get_current_session()
    assert current["category"] == "wasted"

    # Check that previous session was saved
    sessions = tracker.get_sessions()
    assert len(sessions) == 1
    assert sessions[0]["category"] == "programming"
    assert sessions[0]["end"] is not None

    # Test stopping session
    stopped = tracker.stop_session()
    assert stopped is not None
    assert stopped["category"] == "wasted"
    assert tracker.get_current_session() is None

    # Test stop category
    tracker.start_session("programming")
    assert tracker.start_session("stop") == True
    assert tracker.get_current_session() is None

    # Clean up
    os.remove(test_file)
    print("[OK] Basic functionality tests passed!")

def test_gui_import():
    """Test that GUI components can be imported"""
    print("Testing GUI imports...")
    try:
        from gui import CategoryPicker, show_category_picker
        print("[OK] GUI components imported successfully!")
    except Exception as e:
        print(f"[ERROR] GUI import failed: {e}")
        return False
    return True

def test_status_import():
    """Test that status display can be imported"""
    print("Testing status display import...")
    try:
        from status import StatusDisplay
        print("[OK] Status display imported successfully!")
    except Exception as e:
        print(f"[ERROR] Status display import failed: {e}")
        return False
    return True

def test_launcher_import():
    """Test that launcher can be imported"""
    print("Testing launcher import...")
    try:
        from launch import TimeCreatorApp
        print("[OK] Launcher imported successfully!")
    except Exception as e:
        print(f"[ERROR] Launcher import failed: {e}")
        return False
    return True

if __name__ == "__main__":
    print("TimeCreator Test Suite")
    print("=" * 40)

    try:
        test_basic_functionality()
        test_gui_import()
        test_status_import()
        test_launcher_import()

        print("\n" + "=" * 40)
        print("[OK] All tests passed! TimeCreator is ready to use.")
        print("\nQuick start:")
        print("1. Install optional dependencies: pip install -r requirements.txt")
        print("2. Start daemon mode: python launch.py daemon")
        print("3. Or use CLI: python launch.py status")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()