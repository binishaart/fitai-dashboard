import cv2
import mediapipe as mp
import math

class PoseDetector:

    def __init__(self):

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

        self.mp_draw = mp.solutions.drawing_utils

        self.results = None

    def findPose(self, img):

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.results = self.pose.process(rgb)

        if self.results.pose_landmarks:

            self.mp_draw.draw_landmarks(
                img,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

        return img

    def findPosition(self, img):

        lmList = []

        if self.results and self.results.pose_landmarks:

            h, w, _ = img.shape

            for id, lm in enumerate(self.results.pose_landmarks.landmark):

                cx = int(lm.x * w)
                cy = int(lm.y * h)

                lmList.append([id, cx, cy])

        return lmList

    def findAngle(self, img, p1, p2, p3, lmList):

        x1, y1 = lmList[p1][1:]
        x2, y2 = lmList[p2][1:]
        x3, y3 = lmList[p3][1:]

        angle = math.degrees(
            math.atan2(y3 - y2, x3 - x2) -
            math.atan2(y1 - y2, x1 - x2)
        )

        angle = abs(angle)
        if angle > 180:
            angle = 360 - angle

        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.line(img, (x2, y2), (x3, y3), (255, 0, 255), 3)

        cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x3, y3), 10, (0, 255, 0), cv2.FILLED)

        cv2.putText(
            img,
            str(int(angle)),
            (x2 - 50, y2 + 50),
            cv2.FONT_HERSHEY_PLAIN,
            2,
            (255, 0, 255),
            2
        )

        return angle   # ✅ FIXED ONLY THIS LINE