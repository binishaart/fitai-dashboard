import cv2
import numpy as np
import time
import json
import csv
import subprocess
import sys
import os
import webbrowser
from datetime import datetime
from pose_detector import PoseDetector

# base folder — so this works no matter what cwd main_dashboard.py launches it from
base_path = os.path.dirname(os.path.abspath(__file__))

cap = cv2.VideoCapture(1)  # use 0 unless you specifically have a second camera

if not cap.isOpened():
    print("ERROR: Could not open camera. Try changing the index (0, 1, 2...) "
          "or check if another app is using the webcam.")
    sys.exit(1)

detector = PoseDetector()

count = 0
direction = 0

mode = "bicep"

print("Gym Trainer Started")

start_time = time.time()

while True:

    success, img = cap.read()

    if not success:
        print("ERROR: Failed to read frame from camera. Exiting.")
        break

    img = detector.findPose(img)
    lmList = detector.findPosition(img)

    # =========================
    # DEFAULTS
    # =========================
    feedback = "No Person Detected"
    angle = 0
    per = 0

    if len(lmList) != 0:

        # =========================
        # BICEP
        # =========================
        if mode == "bicep":

            angle = detector.findAngle(
                img,
                11,
                13,
                15,
                lmList
            )

            target_angle = 60

            if angle > target_angle + 15:
                feedback = "Bad\nContract more"

            elif angle < target_angle - 15:
                feedback = "Bad\nExtend arms"

            else:
                feedback = "Good\nHold position"

        # =========================
        # SQUAT
        # =========================
        else:

            angle = detector.findAngle(
                img,
                23,
                25,
                27,
                lmList
            )

            target_angle = 90

            if angle < target_angle - 15:
                feedback = "Bad\nGo deeper"

            elif angle > 140:
                feedback = "Bad\nLower body"

            else:
                feedback = "Good\nMaintain form"

        # =========================
        # PERCENTAGE
        # =========================
        per = np.interp(
            angle,
            (50, 160),
            (0, 100)
        )

        per = int(per)

        # =========================
        # REP COUNT
        # =========================
        if per >= 95:

            if direction == 0:
                count += 0.5
                direction = 1

        elif per <= 5:

            if direction == 1:
                count += 0.5
                direction = 0

    # =========================
    # UI
    # =========================
    cv2.putText(
        img,
        f"Mode: {mode}",
        (50, 50),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        (255, 255, 0),
        2
    )

    cv2.putText(
        img,
        f"Reps: {int(count)}",
        (50, 100),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        (0, 255, 0),
        2
    )

    cv2.putText(
        img,
        f"{per}%",
        (50, 150),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        (0, 0, 255),
        2
    )

    cv2.putText(
        img,
        feedback,
        (50, 200),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        (0, 0, 255),
        2
    )

    # =========================
    # SHOW WINDOW
    # =========================
    cv2.imshow(
        "AI Gym Trainer",
        img
    )

    # =========================
    # CONTROLS
    # =========================
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):

        workout_time = int(
            time.time() - start_time
        )

        heart_rate = 80 + int(count)

        calories = round(
            count * 0.5,
            1
        )

        if count >= 20:

            recommendation = "Increase Resistance"
            score = 95

        elif count >= 10:

            recommendation = "Maintain Current Intensity"
            score = 80

        else:

            recommendation = "Reduce Weight and Focus on Form"
            score = 60

        data = {
            "exercise": mode,
            "reps": int(count),
            "workout_time": workout_time,
            "heart_rate": heart_rate,
            "calories": calories,
            "recommendation": recommendation,
            "score": score
        }

        # write workout_data.json next to this script, not wherever streamlit happened to cd
        json_path = os.path.join(base_path, "workout_data.json")

        with open(json_path, "w") as f:
            json.dump(data, f)

        # =========================
        # SAVE TO WORKOUT HISTORY (CSV)
        # =========================
        history_path = os.path.join(base_path, "workout_history.csv")

        file_exists = os.path.isfile(history_path)

        with open(history_path, "a", newline="") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["Date", "Exercise", "Reps", "Recommendation"])

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                mode.capitalize(),
                int(count),
                recommendation
            ])

        # workout_summary.py path, resolved relative to this script
        summary_path = os.path.join(base_path, "workout_summary.py")

        # IMPORTANT: different port (8503) so it never clashes with the
        # Diet Chatbot, which runs on 8502 from main_dashboard.py
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                summary_path,
                "--server.port=8503",
                "--server.headless=true"
            ],
            cwd=base_path
        )

        webbrowser.open("http://localhost:8503")

        print("Workout Summary launching at http://localhost:8503")

        break

    elif key == ord('b'):

        mode = "bicep"
        count = 0
        direction = 0

        print(
            "Switched to BICEP"
        )

    elif key == ord('s'):

        mode = "squat"
        count = 0
        direction = 0

        print(
            "Switched to SQUAT"
        )

cap.release()
cv2.destroyAllWindows()