import streamlit as st
from groq import Groq

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="SIMAD AI Tutor", page_icon="🎓", layout="centered")

SUBJECTS = {
    "Computer Science": ["Introduction to Programming", "Data Structures", "Algorithms",
                         "Networking Basics", "Databases", "Operating Systems"],
    "Public Health":    ["Epidemiology", "Health Promotion", "Disease Prevention",
                         "Environmental Health", "Health Policy", "Biostatistics"],
    "Statistics":       ["Descriptive Statistics", "Probability", "Hypothesis Testing",
                         "Regression Analysis", "ANOVA", "Data Visualization"],
    "Research Methods": ["Research Design", "Literature Review", "Data Collection",
                         "Qualitative Methods", "Quantitative Methods", "Academic Writing"],
}

SYSTEM_PROMPT = {
    "English": (
        "You are SIMAD AI Tutor, an educational assistant for SIMAD University students in Mogadishu, Somalia. "
        "Respond clearly in English. Always structure your response with:\n\n"
        "## Explanation\n(Clear explanation of the topic)\n\n"
        "## Real-World Example\n(A practical example relevant to Somalia or everyday life)\n\n"
        "## Quiz Questions\n(Three questions with answers to test understanding)"
    ),
    "Somali": (
        "Adiga waxaad tahay SIMAD AI Tutor, caawimaha waxbarashada ee ardayda Jaamacadda SIMAD, Muqdisho. "
        "Ka jawaab si cad oo Soomaali ah. Jawaabta had iyo jeer u qaybi sidan:\n\n"
        "## Sharaxaad\n(Sharax cad oo mowduuca ah)\n\n"
        "## Tusaale Runta ah\n(Tusaale ku habboon nolosha Soomaalida)\n\n"
        "## Su'aalaha Imtixaanka\n(Saddex su'aalood oo leh jawaabaha)"
    ),
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎓 SIMAD AI Tutor")
    st.caption("Powered by Groq AI")
    st.markdown("---")

    api_key = st.secrets.get("GROQ_API_KEY", "") or st.text_input(
        "🔑 Groq API Key", type="password", placeholder="Paste your Groq API key here"
    )
    language = st.radio("🌐 Language", ["English", "Somali (Soomaali)"])
    lang_key = "Somali" if "Soomaali" in language else "English"

    st.markdown("---")
    st.caption("Phase 1 — Computer Science, Public Health, Statistics, Research Methods")

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("## 🎓 SIMAD AI Tutor")
st.markdown("Select a subject and topic to get a structured lesson and quiz.")

if not api_key:
    st.info("Enter your Groq API key in the sidebar to begin.")
    st.stop()

client = Groq(api_key=api_key)

col1, col2 = st.columns(2)
with col1:
    subject = st.selectbox("📚 Subject", list(SUBJECTS.keys()))
with col2:
    topic = st.selectbox("📖 Topic", SUBJECTS[subject])

custom_q = st.text_input("💬 Ask a specific question (optional)",
                          placeholder="e.g. What is the difference between TCP and UDP?")

if st.button("Generate Lesson ✨", type="primary", use_container_width=True):
    if custom_q.strip():
        user_prompt = f"Subject: {subject}\nTopic: {topic}\nStudent question: {custom_q}"
    else:
        user_prompt = f"Teach me about '{topic}' from the subject '{subject}'."

    with st.spinner("Generating your lesson..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT[lang_key]},
                    {"role": "user", "content": user_prompt},
                ],
            )
            st.markdown("---")
            st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("SIMAD University · Mogadishu, Somalia · Phase 1 Beta")
