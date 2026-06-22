import random
import time
import os
import csv
from datetime import datetime


# =========================
# MOCK IoT SENSOR READINGS
# =========================

def read_heart_rate(reps=0):
    """Simulate a heart rate sensor.
    Base rate increases with rep count (more reps = more effort)."""

    base = 72
    effort_boost = min(reps * 2, 60)   # cap boost at 60 bpm
    noise = random.randint(-5, 5)

    return base + effort_boost + noise


def read_resistance_level():
    """Simulate a resistance/weight sensor on smart equipment.
    Returns current resistance as kg (5-100 kg range)."""

    return random.choice([5, 10, 15, 20, 25, 30, 40, 50, 60])


def read_equipment_temp():
    """Simulate an equipment temperature sensor (in Celsius).
    Higher temp = equipment has been used a lot = suggest rest."""

    return round(random.uniform(28.0, 48.0), 1)


def read_rest_timer():
    """Simulate how many seconds since last rep set ended."""
    return random.randint(10, 120)


def get_sensor_readings(reps=0):
    """Return a dict of all simulated IoT sensor values."""

    return {
        "heart_rate":       read_heart_rate(reps),
        "resistance_kg":    read_resistance_level(),
        "equipment_temp_c": read_equipment_temp(),
        "rest_seconds":     read_rest_timer(),
        "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# =========================
# AI RECOMMENDATION ENGINE
# =========================

def analyze_sensors(readings):
    """Rule-based AI that analyses IoT sensor readings and returns:
    - intensity_status  : 'low' | 'optimal' | 'high'
    - rest_status       : 'insufficient' | 'adequate' | 'too_long'
    - equipment_status  : 'cool' | 'warm' | 'overheated'
    - recommendations   : list of actionable suggestion strings
    - overall_score     : 0-100 (session quality estimate)
    """

    hr   = readings["heart_rate"]
    res  = readings["resistance_kg"]
    temp = readings["equipment_temp_c"]
    rest = readings["rest_seconds"]

    recommendations = []
    score_parts = []

    # ---- Heart Rate / Intensity ----
    if hr < 90:
        intensity_status = "low"
        recommendations.append(
            f"Heart rate ({hr} bpm) is low — increase resistance or pace to enter fat-burn zone."
        )
        score_parts.append(40)

    elif hr <= 150:
        intensity_status = "optimal"
        recommendations.append(
            f"Heart rate ({hr} bpm) is in the optimal training zone. Keep it up! ✅"
        )
        score_parts.append(100)

    else:
        intensity_status = "high"
        recommendations.append(
            f"Heart rate ({hr} bpm) is very high — slow down or take a 60-sec rest immediately. ⚠️"
        )
        score_parts.append(30)

    # ---- Resistance ----
    if res < 10:
        recommendations.append(
            f"Resistance ({res} kg) is very light — consider increasing for better muscle activation."
        )
        score_parts.append(50)
    elif res <= 40:
        recommendations.append(
            f"Resistance ({res} kg) is well-suited for your current session. 💪"
        )
        score_parts.append(100)
    else:
        recommendations.append(
            f"Resistance ({res} kg) is heavy — ensure form is correct to avoid injury."
        )
        score_parts.append(70)

    # ---- Equipment Temperature ----
    if temp < 32:
        equipment_status = "cool"
        recommendations.append(
            f"Equipment temp ({temp}°C) is normal — no overheating concerns."
        )
        score_parts.append(100)
    elif temp <= 42:
        equipment_status = "warm"
        recommendations.append(
            f"Equipment temp ({temp}°C) is warm — take a short break if continuing long session."
        )
        score_parts.append(75)
    else:
        equipment_status = "overheated"
        recommendations.append(
            f"⚠️ Equipment temp ({temp}°C) is high — rest the equipment for 5 mins before continuing."
        )
        score_parts.append(20)

    # ---- Rest Between Sets ----
    if rest < 30:
        rest_status = "insufficient"
        recommendations.append(
            f"Only {rest}s rest between sets — aim for at least 45-60s for muscle recovery."
        )
        score_parts.append(50)
    elif rest <= 90:
        rest_status = "adequate"
        recommendations.append(
            f"Rest period ({rest}s) is adequate for your current intensity. ✅"
        )
        score_parts.append(100)
    else:
        rest_status = "too_long"
        recommendations.append(
            f"Rest period ({rest}s) is too long — muscles cooling down. Start next set now!"
        )
        score_parts.append(60)

    overall_score = int(sum(score_parts) / len(score_parts))

    return {
        "intensity_status":  intensity_status,
        "rest_status":       rest_status,
        "equipment_status":  equipment_status,
        "recommendations":   recommendations,
        "overall_score":     overall_score,
    }


# =========================
# SESSION LOG
# =========================

def log_iot_session(base_path, readings, analysis):
    """Save IoT session snapshot to iot_session_log.csv."""

    log_path = os.path.join(base_path, "iot_session_log.csv")
    file_exists = os.path.isfile(log_path)

    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "Timestamp", "HeartRate", "Resistance_kg",
                "EquipTemp_C", "RestSeconds", "OverallScore"
            ])

        writer.writerow([
            readings["timestamp"],
            readings["heart_rate"],
            readings["resistance_kg"],
            readings["equipment_temp_c"],
            readings["rest_seconds"],
            analysis["overall_score"],
        ])