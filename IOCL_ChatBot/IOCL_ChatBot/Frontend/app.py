
"""
IOCL ChatBot - Streamlit Frontend
Orange & White theme | Bilingual Hindi + English
"""

import streamlit as st
import requests
import uuid
import base64
from datetime import datetime
from pathlib import Path


BACKEND_URL   = "http://localhost:5000"
CHAT_API      = f"{BACKEND_URL}/api/chat"
KNOWLEDGE_API = f"{BACKEND_URL}/api/knowledge"
HEALTH_API    = f"{BACKEND_URL}/api/chat/health"

st.set_page_config(
    page_title="IOCL ChatBot",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_logo_b64():
    p = Path(__file__).parent / "logo.jpeg"
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

LOGO_B64 = get_logo_b64()

ORANGE      = "#D2691E"
ORANGE_DARK = "#B8520A"
ORANGE_LITE = "#FFF6EE"
NAVY        = "#0D2461"
WHITE       = "#FFFFFF"

st.markdown(f"""
<style>
/* PAGE */
.stApp {{ background-color: {ORANGE_LITE} !important; }}

/* SIDEBAR */
[data-testid="stSidebar"] > div:first-child {{
    background-color: {WHITE} !important;
    border-right: 3px solid {ORANGE} !important;
}}

/* ALL SIDEBAR BUTTONS */
[data-testid="stSidebar"] .stButton button {{
    background-color: {WHITE} !important;
    color: {ORANGE_DARK} !important;
    border: 2px solid {ORANGE} !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    text-align: left !important;
    padding: 9px 13px !important;
    width: 100% !important;
    margin-bottom: 4px !important;
    line-height: 1.4 !important;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    background-color: {ORANGE_LITE} !important;
    border-color: {ORANGE_DARK} !important;
}}

/* SEND BUTTON */
div[data-testid="column"]:last-child .stButton button {{
    background-color: {ORANGE} !important;
    color: {WHITE} !important;
    border: 2px solid {ORANGE_DARK} !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    width: 100% !important;
    padding: 9px 10px !important;
}}
div[data-testid="column"]:last-child .stButton button:hover {{
    background-color: {ORANGE_DARK} !important;
}}

/* WHITE FRAME INPUT */
.stTextInput > div > div > input {{
    background-color: {WHITE} !important;
    color: #1a1a1a !important;
    border: 2.5px solid {ORANGE} !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    font-size: 15px !important;
}}
.stTextInput > div > div > input:focus {{
    border: 2.5px solid {ORANGE_DARK} !important;
    background-color: {WHITE} !important;
    box-shadow: 0 0 0 3px rgba(210,105,30,0.18) !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder {{
    color: #BBBBBB !important;
    font-style: italic;
}}
.stTextInput > div {{
    background-color: {WHITE} !important;
    border-radius: 8px !important;
}}

/* TABS - dark orange color */
.stTabs [data-baseweb="tab-list"] {{
    border-bottom: 2.5px solid {ORANGE} !important;
    background-color: {WHITE} !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {ORANGE_DARK} !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}}
.stTabs [aria-selected="true"] {{
    color: {ORANGE_DARK} !important;
    border-bottom: 3px solid {ORANGE} !important;
    font-weight: 800 !important;
}}

/* RADIO - dark orange */
.stRadio > div {{
    flex-direction: row !important;
    gap: 16px !important;
}}
.stRadio label {{
    font-size: 14px !important;
    font-weight: 700 !important;
    color: {ORANGE_DARK} !important;
}}
.stRadio [data-testid="stMarkdownContainer"] p {{
    color: {ORANGE_DARK} !important;
    font-weight: 700 !important;
}}

/* ALL BODY TEXT - dark color */
.stMarkdown p {{
    color: #1a1a1a !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}}
.stMarkdown {{
    color: #1a1a1a !important;
}}
div[data-testid="stMarkdownContainer"] p {{
    color: #1a1a1a !important;
}}

/* DIVIDER */
hr {{ border-color: {ORANGE} !important; opacity: 0.25 !important; }}

/* Hide Streamlit chrome */
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 1.2rem !important; }}

/* EXPANDERS */
details > summary {{
    color: {ORANGE_DARK} !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}}

/* SELECTBOX */
.stSelectbox > div > div {{
    color: {ORANGE_DARK} !important;
    font-weight: 600 !important;
    border: 2px solid {ORANGE} !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("session_id", str(uuid.uuid4())), ("messages", []), ("language", "en")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
def check_backend():
    try:
        return requests.get(HEALTH_API, timeout=3).status_code == 200
    except:
        return False

def send_message(msg, lang):
    try:
        r = requests.post(CHAT_API,
            json={"message": msg, "language": lang,
                  "sessionId": st.session_state.session_id},
            timeout=30)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {
        "answer": ("⚠️ बैकेंड से कनेक्शन नहीं। `dotnet run` चलाएं।"
                   if lang == "hi" else
                   "⚠️ Cannot connect to backend. Please run `dotnet run`."),
        "found": False, "category": "Error", "relatedTopics": [], "policyReference": ""
    }

def get_policies(lang, cat=None):
    try:
        url = f"{KNOWLEDGE_API}?lang={lang}" + (f"&category={cat}" if cat else "")
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def push(text):
    ts = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": text, "ts": ts})
    with st.spinner("Thinking…" if st.session_state.language == "en" else "सोच रहा हूँ…"):
        resp = send_message(text, st.session_state.language)
    st.session_state.messages.append({
        "role": "bot",
        "content":  resp.get("answer", ""),
        "ts":       datetime.now().strftime("%H:%M"),
        "cat":      resp.get("category", ""),
        "ref":      resp.get("policyReference", ""),
        "related":  resp.get("relatedTopics", []),
    })
    st.rerun()

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    logo_html = ""
    if LOGO_B64:
        logo_html = (f'<img src="data:image/jpeg;base64,{LOGO_B64}" '
                 f'style="width:90px;display:block;margin:0 auto 8px;'
                 f'border-radius:6px;" />')

    st.markdown(
    f'<div style="text-align:center;padding-bottom:14px;'
    f'border-bottom:2px solid {ORANGE};margin-bottom:14px;">'
    f'{logo_html}'
    f'<div style="color:{ORANGE_DARK};font-size:17px;font-weight:800;'
    f'margin:6px 0 3px;">IOCL ChatBot</div>'
    f'<div style="color:{NAVY};font-size:11px;font-weight:600;">'
    f'IT Policies &amp; CDA Rules</div></div>',
    unsafe_allow_html=True)

    # Backend status
    is_online = check_backend()
    if is_online:
        st.markdown(
            f'<div style="background:#e6f4ea;color:#1a7a32;border:1px solid #82c99a;'
            f'padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700;'
            f'display:inline-block;margin-bottom:8px;">● Backend online</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="background:#fdecea;color:#b71c1c;border:1px solid #f4a5a5;'
            f'padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700;'
            f'display:inline-block;margin-bottom:8px;">● Backend offline</div>',
            unsafe_allow_html=True)

    st.divider()

    # Language label - dark orange
    st.markdown(
        f'<div style="font-size:13px;font-weight:800;color:{ORANGE_DARK};'
        f'text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;">'
        f'🌐 Language / भाषा</div>',
        unsafe_allow_html=True)

    lang_pick = st.radio("lang", ["English", "हिंदी"],
                         index=0 if st.session_state.language == "en" else 1,
                         label_visibility="collapsed")
    st.session_state.language = "en" if lang_pick == "English" else "hi"

    st.divider()

    # Quick topics label - dark orange
    st.markdown(
        f'<div style="font-size:13px;font-weight:800;color:{ORANGE_DARK};'
        f'text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;">'
        f'📌 Quick Topics</div>',
        unsafe_allow_html=True)

    topics_en = [
        ("📧  Email policy",          "What is the email policy?"),
        ("🔐  Password rules",         "What are the password requirements?"),
        ("📱  Social media policy",    "What is the social media policy?"),
        ("🎁  Gifts and vendors",      "Can I accept gifts from vendors?"),
        ("⚠️  Disciplinary action",    "What is the disciplinary proceedings process?"),
        ("💻  Cyber security",         "What to do in case of a cyber attack?"),
        ("🏠  Work from home / VPN",   "What is the remote work and VPN policy?"),
        ("💼  Outside employment",     "Can officers do freelance work outside IOCL?"),
    ]
    topics_hi = [
        ("📧  ईमेल नीति",             "ईमेल नीति क्या है?"),
        ("🔐  पासवर्ड नियम",          "पासवर्ड की आवश्यकताएँ क्या हैं?"),
        ("📱  सोशल मीडिया",           "सोशल मीडिया नीति क्या है?"),
        ("🎁  उपहार और विक्रेता",     "क्या मैं विक्रेता से उपहार ले सकता हूँ?"),
        ("⚠️  अनुशासनात्मक",          "अनुशासनात्मक कार्यवाही की प्रक्रिया क्या है?"),
        ("💻  साइबर सुरक्षा",         "साइबर हमले में क्या करें?"),
        ("🏠  वर्क फ्रॉम होम",        "VPN और रिमोट वर्क नीति क्या है?"),
        ("💼  बाहरी रोजगार",          "क्या अधिकारी IOCL के बाहर फ्रीलांस कर सकते हैं?"),
    ]

    topics = topics_en if st.session_state.language == "en" else topics_hi
    for label, query in topics:
        if st.button(label, key=f"qt_{label}", use_container_width=True):
            push(query)

    st.divider()
    if st.button("🗑️  Clear chat" if st.session_state.language == "en"
                 else "🗑️  चैट साफ करें", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown(
        f'<div style="font-size:10px;color:#bbb;margin-top:10px;">'
        f'Session: {st.session_state.session_id[:8]}… | '
        f'Msgs: {len(st.session_state.messages)}</div>',
        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
subtitle = ("IT Policies and CDA Rules assistant | Ask in Hindi or English"
            if st.session_state.language == "en" else
            "IT नीतियों और CDA नियमों का सहायक | हिंदी या अंग्रेजी")

if LOGO_B64:
    st.markdown(
        f'<div style="background:{ORANGE};border-radius:12px;padding:16px 26px;'
        f'display:flex;align-items:center;gap:20px;margin-bottom:16px;">'
        f'<img src="data:image/jpeg;base64,{LOGO_B64}" '
        f'style="height:64px;border-radius:8px;background:#fff;padding:4px;" />'
        f'<div><div style="color:#FFFFFF;font-size:26px;font-weight:800;">'
        f'IOCL ChatBot</div>'
        f'<div style="color:rgba(255,255,255,0.90);font-size:13px;margin-top:4px;">'
        f'{subtitle}</div></div></div>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<div style="background:{ORANGE};border-radius:12px;padding:16px 26px;'
        f'margin-bottom:16px;text-align:center;">'
        f'<div style="color:#FFFFFF;font-size:26px;font-weight:800;">IOCL ChatBot</div>'
        f'<div style="color:rgba(255,255,255,0.90);font-size:13px;margin-top:4px;">'
        f'{subtitle}</div></div>',
        unsafe_allow_html=True)

# Tabs
if st.session_state.language == "en":
    tab_chat, tab_browse = st.tabs(["💬  Chat", "📚  Policy Browser"])
else:
    tab_chat, tab_browse = st.tabs(["💬  चैट", "📚  नीति ब्राउज़र"])

# ── TAB 1: Chat ───────────────────────────────────────────────────────────────
with tab_chat:
    if not st.session_state.messages:
        st.markdown(f"""
        <div style="background:{NAVY};color:{WHITE};padding:16px;
                    border-radius:10px;border-left:6px solid {ORANGE};
                    font-size:15px;line-height:1.7;margin-bottom:14px;">
            👋 <b>{'Welcome!' if st.session_state.language == 'en' else 'नमस्ते!'}</b><br><br>
            {'Ask anything about <b>IOCL IT Policies</b> or <b>CDA Rules</b> in <b>Hindi or English</b>.<br><b>Example:</b> What is the Email Policy?'
             if st.session_state.language == 'en' else
             'IOCL की <b>IT Policies</b> या <b>CDA Rules</b> के बारे में <b>हिंदी या English</b> में पूछें।<br><b>उदाहरण:</b> ईमेल नीति क्या है?'}
        </div>
        """, unsafe_allow_html=True)

    # Render messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="background:{ORANGE};color:{WHITE};padding:10px 16px;
                        border-radius:16px 16px 4px 16px;margin:8px 0 2px 24%;
                        font-size:14px;line-height:1.6;font-weight:500;">
                {msg["content"]}
            </div>
            <div style="font-size:10px;color:#bbb;text-align:right;
                        margin-bottom:6px;">{msg.get("ts","")}</div>
            """, unsafe_allow_html=True)
        else:
            chips = ""
            if msg.get("cat"):
                chips += (f'<span style="background:{ORANGE_LITE};color:{ORANGE_DARK};'
                          f'border:1.5px solid {ORANGE};padding:2px 10px;'
                          f'border-radius:20px;font-size:11px;font-weight:700;'
                          f'margin-right:5px;">{msg["cat"]}</span>')
            if msg.get("ref"):
                chips += (f'<span style="background:{NAVY};color:{WHITE};'
                          f'padding:2px 10px;border-radius:20px;'
                          f'font-size:11px;font-weight:700;">{msg["ref"]}</span>')

            # Bot bubble with dark text
            answer_html = msg["content"].replace("\n", "<br>").replace("**", "")
            st.markdown(f"""
            <div style="background:{WHITE};border-left:4px solid {ORANGE};
                        border-top:1px solid #F0D5C0;border-right:1px solid #F0D5C0;
                        border-bottom:1px solid #F0D5C0;padding:12px 16px;
                        border-radius:0 12px 12px 12px;margin:8px 24% 6px 0;
                        color:#1a1a1a;">
                {f'<div style="margin-bottom:8px;">{chips}</div>' if chips else ""}
                <div style="color:#1a1a1a;font-size:14px;line-height:1.7;
                            font-weight:400;">
                    {answer_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if msg.get("related"):
                with st.expander(
                    "🔗 Related topics" if st.session_state.language == "en"
                    else "🔗 संबंधित विषय"):
                    for t in msg["related"]:
                        st.markdown(
                            f'<span style="color:{ORANGE_DARK};font-weight:600;">'
                            f'• {t}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # Input row
    ph = ("Type your question here…"
          if st.session_state.language == "en"
          else "यहाँ अपना प्रश्न टाइप करें…")

    col_in, col_btn = st.columns([5, 1])
    with col_in:
        user_input = st.text_input("question", key="chat_input",
                                   placeholder=ph,
                                   label_visibility="collapsed")
    with col_btn:
        send_clicked = st.button(
            "Send ➤" if st.session_state.language == "en" else "भेजें ➤",
            use_container_width=True, key="send_btn")

    if send_clicked and user_input.strip():
        push(user_input.strip())

# ── TAB 2: Policy Browser ─────────────────────────────────────────────────────
with tab_browse:
    # Heading in navy blue
    st.markdown(
        f'<h3 style="color:{NAVY};font-weight:800;margin-bottom:14px;">'
        f'{"📚 Browse All Policies" if st.session_state.language == "en" else "📚 सभी नीतियाँ ब्राउज़ करें"}'
        f'</h3>',
        unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        search_q = st.text_input(
            "Search", label_visibility="collapsed",
            placeholder="Search policies…" if st.session_state.language == "en"
                        else "नीतियाँ खोजें…")
    with c2:
        cat_sel = st.selectbox("Cat", ["All", "IT Policy", "CDA Rules"],
                               label_visibility="collapsed")

    if search_q:
        try:
            r = requests.get(
                f"{KNOWLEDGE_API}/search?q={search_q}"
                f"&lang={st.session_state.language}", timeout=5)
            policies = r.json() if r.status_code == 200 else []
        except:
            policies = []
    else:
        policies = get_policies(st.session_state.language,
                                None if cat_sel == "All" else cat_sel)

    if policies:
        for p in policies:
            icon = "💻" if p.get("category") == "IT Policy" else "📜"
            with st.expander(
                f"{icon}  [{p.get('id','')}]  "
                f"{p.get('title', p.get('subCategory',''))}"):
                c1, c2 = st.columns(2)
                c1.markdown(
                    f'<span style="color:{ORANGE_DARK};font-weight:700;">Category:</span> '
                    f'<span style="color:#1a1a1a;">{p.get("category","")}</span>',
                    unsafe_allow_html=True)
                c1.markdown(
                    f'<span style="color:{ORANGE_DARK};font-weight:700;">Sub-category:</span> '
                    f'<span style="color:#1a1a1a;">{p.get("subCategory","")}</span>',
                    unsafe_allow_html=True)
                c2.markdown(
                    f'<span style="color:{ORANGE_DARK};font-weight:700;">Policy ref:</span> '
                    f'<code style="background:{ORANGE_LITE};color:{NAVY};padding:2px 6px;">'
                    f'{p.get("policyReference","")}</code>',
                    unsafe_allow_html=True)
                if "answer" in p:
                    st.markdown("---")
                    st.markdown(
                        f'<div style="color:#1a1a1a;font-size:14px;line-height:1.7;">'
                        f'{p["answer"]}</div>', unsafe_allow_html=True)
                else:
                    if st.button("Ask about this →", key=f"ask_{p.get('id')}"):
                        push(p.get("title", ""))
    elif not is_online:
        st.warning("Start the .NET backend (`dotnet run`) to load policies."
                   if st.session_state.language == "en"
                   else "नीतियाँ लोड करने के लिए .NET बैकेंड शुरू करें।")
    else:
        st.markdown(
            f'<div style="color:{NAVY};font-weight:600;font-size:14px;">'
            f'{"No policies found." if st.session_state.language == "en" else "कोई नीति नहीं मिली।"}'
            f'</div>', unsafe_allow_html=True)


