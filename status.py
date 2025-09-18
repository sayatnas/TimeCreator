import tkinter as tk
from tkinter import font
import threading
import time
from typing import Optional, Callable
from tracker import TimeTracker
from gui import show_category_picker

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    # Create dummy classes for type hints when pystray is not available
    class Image:
        @staticmethod
        def new(*args, **kwargs):
            return None
    print("pystray not available, using fallback status display")

class StatusDisplay:
    def __init__(self, tracker: TimeTracker):
        self.tracker = tracker
        self.running = False
        self.update_thread = None

        if PYSTRAY_AVAILABLE:
            self.tray_icon = None
            self._setup_tray()
        else:
            self.status_window = None
            self._setup_window()

    def _setup_tray(self):
        """Setup system tray icon"""
        # Create a simple icon
        icon_image = self._create_icon()

        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Switch Category", self._show_picker),
            pystray.MenuItem("---", None),
            *[pystray.MenuItem(cat, lambda _, c=cat: self._switch_to_category(c))
              for cat in self.tracker.get_categories()],
            pystray.MenuItem("---", None),
            pystray.MenuItem("Exit", self._exit)
        )

        self.tray_icon = pystray.Icon(
            "TimeCreator",
            icon_image,
            "TimeCreator - No active session",
            menu
        )

    def _create_icon(self, text: str = "TC"):
        """Create a simple text-based icon"""
        if not PYSTRAY_AVAILABLE:
            return None

        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw circle background
        margin = 4
        draw.ellipse([margin, margin, size-margin, size-margin],
                    fill=(70, 130, 180, 255), outline=(50, 110, 160, 255), width=2)

        # Draw text
        try:
            font_obj = ImageFont.truetype("arial.ttf", 20)
        except:
            font_obj = ImageFont.load_default()

        # Center text
        bbox = draw.textbbox((0, 0), text, font=font_obj)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2

        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font_obj)
        return image

    def _setup_window(self):
        """Setup fallback status window"""
        self.status_window = tk.Tk()
        self.status_window.title("TimeCreator Status")
        self.status_window.geometry("250x80")
        self.status_window.configure(bg='#2d2d2d')
        self.status_window.attributes('-topmost', True)

        # Position in bottom right
        self.status_window.update_idletasks()
        x = self.status_window.winfo_screenwidth() - 260
        y = self.status_window.winfo_screenheight() - 120
        self.status_window.geometry(f"250x80+{x}+{y}")

        # Create status label
        self.status_label = tk.Label(
            self.status_window,
            text="No active session",
            font=font.Font(family="Consolas", size=10, weight="bold"),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        self.status_label.pack(expand=True)

        # Bind double-click to open picker
        self.status_window.bind('<Double-Button-1>', lambda e: self._show_picker())
        self.status_label.bind('<Double-Button-1>', lambda e: self._show_picker())

        # Right-click menu
        self._setup_context_menu()

    def _setup_context_menu(self):
        """Setup right-click context menu for fallback window"""
        self.context_menu = tk.Menu(self.status_window, tearoff=0)
        self.context_menu.add_command(label="Switch Category", command=self._show_picker)
        self.context_menu.add_separator()

        for category in self.tracker.get_categories():
            self.context_menu.add_command(
                label=category,
                command=lambda c=category: self._switch_to_category(c)
            )

        self.context_menu.add_separator()
        self.context_menu.add_command(label="Exit", command=self._exit)

        def show_context_menu(event):
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

        self.status_window.bind('<Button-3>', show_context_menu)
        self.status_label.bind('<Button-3>', show_context_menu)

    def _show_picker(self):
        """Show category picker"""
        def picker_thread():
            selected = show_category_picker(self.tracker)
            if selected:
                self.tracker.start_session(selected)

        threading.Thread(target=picker_thread, daemon=True).start()

    def _switch_to_category(self, category: str):
        """Switch to specific category"""
        self.tracker.start_session(category)

    def _exit(self):
        """Exit the application"""
        self.stop()

    def _format_duration(self, seconds: float) -> str:
        """Format duration as HH:MM"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"

    def _get_status_text(self) -> tuple[str, str]:
        """Get current status text and tooltip"""
        current = self.tracker.get_current_session()
        if not current:
            return "No active session", "TimeCreator - No active session"

        category = current['category']
        duration = self.tracker.get_current_duration()

        if duration:
            time_str = self._format_duration(duration)
            short_text = f"{category} ({time_str})"
            tooltip = f"TimeCreator - {category}: {time_str}"
        else:
            short_text = category
            tooltip = f"TimeCreator - {category}"

        return short_text, tooltip

    def _update_status(self):
        """Update status display"""
        status_text, tooltip = self._get_status_text()

        if PYSTRAY_AVAILABLE and self.tray_icon:
            # Update tray icon
            current = self.tracker.get_current_session()
            if current:
                # Create icon with category abbreviation
                abbrev = current['category'][:2].upper()
                icon = self._create_icon(abbrev)
            else:
                icon = self._create_icon("TC")

            self.tray_icon.icon = icon
            self.tray_icon.title = tooltip

            # Update menu
            menu = pystray.Menu(
                pystray.MenuItem("Switch Category", self._show_picker),
                pystray.MenuItem("---", None),
                *[pystray.MenuItem(cat, lambda _, c=cat: self._switch_to_category(c))
                  for cat in self.tracker.get_categories()],
                pystray.MenuItem("---", None),
                pystray.MenuItem("Exit", self._exit)
            )
            self.tray_icon.menu = menu

        elif self.status_window:
            # Update window
            self.status_label.config(text=status_text)
            self.status_window.title(tooltip)

    def _update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                self._update_status()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"Error updating status: {e}")
                time.sleep(5)

    def start(self):
        """Start the status display"""
        if self.running:
            return

        self.running = True

        if PYSTRAY_AVAILABLE and self.tray_icon:
            # Start update thread
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()

            # Initial update
            self._update_status()

            # Run tray icon (blocks)
            self.tray_icon.run()
        else:
            # Start update thread for window
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()

            # Initial update
            self._update_status()

            # Show window and start mainloop
            self.status_window.mainloop()

    def stop(self):
        """Stop the status display"""
        self.running = False

        if PYSTRAY_AVAILABLE and self.tray_icon:
            self.tray_icon.stop()
        elif self.status_window:
            self.status_window.quit()
            self.status_window.destroy()

if __name__ == "__main__":
    tracker = TimeTracker()
    status = StatusDisplay(tracker)

    try:
        status.start()
    except KeyboardInterrupt:
        status.stop()