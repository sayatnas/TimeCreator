import tkinter as tk
from tkinter import font
from datetime import datetime, timedelta
import math
from typing import Dict, List, Any

from tracker_daily import TimeTracker
from stats_analyzer_daily import StatsAnalyzer

class MinimalStatsWindow:
    def __init__(self, tracker: TimeTracker):
        self.tracker = tracker
        self.analyzer = StatsAnalyzer(tracker)

        self.root = tk.Toplevel()
        self.root.title("TimeCreator Stats")
        self.root.state('zoomed')  # Maximize window on Windows
        self.root.configure(bg='#2d2d2d')
        self.root.resizable(True, True)

        # Define category colors
        self.category_colors = {
            'programming': '#2E8B57',     # Sea green
            'wasted': '#8B4513',          # Brown
            'Asset Creation': '#4682B4',  # Steel blue
            'Math': '#9370DB',            # Medium purple
            'stop': '#696969'             # Dim gray
        }

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        """Create horizontal layout for better screen utilization"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Activity Overview",
            font=font.Font(family="Segoe UI", size=18, weight="bold"),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        title_label.pack(pady=(20, 10))

        # Main horizontal container
        main_container = tk.Frame(self.root, bg='#2d2d2d')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Left column - Stats and graphs
        left_frame = tk.Frame(main_container, bg='#2d2d2d')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right column - Calendar and insights
        right_frame = tk.Frame(main_container, bg='#2d2d2d')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Left column content
        self._create_quick_stats(left_frame)
        self._create_line_graph(left_frame)
        self._create_recent_activity(left_frame)

        # Right column content
        self._create_activity_calendar(right_frame)
        self._create_category_breakdown(right_frame)
        self._create_insights(right_frame)

    def _create_quick_stats(self, parent):
        """Create minimalistic quick stats"""
        stats_frame = tk.Frame(parent, bg='#3d3d3d', relief=tk.FLAT, bd=1)
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            stats_frame,
            text="Total Time Tracked",
            font=font.Font(family="Segoe UI", size=12, weight="bold"),
            bg='#3d3d3d',
            fg='#ffffff'
        ).pack(pady=(15, 5))

        self.total_time_label = tk.Label(
            stats_frame,
            text="0.0 hours",
            font=font.Font(family="Segoe UI", size=24, weight="bold"),
            bg='#3d3d3d',
            fg='#4a9eff'
        )
        self.total_time_label.pack(pady=(0, 15))

    def _create_line_graph(self, parent):
        """Create line graph showing past 10 days for each category"""
        graph_frame = tk.Frame(parent, bg='#3d3d3d', relief=tk.FLAT, bd=1)
        graph_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            graph_frame,
            text="10-Day Trend",
            font=font.Font(family="Segoe UI", size=14, weight="bold"),
            bg='#3d3d3d',
            fg='#ffffff'
        ).pack(pady=(15, 10))

        # Canvas for the graph
        self.graph_canvas = tk.Canvas(
            graph_frame,
            width=450,
            height=200,
            bg='#2d2d2d',
            highlightthickness=0
        )
        self.graph_canvas.pack(pady=(0, 15))

    def _draw_line_graph(self):
        """Draw the 10-day trend line graph"""
        self.graph_canvas.delete("all")

        # Get data for past 10 days
        daily_data = {}
        for i in range(10):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            daily_stats = self.analyzer.tracker.get_daily_stats(date_str)
            daily_data[date_str] = daily_stats

        # Reverse to have oldest first
        dates = sorted(daily_data.keys())

        # Canvas dimensions
        canvas_width = 450
        canvas_height = 200
        margin = 40
        legend_width = 100
        graph_width = canvas_width - 2 * margin - legend_width
        graph_height = canvas_height - 2 * margin

        # Find max hours for scaling
        max_hours = 0
        for date_data in daily_data.values():
            day_total = sum(date_data.values())
            max_hours = max(max_hours, day_total)

        if max_hours == 0:
            max_hours = 1  # Prevent division by zero

        # Draw axes (adjusted for legend space)
        graph_end_x = margin + graph_width
        self.graph_canvas.create_line(margin, margin, margin, canvas_height - margin, fill='#666666', width=2)
        self.graph_canvas.create_line(margin, canvas_height - margin, graph_end_x, canvas_height - margin, fill='#666666', width=2)

        # Y-axis labels (hours)
        for i in range(5):
            y = canvas_height - margin - (i * graph_height / 4)
            hours = (i * max_hours / 4)
            self.graph_canvas.create_text(margin - 10, y, text=f"{hours:.1f}h", fill='#888888', anchor='e', font=('Segoe UI', 8))
            self.graph_canvas.create_line(margin - 5, y, margin, y, fill='#666666')

        # X-axis labels (dates)
        for i, date in enumerate(dates):
            x = margin + (i * graph_width / (len(dates) - 1)) if len(dates) > 1 else margin + graph_width / 2
            day = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d')
            self.graph_canvas.create_text(x, canvas_height - margin + 15, text=day, fill='#888888', font=('Segoe UI', 8))

        # Draw lines for each category
        categories = set()
        for date_data in daily_data.values():
            categories.update(date_data.keys())

        for category in categories:
            if category == 'stop':
                continue

            color = self.category_colors.get(category, '#4682B4')
            points = []

            for i, date in enumerate(dates):
                x = margin + (i * graph_width / (len(dates) - 1)) if len(dates) > 1 else margin + graph_width / 2
                hours = daily_data[date].get(category, 0)
                y = canvas_height - margin - (hours / max_hours * graph_height)
                points.extend([x, y])

                # Draw point
                self.graph_canvas.create_oval(x-3, y-3, x+3, y+3, fill=color, outline=color)

            # Draw line
            if len(points) >= 4:  # Need at least 2 points
                self.graph_canvas.create_line(points, fill=color, width=2, smooth=False)

        # Legend (positioned to the right of the graph)
        legend_x = graph_end_x + 20
        legend_y = margin + 10
        for i, category in enumerate(categories):
            if category == 'stop':
                continue
            color = self.category_colors.get(category, '#4682B4')
            y = legend_y + i * 20
            self.graph_canvas.create_rectangle(legend_x, y, legend_x + 12, y + 12, fill=color, outline=color)
            self.graph_canvas.create_text(legend_x + 16, y + 6, text=category, fill='#ffffff', anchor='w', font=('Segoe UI', 8))

    def _create_recent_activity(self, parent):
        """Create recent activity breakdown by category"""
        recent_frame = tk.Frame(parent, bg='#3d3d3d', relief=tk.FLAT, bd=1)
        recent_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            recent_frame,
            text="Last 7 Days",
            font=font.Font(family="Segoe UI", size=14, weight="bold"),
            bg='#3d3d3d',
            fg='#ffffff'
        ).pack(pady=(15, 10))

        self.recent_content = tk.Frame(recent_frame, bg='#3d3d3d')
        self.recent_content.pack(fill=tk.X, padx=20, pady=(0, 15))

    def _create_activity_calendar(self, parent):
        """Create expanded activity calendar with category details"""
        calendar_frame = tk.Frame(parent, bg='#3d3d3d', relief=tk.FLAT, bd=1)
        calendar_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Header with navigation
        header_frame = tk.Frame(calendar_frame, bg='#3d3d3d')
        header_frame.pack(fill=tk.X, pady=(15, 10))

        self.current_month = datetime.now().replace(day=1)

        self.prev_button = tk.Button(
            header_frame,
            text="←",
            font=font.Font(family="Segoe UI", size=12, weight="bold"),
            bg='#4a9eff',
            fg='#ffffff',
            bd=0,
            command=self._prev_month
        )
        self.prev_button.pack(side=tk.LEFT, padx=(20, 10))

        self.month_label = tk.Label(
            header_frame,
            text="Activity Calendar",
            font=font.Font(family="Segoe UI", size=14, weight="bold"),
            bg='#3d3d3d',
            fg='#ffffff'
        )
        self.month_label.pack(side=tk.LEFT, expand=True)

        self.next_button = tk.Button(
            header_frame,
            text="→",
            font=font.Font(family="Segoe UI", size=12, weight="bold"),
            bg='#4a9eff',
            fg='#ffffff',
            bd=0,
            command=self._next_month
        )
        self.next_button.pack(side=tk.RIGHT, padx=(10, 20))

        self.calendar_content = tk.Frame(calendar_frame, bg='#3d3d3d')
        self.calendar_content.pack(fill=tk.X, padx=20, pady=(0, 15))

        # Legend
        legend_frame = tk.Frame(calendar_frame, bg='#3d3d3d')
        legend_frame.pack(pady=(0, 15))

        tk.Label(legend_frame, text="Categories: ", bg='#3d3d3d', fg='#888888', font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(20, 10))

        # Category legend
        for category, color in self.category_colors.items():
            if category != 'stop':
                cat_frame = tk.Frame(legend_frame, bg='#3d3d3d')
                cat_frame.pack(side=tk.LEFT, padx=5)

                square = tk.Frame(cat_frame, width=10, height=10, bg=color, relief=tk.RAISED, bd=1)
                square.pack(side=tk.LEFT, padx=(0, 3))

                tk.Label(cat_frame, text=category, bg='#3d3d3d', fg='#888888', font=("Segoe UI", 8)).pack(side=tk.LEFT)

    def _create_category_breakdown(self, parent):
        """Create category time breakdown"""
        category_frame = tk.Frame(parent, bg='#3d3d3d', relief=tk.FLAT, bd=1)
        category_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            category_frame,
            text="Time by Category",
            font=font.Font(family="Segoe UI", size=14, weight="bold"),
            bg='#3d3d3d',
            fg='#ffffff'
        ).pack(pady=(15, 10))

        self.category_content = tk.Frame(category_frame, bg='#3d3d3d')
        self.category_content.pack(fill=tk.X, padx=20, pady=(0, 15))

    def _create_insights(self, parent):
        """Create productivity insights section"""
        insights_frame = tk.Frame(parent, bg='#3d3d3d', relief=tk.FLAT, bd=1)
        insights_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            insights_frame,
            text="Insights",
            font=font.Font(family="Segoe UI", size=14, weight="bold"),
            bg='#3d3d3d',
            fg='#ffffff'
        ).pack(pady=(15, 10))

        self.insights_content = tk.Frame(insights_frame, bg='#3d3d3d')
        self.insights_content.pack(fill=tk.X, padx=20, pady=(0, 15))

    def _load_data(self):
        """Load and display all data"""
        self._load_quick_stats()
        self._draw_line_graph()
        self._load_recent_activity()
        self._load_calendar()
        self._load_category_breakdown()
        self._load_insights()

    def _prev_month(self):
        """Navigate to previous month"""
        if self.current_month.month == 1:
            self.current_month = self.current_month.replace(year=self.current_month.year - 1, month=12)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month - 1)
        self._update_calendar()

    def _next_month(self):
        """Navigate to next month"""
        if self.current_month.month == 12:
            self.current_month = self.current_month.replace(year=self.current_month.year + 1, month=1)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month + 1)
        self._update_calendar()

    def _update_calendar(self):
        """Update calendar display for current month"""
        # Clear existing calendar
        for widget in self.calendar_content.winfo_children():
            widget.destroy()

        # Update month label
        month_name = self.current_month.strftime('%B %Y')
        self.month_label.config(text=f"Activity Calendar - {month_name}")

        # Load calendar for current month
        self._load_calendar()

    def _create_category_color_mix(self, categories_data):
        """Create a mixed color representing category distribution"""
        if not categories_data or sum(categories_data.values()) == 0:
            return '#2d2d2d'  # Empty day color

        total_hours = sum(categories_data.values())

        # Calculate weighted average of colors
        r, g, b = 0, 0, 0
        for category, hours in categories_data.items():
            if hours > 0 and category in self.category_colors:
                color = self.category_colors[category]
                # Convert hex to RGB
                hex_color = color.lstrip('#')
                cat_r = int(hex_color[0:2], 16)
                cat_g = int(hex_color[2:4], 16)
                cat_b = int(hex_color[4:6], 16)

                # Weight by hours
                weight = hours / total_hours
                r += cat_r * weight
                g += cat_g * weight
                b += cat_b * weight

        # Convert back to hex, with intensity based on total hours
        intensity = min(1.0, total_hours / 4.0)  # Max intensity at 4 hours
        r = int(r * intensity + 45 * (1 - intensity))  # Blend with dark background
        g = int(g * intensity + 45 * (1 - intensity))
        b = int(b * intensity + 45 * (1 - intensity))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _load_quick_stats(self):
        """Load total time"""
        category_stats = self.analyzer.get_category_totals()
        total_hours = sum(stats['total_hours'] for stats in category_stats.values())
        self.total_time_label.config(text=f"{total_hours:.1f} hours")

    def _load_recent_activity(self):
        """Load recent activity by category"""
        daily_totals = self.analyzer.get_daily_totals(7)

        # Create day headers
        header_frame = tk.Frame(self.recent_content, bg='#3d3d3d')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Day labels - show actual dates
        tk.Label(header_frame, text="", bg='#3d3d3d', width=12).pack(side=tk.LEFT)  # Category column
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            day_text = f"{date.strftime('%a')}\n{date.day}"
            tk.Label(
                header_frame,
                text=day_text,
                font=("Segoe UI", 8, "bold"),
                bg='#3d3d3d',
                fg='#cccccc',
                width=8,
                justify=tk.CENTER
            ).pack(side=tk.LEFT)

        # Get all categories that have been used
        all_categories = set()
        for day_data in daily_totals.values():
            all_categories.update(day_data.keys())

        # Create rows for each category
        for category in sorted(all_categories):
            if category == 'stop':
                continue

            cat_frame = tk.Frame(self.recent_content, bg='#3d3d3d')
            cat_frame.pack(fill=tk.X, pady=2)

            # Category name
            cat_color = self.category_colors.get(category, '#4682B4')
            tk.Label(
                cat_frame,
                text=category,
                font=("Segoe UI", 10),
                bg='#3d3d3d',
                fg=cat_color,
                width=12,
                anchor='w'
            ).pack(side=tk.LEFT)

            # Daily values - show last 7 days ending with today
            for i in range(7):
                date = datetime.now() - timedelta(days=6-i)
                date_str = date.strftime('%Y-%m-%d')
                hours = daily_totals.get(date_str, {}).get(category, 0)

                # Debug: print what we're showing
                # print(f"Day {i}: {date.strftime('%A %Y-%m-%d')} -> {hours:.1f}h for {category}")

                tk.Label(
                    cat_frame,
                    text=f"{hours:.1f}h" if hours > 0 else "-",
                    font=("Consolas", 9),
                    bg='#3d3d3d',
                    fg='#ffffff' if hours > 0 else '#666666',
                    width=8
                ).pack(side=tk.LEFT)

    def _load_calendar(self):
        """Load monthly calendar with progress bar category distribution"""
        import calendar as cal

        # Get calendar data with category segments
        calendar_data = self.analyzer.get_productivity_calendar(365)

        # Create lookup for calendar data by date
        calendar_lookup = {item['date']: item for item in calendar_data}

        # Create calendar grid
        calendar_grid = tk.Frame(self.calendar_content, bg='#3d3d3d')
        calendar_grid.pack(expand=True)

        # Day headers
        days_header = tk.Frame(calendar_grid, bg='#3d3d3d')
        days_header.pack(fill=tk.X, pady=(0, 10))

        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for day_name in day_names:
            tk.Label(
                days_header,
                text=day_name,
                font=("Segoe UI", 10, "bold"),
                bg='#3d3d3d',
                fg='#cccccc',
                width=8
            ).pack(side=tk.LEFT, padx=2)

        # Get calendar data for current month
        month_calendar = cal.monthcalendar(self.current_month.year, self.current_month.month)

        # Create calendar rows
        for week in month_calendar:
            week_frame = tk.Frame(calendar_grid, bg='#3d3d3d')
            week_frame.pack(fill=tk.X, pady=2)

            for day_num in week:
                if day_num == 0:
                    # Empty day from previous/next month
                    empty_frame = tk.Frame(week_frame, width=65, height=50, bg='#2d2d2d')
                    empty_frame.pack(side=tk.LEFT, padx=2, pady=1)
                    empty_frame.pack_propagate(False)
                else:
                    # Actual day
                    date_str = f"{self.current_month.year:04d}-{self.current_month.month:02d}-{day_num:02d}"
                    day_info = calendar_lookup.get(date_str, {
                        'date': date_str,
                        'total_hours': 0,
                        'categories': {},
                        'category_segments': []
                    })

                    # Create day container (increased size for text below)
                    container_height = 85 if day_info['total_hours'] > 0 else 50
                    container_width = 65
                    # More transparent background
                    container_bg = '#1a1a1a' if day_info['total_hours'] > 0 else '#252525'
                    day_container = tk.Frame(week_frame, width=container_width, height=container_height, bg=container_bg, relief=tk.FLAT, bd=1)
                    day_container.pack(side=tk.LEFT, padx=2, pady=1)
                    day_container.pack_propagate(False)

                    # Day number label
                    day_label = tk.Label(
                        day_container,
                        text=str(day_num),
                        font=("Segoe UI", 8, "bold" if day_info['total_hours'] > 0 else "normal"),
                        bg=container_bg,
                        fg='#ffffff' if day_info['total_hours'] > 0 else '#666666'
                    )
                    day_label.pack(pady=(2, 0))

                    # Progress bar area
                    progress_frame = tk.Frame(day_container, bg=container_bg, height=20)
                    progress_frame.pack(fill=tk.X, padx=3, pady=(1, 0))
                    progress_frame.pack_propagate(False)

                    # Create progress bar segments
                    if day_info['category_segments']:
                        segments_frame = tk.Frame(progress_frame, bg=container_bg, height=20)
                        segments_frame.pack(fill=tk.BOTH, expand=True)

                        # Calculate segment widths (total width ~44px)
                        total_width = 44
                        current_x = 0

                        for segment in day_info['category_segments']:
                            category = segment['category']
                            percentage = segment['percentage']
                            segment_width = max(1, int((percentage / 100) * total_width))

                            # Get category color
                            color = self.category_colors.get(category, '#4682B4')

                            # Create segment
                            segment_frame = tk.Frame(
                                segments_frame,
                                width=segment_width,
                                height=20,
                                bg=color
                            )
                            segment_frame.place(x=current_x, y=0)
                            segment_frame.pack_propagate(False)

                            current_x += segment_width

                        # Fill remaining space with dark background if needed
                        if current_x < total_width:
                            remaining_frame = tk.Frame(
                                segments_frame,
                                width=total_width - current_x,
                                height=20,
                                bg='#1d1d1d'
                            )
                            remaining_frame.place(x=current_x, y=0)

                    # Shorthand category text below progress bar
                    if day_info['total_hours'] > 0:
                        text_frame = tk.Frame(day_container, bg=container_bg, height=25)
                        text_frame.pack(fill=tk.X, padx=1, pady=(1, 2))
                        text_frame.pack_propagate(False)

                        # Create shorthand text - use line breaks for better fit
                        shorthand_lines = []
                        current_line = []
                        current_length = 0

                        for segment in day_info['category_segments']:
                            cat = segment['category']
                            hours = segment['hours']

                            # Create shorter category names
                            short_names = {
                                'programming': 'prg',
                                'Asset Creation': 'ast',
                                'Math': 'mth',
                                'wasted': 'wst',
                                'stop': 'stp'
                            }
                            short_cat = short_names.get(cat, cat[:3])

                            # Format time (show minutes if less than 1 hour)
                            if hours >= 1:
                                time_str = f"{hours:.1f}h"
                            else:
                                minutes = int(hours * 60)
                                time_str = f"{minutes}m"

                            part = f"{short_cat}:{time_str}"

                            # Check if we need a new line (keep lines under 8 chars)
                            if current_length + len(part) + 1 > 8 and current_line:
                                shorthand_lines.append(" ".join(current_line))
                                current_line = [part]
                                current_length = len(part)
                            else:
                                current_line.append(part)
                                current_length += len(part) + (1 if current_line else 0)

                        if current_line:
                            shorthand_lines.append(" ".join(current_line))

                        # Limit to 2 lines max
                        if len(shorthand_lines) > 2:
                            shorthand_lines = shorthand_lines[:2]

                        shorthand_text = "\n".join(shorthand_lines)

                        tk.Label(
                            text_frame,
                            text=shorthand_text,
                            font=("Consolas", 8),
                            bg='#2d2d2d',
                            fg='#cccccc',
                            justify=tk.CENTER
                        ).pack(expand=True)

                    # Tooltip with detailed breakdown
                    if day_info['total_hours'] > 0:
                        tooltip_text = f"{date_str}: {day_info['total_hours']:.1f}h total\n"
                        for segment in day_info['category_segments']:
                            cat = segment['category']
                            hours = segment['hours']
                            pct = segment['percentage']
                            tooltip_text += f"  {cat}: {hours:.1f}h ({pct:.1f}%)\n"
                        tooltip_text = tooltip_text.strip()

                        self._create_tooltip(day_container, tooltip_text)
                        self._create_tooltip(day_label, tooltip_text)
                        self._create_tooltip(progress_frame, tooltip_text)

    def _load_category_breakdown(self):
        """Load category breakdown with visual bars"""
        category_stats = self.analyzer.get_category_totals()
        distribution = self.analyzer.get_time_distribution()

        if not category_stats:
            tk.Label(
                self.category_content,
                text="No data available",
                font=("Segoe UI", 11),
                bg='#3d3d3d',
                fg='#888888'
            ).pack()
            return

        # Sort categories by total hours
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['total_hours'], reverse=True)

        for category, stats in sorted_categories:
            if category == 'stop' or stats['total_hours'] == 0:
                continue

            cat_frame = tk.Frame(self.category_content, bg='#3d3d3d')
            cat_frame.pack(fill=tk.X, pady=5)

            # Category info frame
            info_frame = tk.Frame(cat_frame, bg='#3d3d3d')
            info_frame.pack(fill=tk.X)

            # Category name and color
            cat_color = self.category_colors.get(category, '#4682B4')
            color_square = tk.Frame(info_frame, width=12, height=12, bg=cat_color)
            color_square.pack(side=tk.LEFT, padx=(0, 10), pady=6)
            color_square.pack_propagate(False)

            # Category details
            details_frame = tk.Frame(info_frame, bg='#3d3d3d')
            details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Name and total hours
            name_frame = tk.Frame(details_frame, bg='#3d3d3d')
            name_frame.pack(fill=tk.X)

            tk.Label(
                name_frame,
                text=category,
                font=("Segoe UI", 12, "bold"),
                bg='#3d3d3d',
                fg='#ffffff',
                anchor='w'
            ).pack(side=tk.LEFT)

            tk.Label(
                name_frame,
                text=f"{stats['total_hours']:.1f}h",
                font=("Segoe UI", 12),
                bg='#3d3d3d',
                fg='#4a9eff',
                anchor='e'
            ).pack(side=tk.RIGHT)

            # Percentage and average
            stats_frame = tk.Frame(details_frame, bg='#3d3d3d')
            stats_frame.pack(fill=tk.X)

            percentage = distribution.get(category, 0)

            # Percentage
            tk.Label(
                stats_frame,
                text=f"{percentage:.1f}%",
                font=("Segoe UI", 9),
                bg='#3d3d3d',
                fg='#888888',
                anchor='w'
            ).pack(side=tk.LEFT)

            # Separator
            tk.Label(
                stats_frame,
                text=" • Avg: ",
                font=("Segoe UI", 9),
                bg='#3d3d3d',
                fg='#888888'
            ).pack(side=tk.LEFT)

            # Average per day (highlighted)
            tk.Label(
                stats_frame,
                text=f"{stats['average_per_day']:.1f}h/day",
                font=("Segoe UI", 10, "bold"),
                bg='#3d3d3d',
                fg='#4a9eff',  # Bright blue to stand out
                anchor='w'
            ).pack(side=tk.LEFT)

    def _load_insights(self):
        """Load productivity insights"""
        insights = self.analyzer.get_productivity_insights()

        if not insights:
            tk.Label(
                self.insights_content,
                text="Use TimeCreator more to get insights",
                font=("Segoe UI", 11),
                bg='#3d3d3d',
                fg='#888888'
            ).pack()
            return

        for insight in insights:
            insight_frame = tk.Frame(self.insights_content, bg='#3d3d3d')
            insight_frame.pack(fill=tk.X, pady=3)

            # Bullet point
            tk.Label(
                insight_frame,
                text="•",
                font=("Segoe UI", 12),
                bg='#3d3d3d',
                fg='#4a9eff'
            ).pack(side=tk.LEFT, padx=(0, 8))

            # Insight text
            tk.Label(
                insight_frame,
                text=insight,
                font=("Segoe UI", 11),
                bg='#3d3d3d',
                fg='#ffffff',
                anchor='w',
                justify=tk.LEFT,
                wraplength=700
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(
                tooltip,
                text=text,
                background="#2d2d2d",
                foreground="#ffffff",
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", 9),
                justify=tk.LEFT
            )
            label.pack()

            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

def show_minimal_stats_window(tracker: TimeTracker):
    """Show the minimal stats window"""
    try:
        stats_window = MinimalStatsWindow(tracker)
        return stats_window
    except Exception as e:
        print(f"Error opening stats window: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test the minimal stats window
    from tracker_daily import TimeTracker
    tracker = TimeTracker()
    show_minimal_stats_window(tracker)