import streamlit as st
from groq import Groq

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="SIMAD AI Tutor", page_icon="🎓", layout="centered")

SYSTEM_PROMPT = {
    "English": (
        "You are SIMAD AI Tutor, a friendly and knowledgeable educational assistant for "
        "SIMAD University students in Mogadishu, Somalia. You specialize in Computer Science, "
        "Public Health, Statistics, and Research Methods. "
        "Respond naturally and conversationally like a real tutor — explain clearly, use examples "
        "relevant to Somalia and everyday life, ask follow-up questions to check understanding, "
        "and encourage the student. Keep responses focused and helpful. "
        "If asked for a quiz or practice questions, provide them. "
        "If asked to explain a concept, explain it clearly with examples. "
        "Always respond in English unless the student writes in Somali."
    ),
    "Somali": (
        "Adiga waxaad tahay SIMAD AI Tutor, macalin saaxiibtinimo leh oo waxbarasho u ah "
        "ardayda Jaamacadda SIMAD, Muqdisho, Soomaaliya. Waxaad ku takhasustay Cilmiga Kombiyuutarka, "
        "Caafimaadka Guud, Xisaabta, iyo Hababka Cilmi-baarista. "
        "Ka jawaab si dabiici ah oo macalin ah — si cad u sharax, tusaalooyin la xiriira nolosha "
        "Soomaalida isticmaal, su'aalo raadraac ah weydii si aad u hubiso fahamka, ardaygana dhiiri geli. "
        "Had iyo jeer Soomaali ka jawaab haddaan ardaygu Ingiriisi ku qorin."
    ),
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎓 SIMAD AI Tutor")
    st.caption("Jaamacadda SIMAD · Muqdisho")
    st.markdown("---")

    language = st.radio("🌐 Language", ["English", "Somali (Soomaali)"])
    lang_key = "Somali" if "Soomaali" in language else "English"

    st.markdown("**Subjects:**")
    st.markdown("- Computer Science\n- Public Health\n- Statistics\n- Research Methods")

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Phase 1 Beta · SIMAD University")

# ── API Key ───────────────────────────────────────────────────────────────────
api_key = st.secrets.get("GROQ_API_KEY", "") or st.text_input(
    "🔑 Groq API Key", type="password", placeholder="Paste your Groq API key here"
)

if not api_key:
    st.info("Enter your Groq API key to begin.")
    st.stop()

client = Groq(api_key=api_key)

# ── Chat history ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "lang_key" not in st.session_state:
    st.session_state.lang_key = lang_key

# Reset chat if language changed
if st.session_state.lang_key != lang_key:
    st.session_state.messages = []
    st.session_state.lang_key = lang_key

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🎓 SIMAD AI Tutor")
if lang_key == "English":
    st.caption("Ask me anything about your studies — I'm here to help!")
else:
    st.caption("Wax kasta oo ku saabsan waxbarashadaada i weydii — waan kaa caawin doonaa!")

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
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT[lang_key]},
                        *st.session_state.messages,
                    ],
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")
