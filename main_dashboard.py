import streamlit as st
import os
import csv
import time
from streamlit_autorefresh import st_autorefresh
from habit_tracker import analyze_behavior
from gym_buddy import generate_reply
from smart_gym import get_sensor_readings, analyze_sensors, log_iot_session
from pose_analyzer import weekly_report
from gym_recommender import recommend

# ─── Detect if running on Streamlit Cloud ───
IS_CLOUD = os.environ.get("STREAMLIT_SHARING_MODE") is not None or \
           os.environ.get("HOME", "") == "/home/appuser"

st.set_page_config(
    page_title="FitAI · Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

base_path = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Bebas+Neue&family=Space+Grotesk:wght@400;500;600;700&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}
html, body { background:#060B18; color:#E2E8F0; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding:0 !important; max-width:100% !important; }
.stApp { background:#060B18; }

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #060B18 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
    width: 240px !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
[data-testid="stSidebar"] .stRadio > label { display:none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap:2px; display:flex; flex-direction:column; padding-bottom:8px !important; }
[data-testid="stSidebar"] .stRadio label {
    color: #FFFFFF !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    transition: all 0.18s !important;
    cursor: pointer !important;
    margin: 0 !important;
    display: block !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #F1F5F9 !important;
    background: rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb] {
    background: rgba(99,102,241,0.15) !important;
    color: #818CF8 !important;
    border-color: rgba(99,102,241,0.3) !important;
}
[data-testid="stSidebar"] .stRadio input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {
    visibility: hidden !important; width: 0 !important; height: 0 !important;
    margin: 0 !important; padding: 0 !important;
}

/* HERO SECTION */
.hero {
    width: 100%; height: 260px; position: relative; overflow: hidden;
    display: flex; align-items: flex-end; padding: 2rem 2.5rem; margin-bottom: 0;
}
.hero-img {
    position: absolute; inset: 0; background-size: cover;
    background-position: center; filter: brightness(0.35) saturate(1.2);
    transform: scale(1.03); transition: transform 8s ease;
}
.hero-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(to top, rgba(6,11,24,1) 0%, rgba(6,11,24,0.7) 40%, rgba(6,11,24,0.2) 100%);
}
.hero-content { position: relative; z-index: 2; }
.hero-eyebrow {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: #818CF8; margin-bottom: 0.4rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif; font-size: 3.8rem; color: #FFFFFF;
    letter-spacing: 2px; line-height: 0.95; margin-bottom: 0.5rem;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
}
.hero-sub { font-size: 0.82rem; color: #94A3B8; font-weight: 400; max-width: 500px; line-height: 1.5; }

/* CONTENT AREA */
.content { padding: 1.8rem 2.5rem 3rem; }

/* SECTION LABEL */
.sec-label {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 3px; text-transform: uppercase;
    color: #94A3B8; margin-bottom: 0.9rem; margin-top: 1.8rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.sec-label::before { content:''; width:20px; height:1px; background:#6366F1; }
.sec-label::after  { content:''; flex:1; height:1px; background:rgba(255,255,255,0.04); }

/* METRIC CARDS */
.mc {
    background: rgba(15,23,42,0.9); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.1rem 1.25rem; position: relative;
    overflow: hidden; transition: all 0.22s ease; height: 100%;
}
.mc::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg,#6366F1,#06B6D4); opacity: 0; transition: opacity 0.22s;
}
.mc:hover { border-color:rgba(99,102,241,0.3); transform:translateY(-2px); box-shadow:0 12px 36px rgba(0,0,0,0.4); }
.mc:hover::before { opacity:1; }
.mc-label { font-size:0.63rem; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; color:#94A3B8; margin-bottom:0.5rem; }
.mc-val   { font-family:'Space Grotesk',sans-serif; font-size:1.7rem; font-weight:700; color:#F8FAFC; line-height:1.1; }
.mc-sub   { font-size:0.7rem; color:#6366F1; margin-top:0.2rem; font-weight:500; }

/* ALERT BOXES */
.ab {
    display:flex; align-items:flex-start; gap:0.75rem;
    background:rgba(15,23,42,0.8); border:1px solid rgba(255,255,255,0.07);
    border-left:3px solid #6366F1; border-radius:0 10px 10px 0;
    padding:0.8rem 1rem; font-size:0.84rem; color:#94A3B8; margin:0.4rem 0; line-height:1.6;
}
.ab-ok   { border-left-color:#10B981; color:#6EE7B7; background:rgba(16,185,129,0.06); }
.ab-warn { border-left-color:#F59E0B; color:#FCD34D; background:rgba(245,158,11,0.06); }
.ab-bad  { border-left-color:#EF4444; color:#FCA5A5; background:rgba(239,68,68,0.06); }

/* GLASS CARD */
.glass {
    background:rgba(15,23,42,0.85); border:1px solid rgba(255,255,255,0.07);
    border-radius:16px; padding:1.4rem 1.6rem; backdrop-filter:blur(12px);
    position:relative; overflow:hidden;
}
.glass::after {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(99,102,241,0.35),transparent);
}

/* BADGE */
.badge {
    display:inline-block; font-size:0.65rem; font-weight:700; letter-spacing:1.5px;
    text-transform:uppercase; padding:0.25rem 0.7rem; border-radius:20px;
    border:1px solid; margin-bottom:0.5rem;
}
.badge-indigo { color:#818CF8; border-color:#6366F120; background:#6366F110; }
.badge-green  { color:#34D399; border-color:#10B98120; background:#10B98110; }
.badge-amber  { color:#FCD34D; border-color:#F59E0B20; background:#F59E0B10; }
.badge-red    { color:#FCA5A5; border-color:#EF444420; background:#EF444410; }

/* PULSE DOT */
.pdot {
    display:inline-block; width:7px; height:7px; border-radius:50%;
    vertical-align:middle; margin-right:5px; animation: pp 2s ease-in-out infinite;
}
.pdot-g { background:#10B981; }
.pdot-y { background:#F59E0B; }
.pdot-r { background:#EF4444; }
.pdot-b { background:#6366F1; }
@keyframes pp { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.5);opacity:0.5} }

/* BUTTONS */
.stButton>button {
    background:linear-gradient(135deg,#6366F1,#4F46E5) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    padding:0.55rem 1.6rem !important; font-weight:600 !important;
    font-size:0.84rem !important; box-shadow:0 4px 18px rgba(99,102,241,0.35) !important;
    transition:all 0.2s !important; letter-spacing:0.3px !important;
}
.stButton>button:hover {
    box-shadow:0 6px 28px rgba(99,102,241,0.55) !important;
    transform:translateY(-1px) !important;
    background:linear-gradient(135deg,#818CF8,#6366F1) !important;
}

/* STREAMLIT OVERRIDES */
[data-testid="stMetricValue"] { color:#F8FAFC !important; font-family:'Space Grotesk',sans-serif !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] { color:#94A3B8 !important; font-size:0.68rem !important; letter-spacing:1.2px !important; text-transform:uppercase !important; }
[data-testid="stDataFrame"]   { border:1px solid rgba(255,255,255,0.06) !important; border-radius:12px !important; }
[data-testid="stChatMessage"] { background:rgba(15,23,42,0.8) !important; border:1px solid rgba(255,255,255,0.06) !important; border-radius:12px !important; }
[data-testid="stExpander"]    { background:rgba(15,23,42,0.7) !important; border:1px solid rgba(255,255,255,0.06) !important; border-radius:12px !important; }
[data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"] { display:none !important; }
[data-testid="stExpander"] summary svg { display:none !important; }
[data-testid="stExpander"] summary > div:last-child { display:none !important; }
[data-testid="stProgressBar"] > div { background:rgba(99,102,241,0.15) !important; border-radius:99px !important; }
[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#6366F1,#06B6D4) !important; border-radius:99px !important; box-shadow:0 0 10px #6366F166 !important; }
.stSlider [data-baseweb="slider"] div { background:linear-gradient(90deg,#6366F1,#06B6D4) !important; }
div[data-baseweb="notification"] { display:none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
HEROES = {
    "🏠  Overview":        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1600&q=80",
    "💪  Gym Trainer":     "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=1600&q=80",
    "🥗  Diet Coach":      "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1600&q=80",
    "🤖  Gym Buddy":       "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1600&q=80",
    "🏗️  Smart Gym · IoT": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1600&q=80",
    "📊  Performance":     "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=1600&q=80",
    "🏆  Recommender":     "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1600&q=80",
}

with st.sidebar:
    st.markdown("""
    <div style="padding:1.8rem 1.2rem 1rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:1.5rem;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#6366F1,#06B6D4);
                border-radius:8px;display:flex;align-items:center;justify-content:center;
                font-size:1rem;">⚡</div>
            <div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:0.95rem;font-weight:700;
                    color:#F1F5F9;letter-spacing:-0.3px;">FitAI</div>
                <div style="font-size:0.58rem;color:#94A3B8;letter-spacing:2px;text-transform:uppercase;">Intelligence Platform</div>
            </div>
        </div>
        <div style="font-size:0.6rem;color:#94A3B8;letter-spacing:2px;text-transform:uppercase;
            margin-bottom:0.5rem;padding:0 0.2rem;">Navigation</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio("", [
        "🏠  Overview",
        "💪  Gym Trainer",
        "🥗  Diet Coach",
        "🤖  Gym Buddy",
        "🏗️  Smart Gym · IoT",
        "📊  Performance",
        "🏆  Recommender",
    ], label_visibility="collapsed")




# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def hero(eyebrow, title, sub):
    img = HEROES.get(menu, HEROES["🏠  Overview"])
    st.markdown(f"""
    <div class="hero">
        <div class="hero-img" style="background-image:url('{img}');"></div>
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <div class="hero-eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-sub">{sub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def sec(label):
    st.markdown(f"<div class='sec-label'>{label}</div>", unsafe_allow_html=True)

def mc4(items):
    cols = st.columns(len(items))
    for col, (lbl, val, sub) in zip(cols, items):
        sub_html = f"<div class='mc-sub'>{sub}</div>" if sub else ""
        col.markdown(f"""
        <div class="mc">
            <div class="mc-label">{lbl}</div>
            <div class="mc-val">{val}</div>
            {sub_html}
        </div>
        """, unsafe_allow_html=True)

def ab(text, kind=""):
    cls = {"ok":"ab ab-ok","warn":"ab ab-warn","bad":"ab ab-bad"}.get(kind,"ab")
    dot = {"ok":"pdot pdot-g","warn":"pdot pdot-y","bad":"pdot pdot-r"}.get(kind,"pdot pdot-b")
    st.markdown(f"<div class='{cls}'><span class='{dot}'></span><span>{text}</span></div>", unsafe_allow_html=True)

def content_start():
    st.markdown("<div class='content'>", unsafe_allow_html=True)

def content_end():
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# OVERVIEW
# ═══════════════════════════════════════════
if menu == "🏠  Overview":

    st_autorefresh(interval=15000, key="home_refresh")

    hero("AI FITNESS INTELLIGENCE PLATFORM",
         "YOUR DASHBOARD",
         "Behavioral AI · Computer Vision · IoT Integration · NLP · Personalized Coaching")

    content_start()

    c1, c2 = st.columns([1,6])
    with c1:
        if st.button("↺  Refresh"):
            st.rerun()
    with c2:
        st.markdown("<div style='color:#64748B;font-size:0.72rem;margin-top:0.55rem;'>Live data · auto-updates every 15 seconds</div>", unsafe_allow_html=True)

    sec("LAST WORKOUT SESSION")
    history_path = os.path.join(base_path, "workout_history.csv")

    if os.path.isfile(history_path):
        with open(history_path, "r", newline="") as f:
            rows = list(csv.DictReader(f))
        if rows:
            last = rows[-1]
            mc4([
                ("Exercise",       last.get("Exercise","—"),       ""),
                ("Reps Completed", last.get("Reps","—"),           "reps"),
                ("Recommendation", last.get("Recommendation","—"), ""),
                ("Total Sessions", str(len(rows)),                 "logged"),
            ])
            st.markdown(f"<div style='color:#64748B;font-size:0.7rem;margin-top:-0.3rem;'>⏱ {last.get('Date','')}</div>", unsafe_allow_html=True)
        else:
            ab("No workouts yet — start a Gym Trainer session locally.")
    else:
        ab("No workouts yet — start a Gym Trainer session locally.")

    sec("BEHAVIORAL AI · HABIT TRACKER")
    behavior = analyze_behavior(base_path)
    status   = behavior["status"]

    if status in ("no_data","baseline"):
        ab(behavior["nudge"])
    else:
        kind = {"high_risk":"bad","slipping":"warn","on_track":"ok"}.get(status,"")
        ab(behavior["nudge"], kind)

        trend_label = {"increasing":"📈 Rising","decreasing":"📉 Dropping","stable":"➡ Stable"}
        mc4([
            ("Days Since Last",  str(behavior["days_since_last"]),                    "days"),
            ("Your Avg Gap",     f"{behavior['avg_gap']} days",                       ""),
            ("Engagement Trend", trend_label.get(behavior.get("trend","stable"),"—"), ""),
            ("Status",           status.replace("_"," ").title(),                     ""),
        ])
        st.markdown(f"<div class='ab' style='margin-top:0.3rem;'>📅 <b>Schedule:</b> {behavior['schedule_suggestion']}</div>", unsafe_allow_html=True)

    content_end()


# ═══════════════════════════════════════════
# GYM TRAINER
# ═══════════════════════════════════════════
elif menu == "💪  Gym Trainer":

    hero("MODULE 1 · COMPUTER VISION",
         "AI GYM TRAINER",
         "MediaPipe pose detection · Real-time rep counting · Form correction feedback")

    content_start()
    sec("HOW IT WORKS")
    st.markdown("""
    <div class="glass">
        <div style="display:flex;flex-wrap:wrap;gap:2rem;">
            <div><div class="mc-label">Bicep Mode</div><div style="color:#06B6D4;font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;">Press  B</div></div>
            <div><div class="mc-label">Squat Mode</div><div style="color:#06B6D4;font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;">Press  S</div></div>
            <div><div class="mc-label">End &amp; Save</div><div style="color:#EF4444;font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;">Press  Q</div></div>
            <div><div class="mc-label">Data Auto-Saved To</div><div style="color:#818CF8;font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;">workout_history.csv</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if IS_CLOUD:
        ab("🎥 Camera-based Gym Trainer requires local setup — <b>run app.py on your machine</b> to use this module. All other 6 modules work live here!", "warn")
        st.markdown("""
        <div class="glass" style="margin-top:1rem;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.95rem;font-weight:700;color:#E2E8F0;margin-bottom:0.5rem;">Run Locally</div>
            <div style="color:#94A3B8;font-size:0.84rem;line-height:1.8;">
                1. Clone the repo from GitHub<br>
                2. Run: <span style="color:#818CF8;font-family:monospace;">pip install mediapipe opencv-python</span><br>
                3. Run: <span style="color:#818CF8;font-family:monospace;">python app.py</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        import subprocess, sys
        ab("⚠️ Gym Trainer requires local setup — camera not available on cloud.", "warn")

    content_end()


# ═══════════════════════════════════════════
# DIET COACH
# ═══════════════════════════════════════════
elif menu == "🥗  Diet Coach":

    hero(
        "MODULE 2 · NLP",
        "AI DIET COACH",
        "BMI-based meal planning · Calorie tracking · Grocery lists · Nutritional guidance"
    )

    content_start()

    st.subheader("🥗 AI Dietician & Calorie Coach")

    if "diet_step" not in st.session_state:
        st.session_state.diet_step = 1

    if "diet_weight" not in st.session_state:
        st.session_state.diet_weight = None

    if "diet_height" not in st.session_state:
        st.session_state.diet_height = None

    if "diet_goal" not in st.session_state:
        st.session_state.diet_goal = None

    # STEP 1
    if st.session_state.diet_step == 1:

        weight = st.number_input(
            "Enter Weight (kg)",
            min_value=1.0,
            value=60.0
        )

        if st.button("Next ➡️"):
            st.session_state.diet_weight = weight
            st.session_state.diet_step = 2
            st.rerun()

    # STEP 2
    elif st.session_state.diet_step == 2:

        height = st.number_input(
            "Enter Height (cm)",
            min_value=50.0,
            value=170.0
        )

        if st.button("Next ➡️"):
            st.session_state.diet_height = height
            st.session_state.diet_step = 3
            st.rerun()

    # STEP 3
    elif st.session_state.diet_step == 3:

        goal = st.selectbox(
            "Select Goal",
            [
                "Weight Loss",
                "Weight Gain",
                "Maintain"
            ]
        )

        if st.button("Generate Diet Plan 🚀"):
            st.session_state.diet_goal = goal
            st.session_state.diet_step = 4
            st.rerun()

    # STEP 4
    elif st.session_state.diet_step == 4:

        weight = float(st.session_state.diet_weight)
        height = float(st.session_state.diet_height) / 100

        bmi = weight / (height * height)

        # BMI Category
        if bmi < 18.5:
            category = "Underweight"
            diet = "Rice Bowl Diet"
            ingredients = [
                "Rice",
                "Milk",
                "Banana",
                "Peanut Butter",
                "Almonds"
            ]

        elif bmi > 25:
            category = "Overweight"
            diet = "Oats Protein Diet"
            ingredients = [
                "Oats",
                "Eggs",
                "Paneer",
                "Vegetables",
                "Fruits"
            ]

        else:
            category = "Healthy"
            diet = "Balanced Plate Diet"
            ingredients = [
                "Rice",
                "Milk",
                "Eggs",
                "Fruits",
                "Vegetables",
                "Nuts"
            ]

        st.success("✅ Diet Plan Generated")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("⚖️ Weight", f"{weight:.1f} kg")

        with col2:
            st.metric("📏 Height", f"{height*100:.0f} cm")

        st.metric(
            label="📊 BMI Score",
            value=f"{bmi:.2f}"
        )

        st.info(f"BMI Category: **{category}**")

        st.write(f"## 🍽️ Recommended Diet: {diet}")

        st.write("### 🛒 Ingredients")

        for item in ingredients:
            st.write(f"• {item}")

        st.write("---")

        if st.button("🔄 Start Again"):
            st.session_state.diet_step = 1
            st.session_state.diet_weight = None
            st.session_state.diet_height = None
            st.session_state.diet_goal = None
            st.rerun()

    content_end()


# ═══════════════════════════════════════════
# GYM BUDDY
# ═══════════════════════════════════════════
elif menu == "🤖  Gym Buddy":

    hero("MODULE 5 · CONVERSATIONAL AI",
         "VIRTUAL GYM BUDDY",
         "Sentiment analysis · Emotional state tracking · Motivational AI companion")

    st.markdown("<div style='padding:1rem 2.5rem 0;'>", unsafe_allow_html=True)

    if "gym_buddy_messages" not in st.session_state:
        st.session_state.gym_buddy_messages = [
            {"role":"assistant","content":"Hey! ⚡ Main tera AI Gym Buddy hoon. Aaj kaisa feel ho raha hai?"}
        ]

    for msg in st.session_state.gym_buddy_messages:
        avatar = "⚡" if msg["role"] == "assistant" else "🧑"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    user_input = st.chat_input("Message your Gym Buddy...")
    if user_input:
        st.session_state.gym_buddy_messages.append({"role":"user","content":user_input})
        reply, _ = generate_reply(user_input, base_path)
        st.session_state.gym_buddy_messages.append({"role":"assistant","content":reply})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# SMART GYM
# ═══════════════════════════════════════════
elif menu == "🏗️  Smart Gym · IoT":

    hero("MODULE 3 · AI + IoT INTEGRATION",
         "SMART GYM ASSISTANT",
         "Live equipment monitoring · Adaptive resistance · Heart rate analysis · Session scoring")

    content_start()
    sec("IoT SENSOR INPUT")

    reps_input = st.slider("Current rep count from your session", 0, 50, 10)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📡  Connect & Analyze"):
        with st.spinner("Handshaking with IoT layer..."):
            time.sleep(1)
            readings = get_sensor_readings(reps=reps_input)
            analysis = analyze_sensors(readings)
            log_iot_session(base_path, readings, analysis)

        ab("✅ All 4 sensors responding · session logged to iot_session_log.csv", "ok")

        sec("LIVE SENSOR READINGS")
        mc4([
            ("Heart Rate",   f"{readings['heart_rate']} bpm",     readings["timestamp"][:10]),
            ("Resistance",   f"{readings['resistance_kg']} kg",   "smart equipment"),
            ("Equip Temp",   f"{readings['equipment_temp_c']}C",  "thermal sensor"),
            ("Rest Period",  f"{readings['rest_seconds']} sec",   "between sets"),
        ])

        sec("SESSION QUALITY SCORE")
        score = analysis["overall_score"]
        kind  = "ok" if score>=80 else "warn" if score>=60 else "bad"
        label = "Excellent session!" if score>=80 else "Good — push harder" if score>=60 else "Needs improvement"
        ab(f"<b>{score} / 100</b> — {label}", kind)
        st.progress(score / 100)

        sec("AI RECOMMENDATIONS")
        for rec in analysis["recommendations"]:
            ab(f"▸ {rec}")

    content_end()


# ═══════════════════════════════════════════
# PERFORMANCE
# ═══════════════════════════════════════════
elif menu == "📊  Performance":

    hero("MODULE 6 · MOTION EFFICIENCY",
         "POSE-TO-PERFORMANCE",
         "Performance scoring · Weekly progress reports · Trend analysis · Session history")

    content_start()

    import pandas as pd
    report = weekly_report(base_path)

    if not report:
        ab("No workout history found — complete at least one Gym Trainer session first.")
    else:
        trend_cfg = {
            "improving": ("ok",   "Performance improving week-over-week — excellent consistency!"),
            "declining": ("warn", "Performance declining — increase session frequency."),
            "stable":    ("",     "Performance stable — aim to push intensity this week."),
        }
        kind, msg = trend_cfg[report["trend"]]
        ab(msg, kind)

        sec("WEEKLY SCORE")
        chart_df = pd.DataFrame({"Week":report["weeks"],"Avg Score":report["avg_scores"]}).set_index("Week")
        st.bar_chart(chart_df["Avg Score"], color="#6366F1")

        mc4([
            ("Best Week",      report["best_week"],              ""),
            ("Weeks Tracked",  str(len(report["weeks"])),        ""),
            ("Total Sessions", str(len(report["all_sessions"])), ""),
            ("Latest Score",   str(report["avg_scores"][-1]),    "/ 100"),
        ])

        sec("SESSION LOG")
        df = pd.DataFrame(report["all_sessions"])
        df.columns = ["Date","Week","Exercise","Reps","Performance Score"]
        st.dataframe(df[["Date","Exercise","Reps","Performance Score"]], use_container_width=True, hide_index=True)

    content_end()


# ═══════════════════════════════════════════
# RECOMMENDER
# ═══════════════════════════════════════════
elif menu == "🏆  Recommender":

    hero("MODULE 7 · RECOMMENDATION ENGINE",
         "GYM RECOMMENDER",
         "AI fitness profiling · Personalized workout programs · Nearby gym discovery")

    content_start()

    result = recommend(base_path)
    level  = result["level"]

    badge_cfg = {
        "beginner":     ("badge badge-green", "Beginner"),
        "intermediate": ("badge badge-amber", "Intermediate"),
        "advanced":     ("badge badge-red",   "Advanced"),
    }
    badge_cls, badge_lbl = badge_cfg[level]

    sec("FITNESS PROFILE")
    st.markdown(f"""
    <div class="glass">
        <span class="{badge_cls}">{badge_lbl}</span>
        <div style="color:#94A3B8;font-size:0.85rem;margin-top:0.4rem;line-height:1.6;">{result['insight']}</div>
    </div>
    """, unsafe_allow_html=True)

    mc4([
        ("Fitness Level",      level.capitalize(),                  "AI detected"),
        ("Fav Exercise",       result["favourite_ex"],              "from history"),
        ("Program",            result["program"]["label"][:20]+"…", "recommended"),
        ("Gyms Found",         str(len(result["gyms"])),            "near you"),
    ])

    sec("RECOMMENDED WORKOUT PROGRAM")
    prog = result["program"]
    schedule_html = "".join(
        f"<div class='ab' style='margin-bottom:0.3rem;padding:0.55rem 1rem;'>▸ {d}</div>"
        for d in prog["schedule"]
    )
    st.markdown(f"""
    <div class="glass">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;
            color:#E2E8F0;margin-bottom:0.25rem;">{prog['label']}</div>
        <div style="color:#94A3B8;font-size:0.8rem;margin-bottom:1rem;">{prog['description']}</div>
        {schedule_html}
        <div class="ab ab-ok" style="margin-top:0.7rem;"> <b>Challenge:</b> {prog['challenge']}</div>
    </div>
    """, unsafe_allow_html=True)

    sec("TOP GYM SUGGESTIONS")
    for gym in result["gyms"]:
        st.markdown(f"""
        <div class="glass" style="margin-bottom:0.8rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:0.95rem;font-weight:700;color:#E2E8F0;">{gym['name']}</div>
                <div style="font-size:0.75rem;color:#FCD34D;font-weight:600;">&#11088; {gym['rating']} / 5</div>
            </div>
            <div style="font-size:0.78rem;color:#94A3B8;margin-bottom:0.8rem;">📍 {gym['location']}</div>
            <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.6rem;color:#94A3B8;letter-spacing:1.5px;text-transform:uppercase;">Monthly</div>
                    <div style="font-size:0.9rem;color:#818CF8;font-weight:600;">{gym['fee']}</div>
                </div>
                <div>
                    <div style="font-size:0.6rem;color:#94A3B8;letter-spacing:1.5px;text-transform:uppercase;">Specialty</div>
                    <div style="font-size:0.9rem;color:#CBD5E1;">{', '.join(gym['specialty'])}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    content_end()
