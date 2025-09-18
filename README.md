# TimeCreator

A simple, mindful time tracking system for Windows inspired by timewarrior. Focus on building the habit of tracking time rather than perfect data collection.

## Features

- **Simple category-based tracking** - programming, wasted, stop (customizable)
- **Manual switching for mindfulness** - Every category change is a conscious decision
- **Multiple interfaces:**
  - System tray with right-click menu (when dependencies installed)
  - GUI picker with keyboard navigation
  - Command-line interface
  - Global hotkeys (Ctrl+Alt+T for picker, Ctrl+Alt+S to stop)
- **Persistent data storage** - JSON format for easy backup/inspection
- **Fallback mode** - Works without any external dependencies

## Philosophy

This tool emphasizes the **habit** of time tracking over perfect data. Like the person in the video said: "It's more about the manual act of control+space+t... it's just like another message to me."

The goal isn't perfect time tracking data - it's building mindfulness about how you spend your time.

## Installation

### Basic Installation (No Dependencies)
Works with just Python's standard library but with limited functionality:

```bash
git clone https://github.com/yourusername/TimeCreator.git
cd TimeCreator
python test.py  # Verify everything works
```

### Full Installation (Recommended)
Install optional dependencies for full functionality:

```bash
pip install -r requirements.txt
```

**Optional Dependencies:**
- `pystray + Pillow` - System tray functionality
- `keyboard` - Global hotkey support

## Usage

### Daemon Mode (Recommended)
Start with system tray and global hotkeys:
```bash
python launch.py daemon
```

**Hotkeys:**
- `Ctrl+Alt+T` - Open category picker
- `Ctrl+Alt+S` - Stop current session

### Command Line Interface

```bash
# Check current status
python launch.py status

# Start a session
python launch.py start programming

# Stop current session
python launch.py stop

# Show category picker
python launch.py picker

# List categories
python launch.py categories

# Add new category
python launch.py add "deep-work"

# Show recent history
python launch.py history

# Show daily stats
python launch.py stats
```

### Batch File (Windows)
Use the included batch file for easier access:
```cmd
timecreator.bat status
timecreator.bat start programming
timecreator.bat daemon
```

## File Structure

```
TimeCreator/
├── tracker.py          # Core time tracking logic
├── gui.py              # Category picker interface
├── status.py           # System tray/status display
├── launch.py           # Main launcher
├── timecreator.bat     # Windows batch launcher
├── data.json           # Your time tracking data
├── requirements.txt    # Optional dependencies
├── test.py             # Test suite
└── README.md           # This file
```

## Data Format

Data is stored in `data.json`:

```json
{
  "sessions": [
    {
      "category": "programming",
      "start": "2025-01-15T10:00:00+00:00",
      "end": "2025-01-15T11:30:00+00:00"
    }
  ],
  "categories": ["programming", "wasted", "stop"],
  "current": {
    "category": "programming",
    "start": "2025-01-15T12:00:00+00:00"
  }
}
```

## Customization

### Adding Categories
```bash
python launch.py add "reading"
python launch.py add "meetings"
```

### Removing Categories
Edit `data.json` directly to remove categories from the list.

### Changing Data Location
```bash
python launch.py --data /path/to/your/data.json daemon
```

## Interface Modes

### System Tray Mode (Full Dependencies)
- Icon in system tray showing current activity
- Right-click menu for quick category switching
- Tooltip shows elapsed time
- Double-click to open picker

### Fallback Window Mode (No Dependencies)
- Small status window in bottom-right corner
- Shows current activity and elapsed time
- Double-click to open picker
- Right-click for context menu

### GUI Picker
- Clean, minimal interface
- Keyboard navigation (arrow keys, enter, escape)
- Shows current session info
- Centered on screen

## Differences from Timewarrior

- **Windows-native** - Built for Windows with GUI interfaces
- **Mindfulness-focused** - Manual switching is the main feature
- **Simpler** - Fewer features, easier to set up
- **Visual** - System tray and GUI interfaces
- **Optional dependencies** - Works without any external libraries

## Tips for Building the Habit

1. **Don't worry about perfect data** - The act of switching matters more than accuracy
2. **Use the "wasted" category liberally** - It's about awareness, not judgment
3. **Make switching easy** - Set up hotkeys and keep the picker accessible
4. **Focus on the ritual** - Every category switch is a moment of mindfulness

## Troubleshooting

### No System Tray Icon
Install optional dependencies: `pip install pystray Pillow`

### No Global Hotkeys
Install keyboard library: `pip install keyboard`

### GUI Issues
The fallback mode uses tkinter (included with Python). If GUI doesn't work, use CLI mode only.

### Unicode Issues on Windows
If you see encoding errors, ensure your terminal supports UTF-8 or use the CLI commands which use ASCII only.

## Contributing

This is intentionally a simple tool. When adding features, consider whether they align with the mindfulness philosophy of the original timewarrior workflow.

## License

MIT License - Use, modify, and distribute freely.