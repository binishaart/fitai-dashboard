import os
import csv
import random
import re
from datetime import datetime

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from habit_tracker import analyze_behavior

_analyzer = SentimentIntensityAnalyzer()


def _contains_keyword(text, keywords):
    """Whole-word/phrase match, not plain substring — avoids false positives
    like 'hi' matching inside 'which' or 'this'."""

    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text):
            return True

    return False


# =========================
# RESPONSE TEMPLATES
# =========================
GREETINGS = [
    "Hey! 👋 Kaisi chal rahi hai fitness journey?",
    "Hi there! Ready for today's session? 💪",
    "Namaste! Bata, aaj kya plan hai?",
]

THANKS_REPLIES = [
    "You're welcome! Always here for you 😊",
    "Anytime! Keep showing up, that's all that matters. 💪",
]

AFFIRMATIVE_REPLIES = [
    "Nice! Konsa workout try karna hai — bicep curls ya squats? 💪 Gym Trainer tab se shuru kar sakti ho.",
    "Great! Chal phir Gym Trainer tab khol aur start kar de.",
]

LONG_BREAK_REPLIES = [
    "Itna lamba break thoda risky hai — strength aur momentum dono lose ho sakte hain. Agar rest chahiye, 3-4 din ka short break le, phir halka-phulka shuru kar de.",
    "Pura mahina chhodne se dobara start karna aur mushkil ho jaata hai. Intensity kam kar de agar zaroorat hai, but bilkul band mat kar.",
    "Samajh sakta hoon thakaan ho rahi hai, par 1 month ka gap habit tod sakta hai. Koi specific wajah hai? Shayad schedule hi adjust kar lein.",
]

DISCOURAGED_REPLIES = [
    "Samajh sakta hoon, thakaan feel karna normal hai. Ek chhota 10-min session bhi count karta hai — bas shuru kar de! 🌱",
    "Skip karne ka mann hai? Koi baat nahi, bas kal phir try karna. Consistency matters, perfection nahi. 💛",
    "Tough din lag raha hai? Apne aap pe thoda easy jaa, lekin movement bilkul band mat kar. Even a short walk helps.",
]

MOTIVATION_QUOTES = [
    "Tera body wahi keh rahi hai jo tu usse roz batati hai — keep showing up! 🔥",
    "Progress slow ho sakta hai, lekin har rep count hota hai. Tu already better hai kal se!",
    "Discipline beats motivation on the days motivation doesn't show up. Just one set, abhi! 💪",
    "Tu yahan tak pahunchi, ye already ek win hai. Aage badh!",
]

ACHIEVEMENT_REPLIES = [
    "Yesss! 🎉 Bahut badhiya, proud of you!",
    "That's the spirit! Keep this momentum going! 🔥",
    "Solid work! Apni progress ko celebrate karna mat bhoolna. 🙌",
]

WORKOUT_TIP_REPLIES = [
    "Beginners ke liye usually 8-12 reps per set acha range hota hai. Real-time form feedback ke liye 💪 Gym Trainer tab try kar!",
    "Yeh depend karta hai goal pe — strength ke liye kam reps zyada effort, endurance ke liye zyada reps kam effort. 💪 Gym Trainer tab mein live feedback bhi milega.",
]

BICEP_REPLIES = [
    "Bicep curls ke liye Gym Trainer kholo aur 'b' dabakar bicep mode select karo — real-time form feedback aur rep counting dono milega! 💪",
    "Bicep mode mein elbow stable rakhna aur full range of motion pe focus karna — Gym Trainer tab mein 'b' dabao to start.",
]

SQUAT_REPLIES = [
    "Squats ke liye Gym Trainer kholo aur 's' dabakar squat mode select karo — depth aur form dono track hoga! 🦵",
    "Squats mein knees toes ke direction mein rakhna, aur depth pe target rakhna — Gym Trainer mein 's' dabao to start.",
]

DIET_REDIRECT = [
    "Diet ke liye 🥗 Diet Chatbot tab try kar — wahan BMI-based plan milega!",
]

FAREWELL_REPLIES = [
    "Bye! Apna khayal rakhna, aur kal milte hain workout pe! 👋",
    "Catch you later — don't forget tomorrow's session!",
]

GENERIC_REPLIES = [
    "Bata aur kya chal raha hai — workout, diet, ya bas motivation chahiye? 😊",
    "Main yahin hoon agar kabhi push chahiye ho ya bas baat karni ho.",
]


# =========================
# SENTIMENT (used only for mood_log.csv tracking, not for reply selection)
# =========================
def detect_sentiment(text):
    """Returns (label, compound_score) using VADER sentiment analysis."""

    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.3:
        label = "positive"
    elif compound <= -0.3:
        label = "negative"
    else:
        label = "neutral"

    return label, compound


# =========================
# INTENT (keyword based — this is what drives the reply, not sentiment)
# =========================
def detect_intent(text):
    t = text.lower()

    if _contains_keyword(t, ["thank you", "thanks", "thank u", "shukriya"]):
        return "thanks"

    if _contains_keyword(t, ["yes", "yeah", "yup", "haan", "sure", "ok", "okay"]):
        return "affirmative"

    if _contains_keyword(t, [
        "leave", "chutti", "break for", "1 month", "ek mahina",
        "mahine ki chutti", "quit workout", "stop workout", "stop training"
    ]):
        return "long_break"

    if _contains_keyword(t, [
        "tired", "exhausted", "lazy", "skip", "cant", "can't",
        "thakaan", "thak gaya", "thak gayi", "mann nahi",
        "mood down", "mood off", "udaas", "dukhi", "sad", "down",
        "low feel", "low hu", "low hoon"
    ]):
        return "discouraged"

    if _contains_keyword(t, [
        "motivate", "motivation", "motivated", "inspire", "inspired",
        "push me", "josh"
    ]):
        return "motivation_request"

    if _contains_keyword(t, ["did it", "completed", "done", "proud", "finished", "kar liya", "ho gaya"]):
        return "achievement"

    if _contains_keyword(t, ["bicep", "biceps", "curl", "curls"]):
        return "bicep_exercise"

    if _contains_keyword(t, ["squat", "squats"]):
        return "squat_exercise"

    if _contains_keyword(t, ["hi", "hello", "hey", "namaste", "yo"]):
        return "greeting"

    if _contains_keyword(t, ["reps", "sets", "how many", "count", "kitne"]):
        return "workout_question"

    if _contains_keyword(t, ["diet", "food", "eat", "calorie", "khana"]):
        return "diet_question"

    if _contains_keyword(t, ["bye", "goodbye", "see you", "alvida"]):
        return "farewell"

    return "general"


# =========================
# MOOD LOGGING
# =========================
def log_mood(base_path, sentiment_label, score):
    """Append a row to mood_log.csv so emotional state is tracked over time."""

    log_path = os.path.join(base_path, "mood_log.csv")
    file_exists = os.path.isfile(log_path)

    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Date", "Sentiment", "Score"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            sentiment_label,
            round(score, 3)
        ])


# =========================
# MAIN REPLY GENERATOR
# =========================
def generate_reply(user_text, base_path):
    """Returns (reply_text, sentiment_label) for a given user message.

    Reply category is decided purely by keyword/intent matching — predictable
    and easy to debug. Sentiment is still computed and logged (for the mood
    history), but it no longer picks the reply category on its own, since
    that caused short/ambiguous messages (e.g. "thank you", "yes") to be
    misclassified.
    """

    sentiment_label, score = detect_sentiment(user_text)
    intent = detect_intent(user_text)

    log_mood(base_path, sentiment_label, score)

    behavior = analyze_behavior(base_path)

    if intent == "greeting":
        reply = random.choice(GREETINGS)

    elif intent == "thanks":
        reply = random.choice(THANKS_REPLIES)

    elif intent == "affirmative":
        reply = random.choice(AFFIRMATIVE_REPLIES)

    elif intent == "long_break":
        reply = random.choice(LONG_BREAK_REPLIES)

    elif intent == "discouraged":
        reply = random.choice(DISCOURAGED_REPLIES)

        if behavior.get("status") == "high_risk":
            reply += (
                f" Btw, {behavior['days_since_last']} din ho gaye last workout ko — "
                f"ek chhota session try kar le aaj? 👀"
            )

    elif intent == "motivation_request":
        reply = random.choice(MOTIVATION_QUOTES)

    elif intent == "achievement":
        reply = random.choice(ACHIEVEMENT_REPLIES)

    elif intent == "bicep_exercise":
        reply = random.choice(BICEP_REPLIES)

    elif intent == "squat_exercise":
        reply = random.choice(SQUAT_REPLIES)

    elif intent == "workout_question":
        reply = random.choice(WORKOUT_TIP_REPLIES)

    elif intent == "diet_question":
        reply = random.choice(DIET_REDIRECT)

    elif intent == "farewell":
        reply = random.choice(FAREWELL_REPLIES)

    else:
        reply = random.choice(GENERIC_REPLIES)

    return reply, sentiment_label