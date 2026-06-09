import streamlit as st
from groq import Groq

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIMAD AI Tutor",
    page_icon="🎓",
    layout="centered",
    menu_items={"About": "SIMAD AI Tutor — Jaamacadda SIMAD · Muqdisho, Soomaaliya"}
)

SIMAD_LOGO = "https://www.simad.edu.so/_next/image?url=%2Fassets%2Fimg%2FSU_25th.png&w=640&q=75"

FACULTIES = [
    "Computing",
    "Management Science",
    "Accounting",
    "Education",
    "Law",
    "Social Science",
    "Engineering",
    "Economics",
    "Medicine and Health Sciences",
]

SUGGESTED_QUESTIONS = {
    "Computing":                  ["Explain what an algorithm is", "What is object-oriented programming?", "How does the internet work?"],
    "Management Science":         ["What is strategic management?", "Explain supply chain management", "What are management theories?"],
    "Accounting":                 ["What is double-entry bookkeeping?", "Explain the accounting equation", "What is a balance sheet?"],
    "Education":                  ["What are teaching methodologies?", "Explain Bloom's taxonomy", "What is curriculum development?"],
    "Law":                        ["What is constitutional law?", "Explain contract law basics", "What is the Somali legal system?"],
    "Social Science":             ["What is sociology?", "Explain qualitative research", "What is social stratification?"],
    "Engineering":                ["What is Ohm's law?", "Explain structural loads", "What is thermodynamics?"],
    "Economics":                  ["What is supply and demand?", "Explain GDP", "What is monetary policy?"],
    "Medicine and Health Sciences": ["What is epidemiology?", "Explain the immune system", "What is public health?"],
}

SYSTEM_PROMPT = {
    "English": (
        "You are SIMAD AI Tutor, a friendly, encouraging, and knowledgeable educational assistant "
        "for SIMAD University students in Mogadishu, Somalia. "
        "You cover all faculties: Computing, Management Science, Accounting, Education, Law, "
        "Social Science, Engineering, Economics, and Medicine and Health Sciences. "
        "The student's selected faculty is: {faculty}. Tailor your responses to their field. "
        "Respond naturally and conversationally like a real tutor — explain clearly, "
        "use examples relevant to Somalia and everyday life, ask follow-up questions, "
        "and always encourage the student. Be warm and supportive. "
        "If asked for a quiz, provide questions with answers. "
        "Always respond in English unless the student writes in Somali."
    ),
    "Somali": (
        "Adiga waxaad tahay SIMAD AI Tutor, macalin saaxiibtinimo leh, dhiiri-gelin badan, "
        "oo waxbarasho u ah ardayda Jaamacadda SIMAD, Muqdisho, Soomaaliya. "
        "Waxaad daboolaysaa dhammaan kulliyadaha: Kombiyuutarka, Maareynta, Xisaabaadka, "
        "Waxbarashada, Sharciga, Bulshada, Injineernimada, Dhaqaalaha, iyo Caafimaadka. "
        "Kulliyada ardaygu xushay waa: {faculty}. Jawaabaha u habbee goobtooda. "
        "Ka jawaab si dabiici ah oo macalin ah — si cad u sharax, tusaalooyin Soomaalida "
        "la xiriira isticmaal, su'aalo raadraac ah weydii, ardaygana had iyo jeer dhiiri geli. "
        "Had iyo jeer Soomaali ka jawaab haddaan ardaygu Ingiriisi ku qorin."
    ),
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(SIMAD_LOGO, use_container_width=True)
    st.markdown("### 🎓 SIMAD AI Tutor")
    st.caption("Jaamacadda SIMAD · Muqdisho, Soomaaliya")
    st.markdown("---")

    language = st.radio("🌐 Language / Luqad", ["English", "Somali (Soomaali)"])
    lang_key = "Somali" if "Soomaali" in language else "English"

    faculty = st.selectbox(
        "🏛️ Your Faculty" if lang_key == "English" else "🏛️ Kulliyadaada",
        FACULTIES
    )

    student_name = st.text_input(
        "👤 Your Name (optional)" if lang_key == "English" else "👤 Magacaaga (ikhtiyaari)"
    )

    st.markdown("---")
    if st.button("🗑️ Clear chat" if lang_key == "English" else "🗑️ Tirtir sheekada", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Phase 2 · All Faculties · SIMAD University")

# ── API Key ───────────────────────────────────────────────────────────────────
api_key = st.secrets.get("GROQ_API_KEY", "") or st.text_input(
    "🔑 Groq API Key", type="password", placeholder="Paste your Groq API key here"
)

if not api_key:
    st.info("Enter your Groq API key to begin." if lang_key == "English" else "Furaha API-ga Groq geli si aad u bilowdo.")
    st.stop()

client = Groq(api_key=api_key)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_faculty" not in st.session_state:
    st.session_state.last_faculty = faculty
if "last_lang" not in st.session_state:
    st.session_state.last_lang = lang_key

# Reset chat if faculty or language changed
if st.session_state.last_faculty != faculty or st.session_state.last_lang != lang_key:
    st.session_state.messages = []
    st.session_state.last_faculty = faculty
    st.session_state.last_lang = lang_key

# ── Header ────────────────────────────────────────────────────────────────────
greeting = f"Hello{', ' + student_name if student_name else ''}! 👋" if lang_key == "English" else f"Salaan{', ' + student_name if student_name else ''}! 👋"
st.markdown(f"## {greeting}")
if lang_key == "English":
    st.caption(f"You're studying **{faculty}**. Ask me anything — I'm here to help!")
else:
    st.caption(f"Waxaad baranaysaa **{faculty}**. Wax kasta i weydii — waan kaa caawin doonaa!")

# ── Welcome screen with suggested questions ───────────────────────────────────
if not st.session_state.messages:
    st.markdown("---")
    label = "💡 Try asking:" if lang_key == "English" else "💡 Isku day:"
    st.markdown(f"**{label}**")
    cols = st.columns(1)
    for q in SUGGESTED_QUESTIONS.get(faculty, []):
        if st.button(q, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
    st.markdown("---")

# ── Display chat messages ─────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
placeholder = "Ask a question..." if lang_key == "English" else "Su'aal weydii..."

if prompt := st.chat_input(placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                system = SYSTEM_PROMPT[lang_key].format(faculty=faculty)
                if student_name:
                    system += f" The student's name is {student_name}. Address them by name occasionally."

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system},
                        *st.session_state.messages,
                    ],
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("© 2026 SIMAD University · Mogadishu, Somalia · AI Tutor Phase 2")
