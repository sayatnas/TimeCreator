import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import calendar

class DailyStatsAnalyzer:
    def __init__(self, tracker):
        self.tracker = tracker

    def get_date_range(self, days_back: int = 365) -> Tuple[datetime, datetime]:
        """Get date range for analysis"""
        end_date = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = end_date - timedelta(days=days_back)
        return start_date, end_date

    def get_daily_totals(self, days_back: int = 365) -> Dict[str, Dict[str, float]]:
        """Get total hours per category per day using daily files"""
        start_date, end_date = self.get_date_range(days_back)
        daily_totals = {}

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_stats = self.tracker.get_daily_stats(date_str)
            if daily_stats:
                daily_totals[date_str] = daily_stats
            current_date += timedelta(days=1)

        return daily_totals

    def get_category_totals(self, days_back: int = 365) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive stats per category"""
        return self.tracker.get_category_totals(days_back)

    def get_productivity_calendar(self, days_back: int = 365) -> List[Dict[str, Any]]:
        """Generate calendar data with category breakdown for progress bars"""
        daily_totals = self.get_daily_totals(days_back)
        start_date, end_date = self.get_date_range(days_back)

        calendar_data = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_data = daily_totals.get(date_str, {})
            day_total = sum(day_data.values())

            # Create category segments for progress bar
            category_segments = []
            if day_total > 0:
                for category, hours in sorted(day_data.items(), key=lambda x: x[1], reverse=True):
                    if hours > 0:
                        percentage = (hours / day_total) * 100
                        category_segments.append({
                            'category': category,
                            'hours': hours,
                            'percentage': percentage
                        })

            calendar_data.append({
                'date': date_str,
                'total_hours': day_total,
                'categories': day_data,
                'category_segments': category_segments,
                'weekday': current_date.weekday(),
                'week_of_year': current_date.isocalendar()[1]
            })

            current_date += timedelta(days=1)

        return calendar_data

    def get_weekly_patterns(self) -> Dict[str, Dict[str, float]]:
        """Analyze patterns by day of week"""
        daily_totals = self.get_daily_totals()
        weekday_totals = defaultdict(lambda: defaultdict(list))

        for date_str, day_data in daily_totals.items():
            date = datetime.strptime(date_str, '%Y-%m-%d')
            weekday = date.strftime('%A')

            for category, hours in day_data.items():
                weekday_totals[weekday][category].append(hours)

        # Calculate averages
        weekday_averages = {}
        for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            weekday_averages[weekday] = {}
            for category, hours_list in weekday_totals[weekday].items():
                weekday_averages[weekday][category] = sum(hours_list) / len(hours_list) if hours_list else 0

        return weekday_averages

    def get_monthly_trends(self) -> Dict[str, Dict[str, float]]:
        """Get monthly trends for the past year"""
        daily_totals = self.get_daily_totals()
        monthly_totals = defaultdict(lambda: defaultdict(float))

        for date_str, day_data in daily_totals.items():
            month_key = date_str[:7]  # YYYY-MM
            for category, hours in day_data.items():
                monthly_totals[month_key][category] += hours

        return dict(monthly_totals)

    def get_productivity_insights(self) -> List[str]:
        """Generate productivity insights based on data"""
        insights = []
        category_stats = self.get_category_totals()
        daily_totals = self.get_daily_totals(30)  # Last 30 days
        weekly_patterns = self.get_weekly_patterns()

        # Total productivity
        total_hours = sum(stats['total_hours'] for stats in category_stats.values())
        if total_hours > 0:
            insights.append(f"You've tracked {total_hours:.1f} total hours across all categories")

        # Most productive category
        if category_stats:
            top_category = max(category_stats.items(), key=lambda x: x[1]['total_hours'])
            insights.append(f"Your most tracked activity is '{top_category[0]}' with {top_category[1]['total_hours']:.1f} hours")

        # Recent activity
        recent_days_with_data = len([d for d in daily_totals.values() if sum(d.values()) > 0])
        if recent_days_with_data > 0:
            insights.append(f"You've been active {recent_days_with_data} out of the last 30 days")

        # Best day of week
        best_weekday = None
        best_average = 0
        for weekday, categories in weekly_patterns.items():
            day_total = sum(categories.values())
            if day_total > best_average:
                best_average = day_total
                best_weekday = weekday

        if best_weekday and best_average > 0:
            insights.append(f"Your most productive day is {best_weekday} (avg {best_average:.1f}h)")

        # Wasted time analysis
        if 'wasted' in category_stats:
            wasted_total = category_stats['wasted']['total_hours']
            if wasted_total > 0:
                wasted_pct = (wasted_total / total_hours) * 100 if total_hours > 0 else 0
                insights.append(f"You've tracked {wasted_total:.1f}h as 'wasted' ({wasted_pct:.1f}% of total time)")

        # Consistency
        productive_categories = [cat for cat, stats in category_stats.items()
                               if cat not in ['wasted', 'stop'] and stats['total_hours'] > 0]
        if productive_categories:
            avg_days_active = sum(category_stats[cat]['days_active'] for cat in productive_categories) / len(productive_categories)
            insights.append(f"You're consistent! Average {avg_days_active:.1f} active days per category")

        # Current streak
        available_dates = sorted(self.tracker.list_available_dates())
        if available_dates:
            current_streak = 0
            today = datetime.now().strftime('%Y-%m-%d')

            # Check backwards from today
            current_date = datetime.now()
            while True:
                date_str = current_date.strftime('%Y-%m-%d')
                daily_stats = self.tracker.get_daily_stats(date_str)

                if sum(daily_stats.values()) > 0:
                    current_streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break

                # Don't go back too far
                if current_streak > 100:
                    break

            if current_streak > 0:
                insights.append(f"Current activity streak: {current_streak} days!")

        return insights

    def get_time_distribution(self) -> Dict[str, float]:
        """Get percentage distribution of time across categories"""
        category_stats = self.get_category_totals()
        total_hours = sum(stats['total_hours'] for stats in category_stats.values())

        if total_hours == 0:
            return {}

        distribution = {}
        for category, stats in category_stats.items():
            percentage = (stats['total_hours'] / total_hours) * 100
            distribution[category] = percentage

        return distribution

# Compatibility wrapper
class StatsAnalyzer(DailyStatsAnalyzer):
    """Compatibility wrapper for existing code"""
    pass