import os
import csv
from datetime import datetime


# =========================
# STATIC GYM DATABASE (mock)
# =========================

GYMS = [
    {"name": "FitZone Mumbai",        "location": "Andheri West",    "rating": 4.5, "specialty": ["weights", "cardio"],        "fee": "₹1500/month"},
    {"name": "Iron Paradise Gym",     "location": "Bandra",          "rating": 4.7, "specialty": ["bodybuilding", "weights"],  "fee": "₹2000/month"},
    {"name": "PowerHouse Fitness",    "location": "Borivali",        "rating": 4.2, "specialty": ["cardio", "crossfit"],       "fee": "₹1200/month"},
    {"name": "Flex Fitness Studio",   "location": "Malad",           "rating": 4.3, "specialty": ["yoga", "flexibility"],      "fee": "₹1800/month"},
    {"name": "Gold's Gym",            "location": "Goregaon",        "rating": 4.6, "specialty": ["weights", "bodybuilding"],  "fee": "₹2500/month"},
    {"name": "Cult.fit",              "location": "Thane",           "rating": 4.4, "specialty": ["crossfit", "cardio"],       "fee": "₹1999/month"},
    {"name": "Snap Fitness",          "location": "Dadar",           "rating": 4.1, "specialty": ["weights", "cardio"],        "fee": "₹1400/month"},
    {"name": "The Fitness Lab",       "location": "Powai",           "rating": 4.8, "specialty": ["bodybuilding", "weights"],  "fee": "₹3000/month"},
]


# =========================
# WORKOUT PROGRAMS
# =========================

PROGRAMS = {
    "beginner": {
        "label": "Beginner Strength Builder",
        "description": "3 days/week — focus on form and building base strength.",
        "schedule": [
            "Day 1: Bicep Curls 3x10, Squats 3x12",
            "Day 2: Rest / Light Walk",
            "Day 3: Shoulder Press 3x10, Lunges 3x12",
            "Day 4: Rest",
            "Day 5: Full Body Circuit — 2 rounds",
            "Day 6-7: Rest",
        ],
        "challenge": "Complete 4 consecutive weeks without skipping — earn 'Consistency Badge'! 🏅",
    },
    "intermediate": {
        "label": "Intermediate Hypertrophy Plan",
        "description": "4 days/week — increase reps and resistance progressively.",
        "schedule": [
            "Day 1: Bicep + Tricep — 4x12",
            "Day 2: Squats + Lunges — 4x15",
            "Day 3: Rest",
            "Day 4: Shoulder + Back — 4x12",
            "Day 5: Full Body HIIT — 20 min",
            "Day 6-7: Rest / Active Recovery",
        ],
        "challenge": "Increase your rep count by 20% over 4 weeks — track in Gym Trainer! 📈",
    },
    "advanced": {
        "label": "Advanced Performance Program",
        "description": "5 days/week — max intensity, periodisation.",
        "schedule": [
            "Day 1: Heavy Bicep + Chest — 5x8",
            "Day 2: Leg Day — Squats 5x10, Deadlifts 4x8",
            "Day 3: Active Recovery — Yoga / Stretch",
            "Day 4: Shoulder + Core — 5x10",
            "Day 5: Full Body Power Circuit",
            "Day 6: Cardio HIIT — 30 min",
            "Day 7: Complete Rest",
        ],
        "challenge": "Hit 30 reps per session for 3 weeks straight — aim for 'Increase Resistance' recommendation! 🔥",
    },
}


# =========================
# LOAD HISTORY FOR ANALYSIS
# =========================

def _load_history(base_path):
    path = os.path.join(base_path, "workout_history.csv")

    if not os.path.isfile(path):
        return []

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


# =========================
# RECOMMENDATION ENGINE
# =========================

def recommend(base_path):
    """Analyse workout history and return personalised recommendations.

    Returns a dict with:
    - level          : 'beginner' | 'intermediate' | 'advanced'
    - program        : recommended program dict
    - gyms           : top 3 gym suggestions
    - favourite_ex   : most-done exercise
    - insight        : short personalised insight string
    """

    rows = _load_history(base_path)

    total_sessions = len(rows)

    # ---- Determine fitness level from history ----
    if total_sessions == 0:
        level = "beginner"
        insight = "No history yet — starting you on the Beginner plan. Log a few sessions to get personalised recommendations!"

    else:
        try:
            avg_reps = sum(int(r.get("Reps", 0)) for r in rows) / total_sessions
        except (ValueError, ZeroDivisionError):
            avg_reps = 0

        high_rec = sum(1 for r in rows if "increase" in r.get("Recommendation", "").lower())
        high_rec_pct = high_rec / total_sessions if total_sessions else 0

        if total_sessions >= 15 and avg_reps >= 18 and high_rec_pct >= 0.5:
            level = "advanced"
            insight = (
                f"With {total_sessions} sessions and avg {round(avg_reps)} reps, "
                f"you're performing at an advanced level. Time to push harder!"
            )
        elif total_sessions >= 6 and avg_reps >= 10:
            level = "intermediate"
            insight = (
                f"You've logged {total_sessions} sessions with avg {round(avg_reps)} reps. "
                f"Intermediate plan will help you keep progressing."
            )
        else:
            level = "beginner"
            insight = (
                f"You're building a habit ({total_sessions} sessions logged). "
                f"Stick to the Beginner plan and focus on form."
            )

    # ---- Exercise preference ----
    if rows:
        ex_counts = {}
        for r in rows:
            ex = r.get("Exercise", "Unknown")
            ex_counts[ex] = ex_counts.get(ex, 0) + 1
        favourite_ex = max(ex_counts, key=ex_counts.get)
    else:
        favourite_ex = "Not enough data"

    # ---- Gym suggestions based on level ----
    if level == "advanced":
        preferred = ["bodybuilding", "weights"]
    elif level == "intermediate":
        preferred = ["weights", "crossfit"]
    else:
        preferred = ["cardio", "crossfit"]

    def gym_score(gym):
        match = sum(1 for s in gym["specialty"] if s in preferred)
        return match * 10 + gym["rating"] * 2

    sorted_gyms = sorted(GYMS, key=gym_score, reverse=True)[:3]

    return {
        "level":        level,
        "program":      PROGRAMS[level],
        "gyms":         sorted_gyms,
        "favourite_ex": favourite_ex,
        "insight":      insight,
    }