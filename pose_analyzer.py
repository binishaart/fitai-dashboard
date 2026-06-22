import os
import csv
from datetime import datetime, date, timedelta


# =========================
# LOAD WORKOUT HISTORY
# =========================

def load_history(base_path):
    """Load all rows from workout_history.csv as list of dicts."""

    history_path = os.path.join(base_path, "workout_history.csv")

    if not os.path.isfile(history_path):
        return []

    with open(history_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    return rows


# =========================
# PERFORMANCE SCORE (per session)
# =========================

def score_session(row):
    """Score a single workout session out of 100.

    Factors:
    - Reps completed        (0-50 pts)
    - Recommendation level  (0-50 pts)
    """

    try:
        reps = int(row.get("Reps", 0))
    except ValueError:
        reps = 0

    recommendation = row.get("Recommendation", "").lower()

    # Reps score: capped at 30 reps = full 50 pts
    reps_score = min(reps / 30, 1.0) * 50

    # Recommendation score
    if "increase" in recommendation:
        rec_score = 50   # doing very well
    elif "maintain" in recommendation:
        rec_score = 35   # decent
    else:
        rec_score = 15   # needs improvement

    return round(reps_score + rec_score)


# =========================
# WEEKLY PROGRESS REPORT
# =========================

def weekly_report(base_path):
    """Generate a weekly performance summary.

    Returns a dict with:
    - weeks         : list of week-label strings
    - avg_scores    : average performance score per week
    - session_counts: number of sessions per week
    - best_week     : label of best-performing week
    - trend         : 'improving' | 'declining' | 'stable'
    - all_sessions  : list of (date_str, exercise, reps, score) for table
    """

    rows = load_history(base_path)

    if not rows:
        return None

    # Tag each row with its score and week label
    tagged = []

    for row in rows:
        try:
            dt = datetime.strptime(row["Date"], "%Y-%m-%d %H:%M")
        except (KeyError, ValueError):
            continue

        # ISO week label e.g. "2026-W25"
        week_label = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
        session_score = score_session(row)

        tagged.append({
            "date":    dt.strftime("%Y-%m-%d"),
            "week":    week_label,
            "exercise": row.get("Exercise", ""),
            "reps":    row.get("Reps", "0"),
            "score":   session_score,
        })

    if not tagged:
        return None

    # Group by week
    week_data = {}

    for t in tagged:
        w = t["week"]
        if w not in week_data:
            week_data[w] = {"scores": [], "count": 0}
        week_data[w]["scores"].append(t["score"])
        week_data[w]["count"] += 1

    weeks          = sorted(week_data.keys())
    avg_scores     = [round(sum(week_data[w]["scores"]) / len(week_data[w]["scores"])) for w in weeks]
    session_counts = [week_data[w]["count"] for w in weeks]

    best_week = weeks[avg_scores.index(max(avg_scores))]

    # Trend: compare last two weeks if available
    if len(avg_scores) >= 2:
        diff = avg_scores[-1] - avg_scores[-2]
        if diff >= 5:
            trend = "improving"
        elif diff <= -5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return {
        "weeks":          weeks,
        "avg_scores":     avg_scores,
        "session_counts": session_counts,
        "best_week":      best_week,
        "trend":          trend,
        "all_sessions":   tagged,
    }