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
    "Computing", "Management Science", "Accounting", "Education",
    "Law", "Social Science", "Engineering", "Economics", "Medicine and Health Sciences",
]

SUGGESTED_QUESTIONS = {
    "Computing":                    ["Explain what an algorithm is", "What is object-oriented programming?", "How does the internet work?"],
    "Management Science":           ["What is strategic management?", "Explain supply chain management", "What are management theories?"],
    "Accounting":                   ["What is double-entry bookkeeping?", "Explain the accounting equation", "What is a balance sheet?"],
    "Education":                    ["What are teaching methodologies?", "Explain Bloom's taxonomy", "What is curriculum development?"],
    "Law":                          ["What is constitutional law?", "Explain contract law basics", "What is the Somali legal system?"],
    "Social Science":               ["What is sociology?", "Explain qualitative research", "What is social stratification?"],
    "Engineering":                  ["What is Ohm's law?", "Explain structural loads", "What is thermodynamics?"],
    "Economics":                    ["What is supply and demand?", "Explain GDP", "What is monetary policy?"],
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
        "use examples relevant to Somalia and everyday life, and always encourage the student."
    ),
    "Somali": (
        "Adiga waxaad tahay SIMAD AI Tutor, macalin saaxiibtinimo leh oo waxbarasho u ah "
        "ardayda Jaamacadda SIMAD, Muqdisho, Soomaaliya. "
        "Kulliyada ardaygu xushay waa: {faculty}. Jawaabaha u habbee goobtooda. "
        "Ka jawaab si dabiici ah oo macalin ah — ardaygana had iyo jeer dhiiri geli."
    ),
}

# ── API Key ───────────────────────────────────────────────────────────────────
api_key = st.secrets.get("GROQ_API_KEY", "") or st.text_input(
    "🔑 Groq API Key", type="password", placeholder="Paste your Groq API key here"
)

def ask_ai(messages, system):
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}, *messages],
    )
    return response.choices[0].message.content

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(SIMAD_LOGO, use_container_width=True)
    st.markdown("### 🎓 SIMAD AI Tutor")
    st.caption("Jaamacadda SIMAD · Muqdisho, Soomaaliya")
    st.markdown("---")

    language = st.radio("🌐 Language / Luqad", ["English", "Somali (Soomaali)"])
    lang_key = "Somali" if "Soomaali" in language else "English"

    faculty = st.selectbox(
        "🏛️ Your Faculty" if lang_key == "English" else "🏛️ Kulliyadaada", FACULTIES
    )
    student_name = st.text_input(
        "👤 Your Name (optional)" if lang_key == "English" else "👤 Magacaaga (ikhtiyaari)"
    )

    st.markdown("---")
    mode = st.radio(
        "📚 Mode" if lang_key == "English" else "📚 Qaab",
        ["💬 Chat", "📝 Quiz", "📄 Study Notes"]
    )
    st.markdown("---")
    if st.button("🗑️ Clear" if lang_key == "English" else "🗑️ Tirtir", use_container_width=True):
        for key in ["messages", "quiz_questions", "quiz_index", "quiz_score", "quiz_done", "notes"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.markdown("---")
    st.caption("Phase 2 · SIMAD University")

if not api_key:
    st.image(SIMAD_LOGO, width=200)
    st.info("Enter your Groq API key in the sidebar to begin.")
    st.stop()

greeting = f"Hello{', ' + student_name if student_name else ''}! 👋" if lang_key == "English" else f"Salaan{', ' + student_name if student_name else ''}! 👋"
system_base = SYSTEM_PROMPT[lang_key].format(faculty=faculty)
if student_name:
    system_base += f" The student's name is {student_name}. Address them by name occasionally."

# ════════════════════════════════════════════════════════════════
# MODE 1: CHAT
# ════════════════════════════════════════════════════════════════
if mode == "💬 Chat":
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.markdown(f"## {greeting}")
    st.caption(f"💬 **{faculty}** · {'Ask me anything!' if lang_key == 'English' else 'Wax kasta i weydii!'}")

    if not st.session_state.messages:
        st.markdown("---")
        st.markdown(f"**{'💡 Try asking:' if lang_key == 'English' else '💡 Isku day:'}**")
        for q in SUGGESTED_QUESTIONS.get(faculty, []):
            if st.button(q, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()
        st.markdown("---")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    placeholder = "Ask a question..." if lang_key == "English" else "Su'aal weydii..."
    if prompt := st.chat_input(placeholder):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(""):
                try:
                    reply = ask_ai(st.session_state.messages, system_base)
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")

# ════════════════════════════════════════════════════════════════
# MODE 2: QUIZ
# ════════════════════════════════════════════════════════════════
elif mode == "📝 Quiz":
    st.markdown(f"## {greeting}")
    st.markdown(f"### 📝 {'Quiz Mode' if lang_key == 'English' else 'Qaabka Imtixaanka'}")
    st.caption(f"{'Test your knowledge on any topic.' if lang_key == 'English' else 'Imtixaan nafta ku samee mowduuc kasta.'}")

    topic = st.text_input(
        "Enter a topic to be quizzed on:" if lang_key == "English" else "Mowduuca aad imtixaan ka qaadanayso geli:",
        placeholder="e.g. Data Structures, Epidemiology, Contract Law..."
    )

    if st.button("🎯 Start Quiz" if lang_key == "English" else "🎯 Bilow Imtixaanka", type="primary", use_container_width=True):
        if topic.strip():
            with st.spinner("Generating quiz..." if lang_key == "English" else "Imtixaanka la diyaarinayaa..."):
                try:
                    prompt = (
                        f"Generate exactly 5 multiple choice questions about '{topic}' for a {faculty} student. "
                        f"Format each question EXACTLY like this:\n"
                        f"Q: [question]\nA) [option]\nB) [option]\nC) [option]\nD) [option]\nANSWER: [letter]\n\n"
                        f"Separate each question with ---"
                    )
                    raw = ask_ai([{"role": "user", "content": prompt}], system_base)
                    questions = [q.strip() for q in raw.split("---") if q.strip()]
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_index = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_done = False
                    st.session_state.quiz_topic = topic
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if "quiz_questions" in st.session_state and not st.session_state.get("quiz_done"):
        questions = st.session_state.quiz_questions
        idx = st.session_state.quiz_index

        if idx < len(questions):
            q_block = questions[idx]
            lines = [l.strip() for l in q_block.split("\n") if l.strip()]
            question_text = next((l[3:] for l in lines if l.startswith("Q:")), "")
            options = [l for l in lines if l.startswith(("A)", "B)", "C)", "D)"))]
            answer_line = next((l for l in lines if l.startswith("ANSWER:")), "")
            correct = answer_line.replace("ANSWER:", "").strip()

            st.markdown("---")
            progress = (idx) / len(questions)
            st.progress(progress, text=f"Question {idx+1} of {len(questions)}")
            st.markdown(f"**{question_text}**")

            choice = st.radio("Choose your answer:", options, key=f"q_{idx}", label_visibility="collapsed")

            if st.button("✅ Submit Answer" if lang_key == "English" else "✅ Jawaabta Gudbi", use_container_width=True):
                selected_letter = choice[0] if choice else ""
                if selected_letter == correct:
                    st.success("✅ Correct!" if lang_key == "English" else "✅ Saxan!")
                    st.session_state.quiz_score += 1
                else:
                    st.error(f"❌ Wrong. Correct answer: **{correct}**" if lang_key == "English" else f"❌ Khalad. Jawaabta sax ah: **{correct}**")

                st.session_state.quiz_index += 1
                if st.session_state.quiz_index >= len(questions):
                    st.session_state.quiz_done = True
                st.rerun()

    if st.session_state.get("quiz_done"):
        score = st.session_state.quiz_score
        total = len(st.session_state.quiz_questions)
        pct = int((score / total) * 100)
        st.markdown("---")
        st.markdown(f"## 🏆 Quiz Complete!")
        st.markdown(f"### Score: **{score}/{total}** ({pct}%)")
        if pct >= 80:
            st.success("Excellent work! 🌟" if lang_key == "English" else "Shaqo fiican! 🌟")
        elif pct >= 60:
            st.info("Good effort! Keep studying. 📚" if lang_key == "English" else "Dadaal wanaagsan! Sii wad barasho. 📚")
        else:
            st.warning("Keep practicing — you'll get there! 💪" if lang_key == "English" else "Sii wad celcelinta — waad gaari doontaa! 💪")

        if st.button("🔄 Try Again" if lang_key == "English" else "🔄 Mar kale isku day", use_container_width=True):
            for key in ["quiz_questions", "quiz_index", "quiz_score", "quiz_done"]:
                st.session_state.pop(key, None)
            st.rerun()

# ════════════════════════════════════════════════════════════════
# MODE 3: STUDY NOTES
# ════════════════════════════════════════════════════════════════
elif mode == "📄 Study Notes":
    st.markdown(f"## {greeting}")
    st.markdown(f"### 📄 {'Study Notes Generator' if lang_key == 'English' else 'Diyaarinta Xusuus-qorka'}")
    st.caption("Generate a clean, structured summary on any topic." if lang_key == "English" else "Soo saar kooban oo qurxoon mowduuc kasta.")

    notes_topic = st.text_input(
        "Enter a topic:" if lang_key == "English" else "Mowduuca geli:",
        placeholder="e.g. Supply and Demand, Human Anatomy, Criminal Law..."
    )

    if st.button("📄 Generate Notes" if lang_key == "English" else "📄 Soo saar Xusuus-qorka", type="primary", use_container_width=True):
        if notes_topic.strip():
            with st.spinner("Generating study notes..." if lang_key == "English" else "Xusuus-qorka la diyaarinayaa..."):
                try:
                    lang_instruction = "in English" if lang_key == "English" else "in Somali (Soomaali)"
                    prompt = (
                        f"Create comprehensive study notes {lang_instruction} about '{notes_topic}' for a {faculty} student at SIMAD University, Somalia. "
                        f"Structure the notes with: "
                        f"1. Overview (2-3 sentences), "
                        f"2. Key Concepts (bullet points), "
                        f"3. Important Definitions, "
                        f"4. Real-world examples from Somalia or Africa, "
                        f"5. Common exam questions on this topic, "
                        f"6. Quick Summary. "
                        f"Make it clear, well-organized, and student-friendly."
                    )
                    notes = ask_ai([{"role": "user", "content": prompt}], system_base)
                    st.session_state.notes = notes
                    st.session_state.notes_topic = notes_topic
                except Exception as e:
                    st.error(f"Error: {e}")

    if "notes" in st.session_state:
        st.markdown("---")
        st.markdown(f"### 📖 {st.session_state.notes_topic}")
        st.markdown(st.session_state.notes)
        st.markdown("---")
        st.download_button(
            label="⬇️ Download Notes" if lang_key == "English" else "⬇️ Soo deji Xusuus-qorka",
            data=st.session_state.notes,
            file_name=f"SIMAD_Notes_{st.session_state.notes_topic.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("© 2026 SIMAD University · Mogadishu, Somalia · AI Tutor Phase 2")
