import tkinter as tk
from tkinter import font
from typing import Optional, Callable, List
from tracker import TimeTracker

class CategoryPicker:
    def __init__(self, tracker: TimeTracker, on_selection: Optional[Callable[[str], None]] = None):
        self.tracker = tracker
        self.on_selection = on_selection
        self.selected_category = None
        self.current_index = 0

        self.root = tk.Tk()
        self.root.withdraw()  # Hide initially
        self._setup_window()
        self._create_widgets()
        self._bind_events()

    def _setup_window(self):
        """Configure the main window"""
        self.root.title("TimeCreator - Select Category")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        self.root.configure(bg='#2d2d2d')

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.root.winfo_screenheight() // 2) - (200 // 2)
        self.root.geometry(f"300x200+{x}+{y}")

        # Window should be on top and focused
        self.root.attributes('-topmost', True)
        self.root.focus_force()

    def _create_widgets(self):
        """Create and layout widgets"""
        # Title
        title_font = font.Font(family="Consolas", size=12, weight="bold")
        title_label = tk.Label(
            self.root,
            text="Select Category",
            font=title_font,
            bg='#2d2d2d',
            fg='#ffffff'
        )
        title_label.pack(pady=(10, 5))

        # Current session info
        current = self.tracker.get_current_session()
        if current:
            duration = self.tracker.get_current_duration()
            if duration:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                time_str = f"{hours:02d}:{minutes:02d}"
                current_text = f"Current: {current['category']} ({time_str})"
            else:
                current_text = f"Current: {current['category']}"
        else:
            current_text = "No active session"

        current_font = font.Font(family="Consolas", size=9)
        current_label = tk.Label(
            self.root,
            text=current_text,
            font=current_font,
            bg='#2d2d2d',
            fg='#888888'
        )
        current_label.pack(pady=(0, 10))

        # Category listbox
        self.listbox = tk.Listbox(
            self.root,
            font=font.Font(family="Consolas", size=11),
            bg='#3d3d3d',
            fg='#ffffff',
            selectbackground='#4a9eff',
            selectforeground='#ffffff',
            activestyle='none',
            highlightthickness=0,
            bd=0
        )

        # Populate categories
        categories = self.tracker.get_categories()
        for category in categories:
            self.listbox.insert(tk.END, category)

        # Select first item
        if categories:
            self.listbox.selection_set(0)
            self.current_index = 0

        self.listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def _bind_events(self):
        """Bind keyboard and mouse events"""
        self.root.bind('<KeyPress>', self._on_keypress)
        self.root.bind('<Escape>', lambda e: self._close())
        self.root.bind('<Return>', lambda e: self._select_current())
        self.root.bind('<KP_Enter>', lambda e: self._select_current())

        self.listbox.bind('<Double-Button-1>', lambda e: self._select_current())
        self.listbox.bind('<<ListboxSelect>>', self._on_listbox_select)

        # Focus on listbox
        self.listbox.focus_set()

    def _on_keypress(self, event):
        """Handle keyboard navigation"""
        if event.keysym == 'Up':
            self._move_selection(-1)
            return 'break'
        elif event.keysym == 'Down':
            self._move_selection(1)
            return 'break'

    def _move_selection(self, direction):
        """Move selection up or down"""
        size = self.listbox.size()
        if size == 0:
            return

        self.current_index = (self.current_index + direction) % size
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.current_index)
        self.listbox.see(self.current_index)

    def _on_listbox_select(self, event):
        """Handle listbox selection change"""
        selection = self.listbox.curselection()
        if selection:
            self.current_index = selection[0]

    def _select_current(self):
        """Select the currently highlighted category"""
        selection = self.listbox.curselection()
        if selection:
            category = self.listbox.get(selection[0])
            self.selected_category = category
            if self.on_selection:
                self.on_selection(category)
        self._close()

    def _close(self):
        """Close the picker window"""
        self.root.quit()
        self.root.destroy()

    def show(self) -> Optional[str]:
        """Show the picker and return selected category"""
        self.root.deiconify()  # Show window
        self.root.mainloop()
        return self.selected_category

def show_category_picker(tracker: TimeTracker) -> Optional[str]:
    """Convenience function to show picker and return selection"""
    picker = CategoryPicker(tracker)
    return picker.show()

def quick_switch_category(tracker: TimeTracker, category: str = None):
    """Quick switch to category or show picker if none specified"""
    if category and category in tracker.get_categories():
        success = tracker.start_session(category)
        if success:
            print(f"Switched to: {category}")
        else:
            print(f"Failed to switch to: {category}")
    else:
        selected = show_category_picker(tracker)
        if selected:
            success = tracker.start_session(selected)
            if success:
                print(f"Switched to: {selected}")
            else:
                print(f"Failed to switch to: {selected}")

if __name__ == "__main__":
    # Test the picker
    tracker = TimeTracker()
    selected = show_category_picker(tracker)
    if selected:
        print(f"Selected: {selected}")
        tracker.start_session(selected)
    else:
        print("No selection made")