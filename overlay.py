import tkinter as tk
from tkinter import font
import threading
from typing import Optional
from tracker import TimeTracker
from gui import show_category_picker

class MinimalOverlay:
    def __init__(self, tracker: TimeTracker):
        self.tracker = tracker
        self.root = tk.Tk()
        self.running = False
        self.update_thread = None
        self.expanded = False
        self.category_buttons = []
        self.base_height = 30

        self._setup_window()
        self._create_widgets()
        self._bind_events()

    def _setup_window(self):
        """Configure the minimal overlay window"""
        self.root.title("TimeCreator")

        # Remove window decorations but keep it clickable
        self.root.overrideredirect(True)

        # On Windows, make sure window can receive events
        self.root.wm_attributes("-disabled", False)

        # Set window properties
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.85)    # Slightly transparent

        # Make sure window can receive focus and clicks
        self.root.focus_set()

        # Set initial size and position (small, top-right corner)
        self.width = 120
        self.initial_height = 30

        # Position in top-right corner with some margin
        screen_width = self.root.winfo_screenwidth()
        self.x = screen_width - self.width - 20
        self.y = 20

        self.root.geometry(f"{self.width}x{self.initial_height}+{self.x}+{self.y}")

        # Set background color
        self.root.configure(bg='#2d2d2d')

        # Make window stay on top of all others
        self.root.lift()

    def _create_widgets(self):
        """Create the minimal category display"""
        # Main frame to hold everything
        self.main_frame = tk.Frame(self.root, bg='#2d2d2d')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Current category label (always visible)
        self.category_label = tk.Label(
            self.main_frame,
            text="No session",
            font=font.Font(family="Segoe UI", size=9, weight="normal"),
            bg='#2d2d2d',
            fg='#ffffff',
            padx=8,
            pady=6,
            cursor='hand2'  # Show it's clickable
        )
        self.category_label.pack(fill=tk.X)

        # Frame for category buttons (initially hidden)
        self.button_frame = tk.Frame(self.main_frame, bg='#2d2d2d')
        # Don't pack initially - will be shown/hidden on click

    def _bind_events(self):
        """Bind click events"""
        # Only bind to the label to avoid multiple triggers
        self.category_label.bind('<Button-1>', self._on_click)
        self.category_label.bind('<Button-3>', self._on_right_click)

        # Make window draggable
        self._setup_dragging()

    def _setup_dragging(self):
        """Setup window dragging functionality"""
        self.drag_data = {"x": 0, "y": 0}

        def start_drag(event):
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

        def do_drag(event):
            x = self.root.winfo_x() + (event.x - self.drag_data["x"])
            y = self.root.winfo_y() + (event.y - self.drag_data["y"])
            self.root.geometry(f"+{x}+{y}")

        # Bind to both window and label for dragging
        self.root.bind('<ButtonPress-2>', start_drag)    # Middle mouse button
        self.root.bind('<B2-Motion>', do_drag)
        self.category_label.bind('<ButtonPress-2>', start_drag)
        self.category_label.bind('<B2-Motion>', do_drag)

    def _on_click(self, event):
        """Handle left click - toggle category list"""
        if self.expanded:
            self._collapse()
        else:
            self._expand()

        # Stop event propagation
        return "break"

    def _on_right_click(self, event):
        """Handle right click - show simple context menu"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.configure(bg='#3d3d3d', fg='#ffffff',
                              activebackground='#4a9eff', activeforeground='#ffffff')

        # Quick category switches
        for category in self.tracker.get_categories():
            context_menu.add_command(
                label=category,
                command=lambda c=category: self._quick_switch(c)
            )

        context_menu.add_separator()
        context_menu.add_command(label="Exit", command=self._exit)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _quick_switch(self, category: str):
        """Quickly switch to a category"""
        self.tracker.start_session(category)
        self._update_display()

    def _expand(self):
        """Show category buttons below current category"""
        if self.expanded:
            return

        self.expanded = True

        # Clear any existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.category_buttons.clear()

        # Create buttons for each category
        categories = self.tracker.get_categories()
        current_category = None
        current_session = self.tracker.get_current_session()
        if current_session:
            current_category = current_session['category']

        for category in categories:
            # Skip current category
            if category == current_category:
                continue

            # Determine button color based on category
            if category == 'wasted':
                bg_color = '#8B4513'  # Brown
            elif category == 'programming':
                bg_color = '#2E8B57'  # Sea green
            elif category == 'stop':
                bg_color = '#2d2d2d'  # Dark gray
            else:
                bg_color = '#4682B4'  # Steel blue

            btn = tk.Label(
                self.button_frame,
                text=category,
                font=font.Font(family="Segoe UI", size=9, weight="normal"),
                bg=bg_color,
                fg='#ffffff',
                padx=8,
                pady=4,
                cursor='hand2'
            )

            # Bind click event
            btn.bind('<Button-1>', lambda e, cat=category: self._select_category(cat))
            btn.pack(fill=tk.X, padx=0, pady=(1, 0))
            self.category_buttons.append(btn)

        # Show the button frame
        self.button_frame.pack(fill=tk.X, pady=(1, 0))

        # Resize window to fit all buttons
        button_count = len(self.category_buttons)
        new_height = self.initial_height + (button_count * 25)  # 25px per button
        self.root.geometry(f"{self.width}x{new_height}+{self.x}+{self.y}")

        # Bind click outside to collapse
        self.root.bind('<FocusOut>', lambda e: self._collapse())

    def _collapse(self):
        """Hide category buttons"""
        if not self.expanded:
            return

        self.expanded = False

        # Hide button frame
        self.button_frame.pack_forget()

        # Resize window back to original size
        self.root.geometry(f"{self.width}x{self.initial_height}+{self.x}+{self.y}")

        # Remove focus out binding
        self.root.unbind('<FocusOut>')

    def _select_category(self, category: str):
        """Select a category and switch to it"""
        self.tracker.start_session(category)
        self._update_display()
        self._collapse()

    def _exit(self):
        """Exit the overlay"""
        self.stop()

    def _update_display(self):
        """Update the category display"""
        current = self.tracker.get_current_session()

        if current and current['category'] != 'stop':
            category_text = current['category']
            # Change color based on category
            if current['category'] == 'wasted':
                bg_color = '#8B4513'  # Brown for wasted time
                fg_color = '#ffffff'
            elif current['category'] == 'programming':
                bg_color = '#2E8B57'  # Sea green for programming
                fg_color = '#ffffff'
            else:
                bg_color = '#4682B4'  # Steel blue for other categories
                fg_color = '#ffffff'
        else:
            category_text = "No session"
            bg_color = '#2d2d2d'  # Dark gray for no session
            fg_color = '#888888'

        # Update label
        self.category_label.config(text=category_text, bg=bg_color, fg=fg_color)
        self.root.configure(bg=bg_color)

    def _update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                self._update_display()
                # Update every 10 seconds (just to catch external changes)
                threading.Event().wait(10)
            except Exception as e:
                print(f"Error updating overlay: {e}")
                threading.Event().wait(5)

    def start(self):
        """Start the overlay"""
        if self.running:
            return

        self.running = True

        # Initial display update
        self._update_display()

        # Start background update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

        # Start the GUI main loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the overlay"""
        self.running = False

        if self.root:
            self.root.quit()
            self.root.destroy()

if __name__ == "__main__":
    tracker = TimeTracker()
    overlay = MinimalOverlay(tracker)

    try:
        overlay.start()
    except KeyboardInterrupt:
        overlay.stop()