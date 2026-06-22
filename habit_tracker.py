import os
import csv
from datetime import datetime, date


def load_workout_dates(base_path):
    """Read workout_history.csv and return a sorted list of unique workout
    dates (as date objects). Returns an empty list if no history exists."""

    history_path = os.path.join(base_path, "workout_history.csv")

    if not os.path.isfile(history_path):
        return []

    with open(history_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    dates = []

    for row in rows:
        try:
            dt = datetime.strptime(row["Date"], "%Y-%m-%d %H:%M").date()
            dates.append(dt)
        except (KeyError, ValueError):
            continue

    return sorted(set(dates))


def analyze_behavior(base_path):
    """Simple behavioral analysis on workout history.

    Predicts skip-risk based on the gap since the last workout vs the
    user's average gap, and detects whether engagement is rising or
    falling. Returns a dict with status, stats, a nudge message, and a
    schedule suggestion.
    """

    unique_dates = load_workout_dates(base_path)

    if len(unique_dates) == 0:
        return {
            "status": "no_data",
            "nudge": "No workouts logged yet. Start your first session today! 💪",
            "schedule_suggestion": "Begin with 2-3 sessions this week to build a baseline.",
        }

    today = date.today()
    last_date = unique_dates[-1]
    days_since_last = (today - last_date).days

    if len(unique_dates) == 1:
        return {
            "status": "baseline",
            "days_since_last": days_since_last,
            "nudge": "Great start! Log a few more workouts so patterns can be learned. 🌱",
            "schedule_suggestion": "Aim for your next session within 2-3 days to build consistency.",
        }

    # average gap between consecutive workout days
    gaps = [
        (unique_dates[i] - unique_dates[i - 1]).days
        for i in range(1, len(unique_dates))
    ]
    avg_gap = sum(gaps) / len(gaps)

    # risk level: how overdue is the next workout vs the user's own habit
    if days_since_last <= avg_gap:
        risk_level = "on_track"
    elif days_since_last <= avg_gap * 1.5:
        risk_level = "slipping"
    else:
        risk_level = "high_risk"

    # engagement trend: last 7 days vs the 7 days before that
    recent_count = sum(1 for d in unique_dates if (today - d).days <= 7)
    prior_count = sum(1 for d in unique_dates if 7 < (today - d).days <= 14)

    if recent_count > prior_count:
        trend = "increasing"
    elif recent_count < prior_count:
        trend = "decreasing"
    else:
        trend = "stable"

    # nudge message
    if risk_level == "high_risk":
        nudge = (
            f"⚠️ It's been {days_since_last} days since your last workout — "
            f"your streak is at risk! A quick session today keeps you on track."
        )
    elif risk_level == "slipping":
        nudge = (
            f"⏳ {days_since_last} days since your last workout. "
            f"You're usually back by now — don't break the habit!"
        )
    else:
        nudge = "✅ You're on track! Keep up the consistency."

    # schedule adjustment suggestion
    if risk_level == "high_risk":
        schedule_suggestion = "Reduce friction: schedule a short 10-15 min session today to restart momentum."
    elif trend == "decreasing":
        schedule_suggestion = "Engagement is dipping — try shorter, more frequent sessions (e.g. 3x this week) instead of longer ones."
    elif trend == "increasing" and risk_level == "on_track":
        schedule_suggestion = "You're consistent and ramping up — consider increasing reps or resistance next session."
    else:
        schedule_suggestion = "Maintain your current schedule — it's working well."

    return {
        "status": risk_level,
        "days_since_last": days_since_last,
        "avg_gap": round(avg_gap, 1),
        "trend": trend,
        "nudge": nudge,
        "schedule_suggestion": schedule_suggestion,
    }