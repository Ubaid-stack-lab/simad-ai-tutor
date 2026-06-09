import streamlit as st
from groq import Groq
import pdfplumber
import io
import json
from datetime import datetime
import plotly.graph_objects as go

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIMAD AI Tutor",
    page_icon="🎓",
    layout="centered",
    menu_items={"About": "SIMAD AI Tutor — Jaamacadda SIMAD · Muqdisho, Soomaaliya"}
)

# ── Custom CSS (SIMAD branding) ───────────────────────────────────────────────
st.markdown("""
<style>
    /* SIMAD brand colors: navy blue + gold */
    :root {
        --simad-navy: #003366;
        --simad-gold: #C9A84C;
        --simad-light: #f0f4f8;
    }
    .stApp { background-color: #f8fafc; }

    /* Header banner */
    .simad-header {
        background: linear-gradient(135deg, #003366 0%, #005099 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .simad-header h1 { color: #C9A84C; font-size: 2rem; margin: 0; }
    .simad-header p  { color: #cce0ff; margin: 0.3rem 0 0 0; font-size: 0.95rem; }

    /* Mode cards */
    .mode-card {
        background: white;
        border-left: 4px solid #C9A84C;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    }

    /* Score badge */
    .score-badge {
        background: linear-gradient(135deg, #003366, #005099);
        color: #C9A84C;
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        font-size: 1.4rem;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }

    /* Progress stat boxes */
    .stat-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .stat-number { font-size: 2rem; font-weight: bold; color: #003366; }
    .stat-label  { font-size: 0.8rem; color: #666; }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003366 0%, #001f44 100%);
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] .stRadio label { color: white !important; }
    section[data-testid="stSidebar"] .stSelectbox label { color: white !important; }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #003366, #005099);
        color: #C9A84C;
        border: none;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #002244, #003d77);
        color: #e6c76a;
    }

    /* Chat messages */
    .stChatMessage { border-radius: 12px; }

    /* Footer */
    .simad-footer {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        padding: 1rem 0;
        border-top: 1px solid #e0e0e0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

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

# ── Init session state ────────────────────────────────────────────────────────
if "messages"       not in st.session_state: st.session_state.messages = []
if "quiz_history"   not in st.session_state: st.session_state.quiz_history = []
if "total_chats"    not in st.session_state: st.session_state.total_chats = 0
if "streak"         not in st.session_state: st.session_state.streak = 0
if "last_activity"  not in st.session_state: st.session_state.last_activity = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(SIMAD_LOGO, use_container_width=True)
    st.markdown("### 🎓 SIMAD AI Tutor")
    st.caption("Jaamacadda SIMAD · Muqdisho")
    st.markdown("---")

    language = st.radio("🌐 Language", ["English", "Somali (Soomaali)"])
    lang_key = "Somali" if "Soomaali" in language else "English"

    faculty = st.selectbox(
        "🏛️ Faculty" if lang_key == "English" else "🏛️ Kulliyad", FACULTIES
    )
    student_name = st.text_input(
        "👤 Your Name" if lang_key == "English" else "👤 Magacaaga",
        placeholder="Optional"
    )

    st.markdown("---")
    mode = st.radio(
        "📚 Mode" if lang_key == "English" else "📚 Qaab",
        ["🏠 Home", "💬 Chat", "📝 Quiz", "📄 Study Notes", "📋 Past Paper Analyzer", "📊 My Progress"]
    )
    st.markdown("---")
    if st.button("🗑️ Clear Chat" if lang_key == "English" else "🗑️ Tirtir", use_container_width=True):
        st.session_state.messages = []
        for k in ["quiz_questions","quiz_index","quiz_score","quiz_done","notes"]:
            st.session_state.pop(k, None)
        st.rerun()
    st.markdown("---")
    # Mini stats in sidebar
    quizzes = len(st.session_state.quiz_history)
    avg = int(sum(q["pct"] for q in st.session_state.quiz_history) / quizzes) if quizzes else 0
    st.markdown(f"📊 **Quizzes taken:** {quizzes}")
    st.markdown(f"⭐ **Avg score:** {avg}%")

if not api_key:
    st.image(SIMAD_LOGO, width=250)
    st.markdown('<div class="simad-header"><h1>🎓 SIMAD AI Tutor</h1><p>Jaamacadda SIMAD · Muqdisho, Soomaaliya</p></div>', unsafe_allow_html=True)
    st.info("Enter your Groq API key in the sidebar to begin.")
    st.stop()

greeting  = f"Hello{', ' + student_name if student_name else ''}! 👋" if lang_key == "English" else f"Salaan{', ' + student_name if student_name else ''}! 👋"
system_base = SYSTEM_PROMPT[lang_key].format(faculty=faculty)
if student_name:
    system_base += f" The student's name is {student_name}. Address them by name occasionally."

# ════════════════════════════════════════════════════════════════
# HOME
# ════════════════════════════════════════════════════════════════
if mode == "🏠 Home":
    st.markdown(f'''
    <div class="simad-header">
        <h1>🎓 SIMAD AI Tutor</h1>
        <p>Jaamacadda SIMAD · Muqdisho, Soomaaliya · Powered by AI</p>
    </div>
    ''', unsafe_allow_html=True)

    name_display = f", {student_name}" if student_name else ""
    welcome = f"Welcome{name_display}!" if lang_key == "English" else f"Soo dhawoow{name_display}!"
    st.markdown(f"### {welcome}")
    st.markdown(f"**Faculty:** {faculty}")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    quizzes = len(st.session_state.quiz_history)
    avg = int(sum(q["pct"] for q in st.session_state.quiz_history) / quizzes) if quizzes else 0

    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{quizzes}</div><div class="stat-label">Quizzes Taken</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{avg}%</div><div class="stat-label">Avg Quiz Score</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{st.session_state.total_chats}</div><div class="stat-label">Questions Asked</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 What do you want to do?" if lang_key == "English" else "### 🚀 Maxaad rabta?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="mode-card">💬 <b>Chat</b><br><small>Ask your tutor anything</small></div>', unsafe_allow_html=True)
        st.markdown('<div class="mode-card">📄 <b>Study Notes</b><br><small>Generate notes on any topic</small></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="mode-card">📝 <b>Quiz</b><br><small>Test your knowledge</small></div>', unsafe_allow_html=True)
        st.markdown('<div class="mode-card">📋 <b>Past Paper Analyzer</b><br><small>Upload & analyze past exams</small></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 Select a mode from the sidebar to get started!" if lang_key == "English" else "👈 Qaabka ka dooro dhinaca bidixda!")

# ════════════════════════════════════════════════════════════════
# CHAT
# ════════════════════════════════════════════════════════════════
elif mode == "💬 Chat":
    st.markdown(f'''<div class="simad-header"><h1>💬 Chat</h1><p>{greeting} · {faculty}</p></div>''', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(f"**{'💡 Try asking:' if lang_key == 'English' else '💡 Isku day:'}**")
        for q in SUGGESTED_QUESTIONS.get(faculty, []):
            if st.button(q, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()
        st.markdown("---")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question..." if lang_key == "English" else "Su'aal weydii..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.total_chats += 1
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
# QUIZ
# ════════════════════════════════════════════════════════════════
elif mode == "📝 Quiz":
    st.markdown(f'''<div class="simad-header"><h1>📝 Quiz Mode</h1><p>{greeting} · {faculty}</p></div>''', unsafe_allow_html=True)

    topic = st.text_input(
        "Enter a topic:" if lang_key == "English" else "Mowduuca geli:",
        placeholder="e.g. Data Structures, Epidemiology, Contract Law..."
    )

    if st.button("🎯 Start Quiz", type="primary", use_container_width=True):
        if topic.strip():
            with st.spinner("Generating quiz..."):
                try:
                    prompt = (
                        f"Generate exactly 5 multiple choice questions about '{topic}' for a {faculty} student. "
                        f"Format EXACTLY:\nQ: [question]\nA) [option]\nB) [option]\nC) [option]\nD) [option]\nANSWER: [letter]\n\n"
                        f"Separate each with ---"
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
            options = [l for l in lines if l.startswith(("A)","B)","C)","D)"))]
            correct = next((l for l in lines if l.startswith("ANSWER:")), "").replace("ANSWER:","").strip()

            st.markdown("---")
            st.progress(idx / len(questions), text=f"Question {idx+1} of {len(questions)}")
            st.markdown(f"### {question_text}")
            choice = st.radio("", options, key=f"q_{idx}", label_visibility="collapsed")

            if st.button("✅ Submit Answer", use_container_width=True):
                selected = choice[0] if choice else ""
                if selected == correct:
                    st.success("✅ Correct!" if lang_key == "English" else "✅ Saxan!")
                    st.session_state.quiz_score += 1
                else:
                    st.error(f"❌ Correct answer: **{correct}**")
                st.session_state.quiz_index += 1
                if st.session_state.quiz_index >= len(questions):
                    st.session_state.quiz_done = True
                st.rerun()

    if st.session_state.get("quiz_done"):
        score = st.session_state.quiz_score
        total = len(st.session_state.quiz_questions)
        pct   = int((score / total) * 100)

        # Save to history
        st.session_state.quiz_history.append({
            "topic": st.session_state.get("quiz_topic", "Unknown"),
            "faculty": faculty,
            "score": score,
            "total": total,
            "pct": pct,
            "date": datetime.now().strftime("%b %d")
        })

        st.markdown("---")
        st.markdown(f'<div style="text-align:center"><div class="score-badge">🏆 {score}/{total} — {pct}%</div></div>', unsafe_allow_html=True)
        st.markdown("")

        if pct >= 80:
            st.success("🌟 Excellent! Outstanding performance!" if lang_key == "English" else "🌟 Aad u fiican! Waxaad si weyn u sameysay!")
        elif pct >= 60:
            st.info("📚 Good effort! Keep studying." if lang_key == "English" else "📚 Dadaal wanaagsan! Sii wad.")
        else:
            st.warning("💪 Keep practicing — you'll improve!" if lang_key == "English" else "💪 Sii wad celcelinta — waad wanaajin doontaa!")

        if st.button("🔄 New Quiz", use_container_width=True):
            for k in ["quiz_questions","quiz_index","quiz_score","quiz_done"]:
                st.session_state.pop(k, None)
            st.rerun()

# ════════════════════════════════════════════════════════════════
# STUDY NOTES
# ════════════════════════════════════════════════════════════════
elif mode == "📄 Study Notes":
    st.markdown(f'''<div class="simad-header"><h1>📄 Study Notes</h1><p>{greeting} · {faculty}</p></div>''', unsafe_allow_html=True)

    notes_topic = st.text_input(
        "Enter a topic:" if lang_key == "English" else "Mowduuca geli:",
        placeholder="e.g. Supply and Demand, Human Anatomy..."
    )

    if st.button("📄 Generate Notes", type="primary", use_container_width=True):
        if notes_topic.strip():
            with st.spinner("Generating study notes..."):
                try:
                    lang_i = "in English" if lang_key == "English" else "in Somali"
                    prompt = (
                        f"Create comprehensive study notes {lang_i} about '{notes_topic}' for a {faculty} student at SIMAD University, Somalia. "
                        f"Structure: 1) Overview, 2) Key Concepts, 3) Important Definitions, "
                        f"4) Real-world examples from Somalia, 5) Common exam questions, 6) Quick Summary."
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
        st.download_button(
            "⬇️ Download Notes" if lang_key == "English" else "⬇️ Soo deji",
            data=st.session_state.notes,
            file_name=f"SIMAD_Notes_{st.session_state.notes_topic.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ════════════════════════════════════════════════════════════════
# PAST PAPER ANALYZER
# ════════════════════════════════════════════════════════════════
elif mode == "📋 Past Paper Analyzer":
    st.markdown(f'''<div class="simad-header"><h1>📋 Past Paper Analyzer</h1><p>{greeting} · {faculty}</p></div>''', unsafe_allow_html=True)
    st.caption("Upload a past exam paper and I'll explain every question with model answers." if lang_key == "English" else "Warqada imtixaanka soo geli, su'aal kasta waan kuu sharxi doonaa.")

    input_method = st.radio("Input method:", ["📎 Upload PDF", "✏️ Paste Text"])
    exam_text = ""

    if input_method == "📎 Upload PDF":
        uploaded = st.file_uploader("Upload past exam (PDF)", type=["pdf"])
        if uploaded:
            with st.spinner("Reading PDF..."):
                try:
                    with pdfplumber.open(io.BytesIO(uploaded.read())) as pdf:
                        exam_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
                    st.success(f"✅ PDF loaded — {len(exam_text)} characters.")
                except Exception as e:
                    st.error(f"Could not read PDF: {e}")
    else:
        exam_text = st.text_area("Paste exam questions:", height=200, placeholder="Paste questions here...")

    analysis_type = st.radio("What do you want?", [
        "📖 Explain all questions with model answers",
        "🔑 Key topics & what to study",
        "⚡ Quick summary of the exam",
    ])

    if st.button("🔍 Analyze", type="primary", use_container_width=True):
        if exam_text.strip():
            with st.spinner("Analyzing..."):
                try:
                    lang_i = "in English" if lang_key == "English" else "in Somali"
                    if "Explain all" in analysis_type:
                        prompt = f"Analyze this {faculty} past exam. For each question provide: question text, model answer, key concepts. Respond {lang_i}.\n\nEXAM:\n{exam_text[:6000]}"
                    elif "Key topics" in analysis_type:
                        prompt = f"Analyze this {faculty} exam. Identify main topics, most tested areas, study priorities, predicted future topics. Respond {lang_i}.\n\nEXAM:\n{exam_text[:6000]}"
                    else:
                        prompt = f"Give a quick summary of this {faculty} exam: number of questions, main topics, difficulty, key advice. Respond {lang_i}.\n\nEXAM:\n{exam_text[:6000]}"

                    result = ask_ai([{"role": "user", "content": prompt}], system_base)
                    st.markdown("---")
                    st.markdown(result)
                    st.download_button("⬇️ Download Analysis", data=result, file_name="SIMAD_Exam_Analysis.txt", mime="text/plain", use_container_width=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please upload a PDF or paste exam text first.")

# ════════════════════════════════════════════════════════════════
# MY PROGRESS
# ════════════════════════════════════════════════════════════════
elif mode == "📊 My Progress":
    st.markdown(f'''<div class="simad-header"><h1>📊 My Progress</h1><p>{greeting} · {faculty}</p></div>''', unsafe_allow_html=True)

    history = st.session_state.quiz_history
    total_chats = st.session_state.total_chats

    col1, col2, col3 = st.columns(3)
    quizzes = len(history)
    avg = int(sum(q["pct"] for q in history) / quizzes) if quizzes else 0
    best = max((q["pct"] for q in history), default=0)

    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{quizzes}</div><div class="stat-label">Quizzes Taken</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{avg}%</div><div class="stat-label">Average Score</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{best}%</div><div class="stat-label">Best Score</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    if history:
        # Score chart
        st.markdown("### 📈 Quiz Score History")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[f"{h['topic']} ({h['date']})" for h in history],
            y=[h["pct"] for h in history],
            mode="lines+markers",
            marker=dict(color="#C9A84C", size=10),
            line=dict(color="#003366", width=2),
            fill="tozeroy",
            fillcolor="rgba(0,51,102,0.1)",
        ))
        fig.add_hline(y=60, line_dash="dot", line_color="orange", annotation_text="Pass (60%)")
        fig.add_hline(y=80, line_dash="dot", line_color="green", annotation_text="Excellent (80%)")
        fig.update_layout(
            yaxis=dict(range=[0, 105], title="Score %"),
            xaxis=dict(title="Quiz"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=350,
            margin=dict(l=20, r=20, t=20, b=80),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Quiz history table
        st.markdown("### 📋 Quiz History")
        for i, h in enumerate(reversed(history), 1):
            medal = "🥇" if h["pct"] >= 80 else "🥈" if h["pct"] >= 60 else "🥉"
            st.markdown(f"{medal} **{h['topic']}** — {h['score']}/{h['total']} ({h['pct']}%) · {h['faculty']} · {h['date']}")

        # Weak topics
        weak = [h["topic"] for h in history if h["pct"] < 60]
        if weak:
            st.markdown("---")
            st.warning(f"📌 **Topics to review:** {', '.join(set(weak))}")
    else:
        st.info("No quiz history yet. Take a quiz to start tracking your progress! 📝" if lang_key == "English" else "Wali taariikh imtixaan ma jirto. Imtixaan qaado si aad horumarkaaga u raadiso! 📝")
        st.markdown("👈 Go to **Quiz** mode to get started.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="simad-footer">© 2026 SIMAD University · Mogadishu, Somalia · AI Tutor · Built with ❤️ for Somali students</div>', unsafe_allow_html=True)
