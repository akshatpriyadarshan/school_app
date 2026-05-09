import streamlit as st
from database import init_db, authenticate_user
from students import render_students
from teachers import render_teachers
from fees import render_fee_structure
from admin import render_admin_panel

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Ram Prasad Chaudhary School",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Hide default Streamlit header */
    header[data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 1rem !important; }

    /* Login page wrapper */
    .login-wrapper {
        max-width: 440px;
        margin: 60px auto;
        background: white;
        border-radius: 20px;
        padding: 48px 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.12);
        border: 1px solid #f0f0f0;
    }
    .login-school-name {
        font-family: 'Playfair Display', serif;
        font-size: 22px;
        color: #1a1a2e;
        font-weight: 700;
        text-align: center;
        line-height: 1.3;
        margin-bottom: 4px;
    }
    .login-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        margin-bottom: 32px;
    }
    .login-icon {
        text-align: center;
        font-size: 48px;
        margin-bottom: 16px;
    }

    /* Top header bar */
    .top-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 16px 32px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }
    .school-title {
        font-family: 'Playfair Display', serif;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }
    .welcome-text {
        font-size: 14px;
        opacity: 0.85;
    }
    .role-badge {
        background: rgba(255,255,255,0.15);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f8fafc;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        font-size: 14px;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #1a1a2e !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 20px;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #f8fafc;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }

    /* Form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border-color: #e2e8f0 !important;
        font-size: 14px !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1a1a2e;
    }

    /* Info/success/error alerts */
    .stAlert {
        border-radius: 10px;
    }

    /* Logout button in top right */
    .logout-btn > button {
        background: rgba(255,255,255,0.15) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        font-size: 13px !important;
        padding: 4px 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── INIT DB ──────────────────────────────────────────────────────────────────

init_db()

# ─── SESSION STATE ────────────────────────────────────────────────────────────

if 'user' not in st.session_state:
    st.session_state['user'] = None

# ─── LOGIN PAGE ───────────────────────────────────────────────────────────────

def login_page():
    # Center the login form
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div class="login-icon">🏫</div>
        <div class="login-school-name">Ram Prasad Chaudhary School</div>
        <div class="login-subtitle">School Management Portal</div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            login_id = st.text_input("Login ID", placeholder="Enter your login ID", key="login_id_input")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass_input")
            submitted = st.form_submit_button("🔐  Sign In", use_container_width=True)

        if submitted:
            if not login_id.strip() or not password:
                st.error("Please enter both Login ID and Password.")
            else:
                user = authenticate_user(login_id.strip(), password)
                if user:
                    st.session_state['user'] = user
                    st.rerun()
                else:
                    st.error("Invalid Login ID or Password. Please try again.")

        st.markdown("""
        <div style="text-align:center; margin-top: 24px; color: #94a3b8; font-size: 12px;">
            Contact your administrator if you need access.
        </div>
        """, unsafe_allow_html=True)


# ─── HOME PAGE ────────────────────────────────────────────────────────────────

def home_page():
    user = st.session_state['user']
    role = user['role']

    # Header
    hcol1, hcol2 = st.columns([4, 1])
    with hcol1:
        st.markdown(f"""
        <div class="top-header">
            <div>
                <div class="school-title">🏫 Ram Prasad Chaudhary School</div>
                <div class="welcome-text">Welcome back, <strong>{user['name']}</strong></div>
            </div>
            <div class="role-badge">{role.upper()}</div>
        </div>
        """, unsafe_allow_html=True)
    with hcol2:
        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Build main tabs based on role
    if role == 'Teacher':
        # Teacher: Student + Fee Structure only
        tab_labels = ["🎓 Students", "📋 Fee Structure"]
        tabs = st.tabs(tab_labels)
        with tabs[0]:
            render_students(user)
        with tabs[1]:
            render_fee_structure(user)

    elif role == 'Manager':
        tab_labels = ["🎓 Students", "👨‍🏫 Teachers", "📋 Fee Structure"]
        tabs = st.tabs(tab_labels)
        with tabs[0]:
            render_students(user)
        with tabs[1]:
            render_teachers(user)
        with tabs[2]:
            render_fee_structure(user)

    elif role == 'Admin':
        tab_labels = ["🎓 Students", "👨‍🏫 Teachers", "📋 Fee Structure", "⚙️ Admin Panel"]
        tabs = st.tabs(tab_labels)
        with tabs[0]:
            render_students(user)
        with tabs[1]:
            render_teachers(user)
        with tabs[2]:
            render_fee_structure(user)
        with tabs[3]:
            render_admin_panel()


# ─── ROUTER ───────────────────────────────────────────────────────────────────

if st.session_state['user'] is None:
    login_page()
else:
    home_page()
