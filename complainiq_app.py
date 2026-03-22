"""
ComplainIQ v3.0 — Union Bank of India
Agentic AI Complaint Resolution Dashboard
==========================================
INSTALL:  pip install streamlit plotly anthropic
RUN:      streamlit run complainiq_v3.py

FIXES in v3:
- HTML rendering bug completely fixed (no more raw code display)
- All HTML uses double-quoted attributes inside triple-quoted strings
- CSAT-Gated Resolution
- 2nd Resolution Engine
- Social Media Priority 0
- Demo mode (no API key needed)
- Fixed Claude API (haiku model — free tier)
"""

import streamlit as st
import plotly.graph_objects as go
import json, time, random

try:
    import anthropic
    ANTHROPIC_OK = True
except ImportError:
    ANTHROPIC_OK = False

# ══════════════════════════════════════════
# COLORS
# ══════════════════════════════════════════
BLUE    = "#003087"
GOLD    = "#F5A623"
LBLUE   = "#E8F0FE"
CRIT    = "#C62828"
HIGH    = "#E65100"
MED     = "#F9A825"
GOOD    = "#2E7D32"
PINK    = "#880E4F"

# ══════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════
st.set_page_config(
    page_title="ComplainIQ — Union Bank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════
# CSS — all styles in one block
# ══════════════════════════════════════════
st.markdown("""
<style>
/* ── Layout ── */
.stApp { background: #F0F4FB; }
section[data-testid="stSidebar"] { background: #003087 !important; }
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 14px; }
.block-container { padding-top: 1rem; }

/* ── Header ── */
.header-bar {
    background: #003087; color: white;
    padding: 14px 22px; border-radius: 12px;
    margin-bottom: 18px;
    display: flex; justify-content: space-between; align-items: center;
}
.header-bar h2 { margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 1px; }
.header-sub { color: #F5A623; font-size: 11px; margin-top: 3px; }
.header-right { text-align: right; }
.header-team { color: #F5A623; font-size: 18px; font-weight: 800; }
.header-tag { color: #aaa; font-size: 11px; }

/* ── Section title ── */
.sec-h {
    font-size: 19px; font-weight: 700; color: #003087;
    border-bottom: 3px solid #F5A623;
    padding-bottom: 6px; margin-bottom: 16px;
}

/* ── Cards ── */
.card {
    background: white; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 10px;
    border: 1px solid #dde6f5;
    box-shadow: 0 1px 6px rgba(0,48,135,0.06);
}
.card-social {
    background: #fff5f5; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 10px;
    border: 1px solid #ffcdd2;
    border-left: 4px solid #C62828;
    box-shadow: 0 1px 6px rgba(198,40,40,0.08);
}
.metric-card {
    background: white; border-radius: 10px;
    padding: 16px 18px;
    border-left: 5px solid #003087;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    height: 90px;
}

/* ── Badges & pills ── */
.b-crit  { background:#FFEBEE; color:#C62828; border:1px solid #C62828;
           padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.b-high  { background:#FFF3E0; color:#E65100; border:1px solid #E65100;
           padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.b-med   { background:#FFFDE7; color:#B8860B; border:1px solid #F9A825;
           padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.b-low   { background:#E8F5E9; color:#2E7D32; border:1px solid #2E7D32;
           padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.b-social{ background:#FCE4EC; color:#880E4F; border:1px solid #880E4F;
           padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; }

.p-open  { background:#E3F2FD; color:#1565C0; padding:2px 9px; border-radius:10px; font-size:11px; }
.p-csat  { background:#FFF8E1; color:#856404; padding:2px 9px; border-radius:10px; font-size:11px; font-weight:700; }
.p-done  { background:#E8F5E9; color:#2E7D32; padding:2px 9px; border-radius:10px; font-size:11px; }
.p-2nd   { background:#FFF3E0; color:#E65100; padding:2px 9px; border-radius:10px; font-size:11px; font-weight:700; }
.p-esc   { background:#FFEBEE; color:#C62828; padding:2px 9px; border-radius:10px; font-size:11px; }

/* ── Progress bars ── */
.bar-wrap { background:#E0E0E0; border-radius:4px; height:7px; margin-top:3px; }
.bar-fill { height:7px; border-radius:4px; }

/* ── Alert banners ── */
.social-alert {
    background:#FFEBEE; border:1.5px solid #C62828; border-radius:8px;
    padding:10px 16px; margin-bottom:14px;
    font-size:13px; color:#C62828; font-weight:600;
    animation: pulse-red 1.4s infinite;
}
@keyframes pulse-red {
    0%,100% { box-shadow: 0 0 0 0 rgba(198,40,40,0.3); }
    50%      { box-shadow: 0 0 0 5px rgba(198,40,40,0); }
}
.csat-bar {
    background:#FFF8E1; border:1.5px solid #F9A825;
    border-radius:10px; padding:14px 18px; margin:12px 0;
}
.resolved-bar {
    background:#E8F5E9; border:2px solid #2E7D32;
    border-radius:10px; padding:16px; text-align:center;
    color:#2E7D32; font-size:17px; font-weight:700;
}
.second-bar {
    background:#FFF3E0; border:1.5px solid #E65100;
    border-radius:10px; padding:12px 16px; margin:10px 0;
    color:#E65100; font-size:13px; font-weight:600;
}
.ai-card {
    background:#E8F0FE; border-left:5px solid #F5A623;
    border-radius:10px; padding:16px 20px; margin:14px 0;
}

/* ── Impact banner ── */
.impact-row {
    background:#003087; border-radius:12px;
    padding:18px 24px; margin-top:10px;
    display:flex; justify-content:space-around; align-items:center;
}
.impact-num { font-size:28px; font-weight:800; color:#F5A623; text-align:center; }
.impact-lbl { font-size:11px; color:rgba(255,255,255,0.8); text-align:center; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# COMPLAINTS DATA
# ══════════════════════════════════════════
COMPLAINTS = [
    {
        "id": "UBI2024031547", "customer": "Ramesh Sharma",
        "phone": "+91-9876543210", "channel": "WhatsApp", "icon": "💬",
        "type": "NEFT Failure", "severity": "Critical",
        "is_social": False, "shares": 0,
        "sla": 1.2, "frustration": 9.1, "status": "Open",
        "time": "10:32 AM, 19 Mar",
        "text": (
            "I am Ramesh Sharma. I transferred ₹45,000 from my Union Bank account "
            "to my son's account on 3rd March. The money was debited from my account "
            "but never credited to his account. It has been 4 days. I am very worried. "
            "My UTR number is UBI20240303487291. Please help immediately."
        ),
    },
    {
        "id": "UBI2024031548", "customer": "@angry_user99 — Twitter/X",
        "phone": "Twitter DM", "channel": "Twitter/X", "icon": "🐦",
        "type": "UPI Failure", "severity": "Critical",
        "is_social": True, "shares": 312,
        "sla": 0.5, "frustration": 9.8, "status": "Open",
        "time": "09:45 AM, 19 Mar",
        "text": (
            "@UnionBankof_Ind WORST BANK EVER. My UPI payment of ₹12,000 failed "
            "but money was deducted 3 days ago. No response from customer care after "
            "6 calls. Going to RBI Ombudsman and making this viral. #UnionBankFail"
        ),
    },
    {
        "id": "UBI2024031549", "customer": "Anita Singh",
        "phone": "+91-9543210987", "channel": "Mobile App", "icon": "📱",
        "type": "Credit Card Fraud", "severity": "Critical",
        "is_social": False, "shares": 0,
        "sla": 0.8, "frustration": 9.4, "status": "Escalated",
        "time": "11:02 AM, 19 Mar",
        "text": (
            "My credit card has been used fraudulently. I see 3 transactions totaling "
            "₹18,500 — two at a Delhi petrol pump and one online. I am in Mumbai. "
            "Please block my card immediately. Card ending 4521."
        ),
    },
    {
        "id": "UBI2024031550", "customer": "Priya Mehta",
        "phone": "+91-9765432109", "channel": "Email", "icon": "📧",
        "type": "Wrong Debit", "severity": "High",
        "is_social": False, "shares": 0,
        "sla": 3.5, "frustration": 7.2, "status": "Open",
        "time": "09:15 AM, 19 Mar",
        "text": (
            "₹2,500 was debited from my savings account SB00234567 yesterday without "
            "my knowledge. I did not make any transaction. Please investigate and "
            "refund immediately."
        ),
    },
    {
        "id": "UBI2024031551", "customer": "Suresh Patel",
        "phone": "+91-9654321098", "channel": "Branch", "icon": "🏦",
        "type": "KYC Update", "severity": "Medium",
        "is_social": False, "shares": 0,
        "sla": 18.0, "frustration": 5.1, "status": "Open",
        "time": "08:45 AM, 19 Mar",
        "text": (
            "Mera naam Suresh Patel hai. Main apna address update karna chahta hoon. "
            "Maine teen baar branch mein jaake form jama kiya lekin abhi tak update "
            "nahi hua. Kripya jaldi se update karein."
        ),
    },
    {
        "id": "UBI2024031552", "customer": "Kavita Rao",
        "phone": "+91-9321098765", "channel": "Net Banking", "icon": "🌐",
        "type": "Net Banking Access", "severity": "Medium",
        "is_social": False, "shares": 0,
        "sla": 12.0, "frustration": 6.3, "status": "Open",
        "time": "03:45 PM, 18 Mar",
        "text": (
            "Unable to login to net banking since yesterday. Shows account temporarily "
            "blocked. Tried calling customer care but on hold 45 minutes. "
            "Need to pay EMI today to avoid penalty."
        ),
    },
]

# ══════════════════════════════════════════
# DEMO AI RESPONSES
# ══════════════════════════════════════════
DEMO = {
    "UBI2024031547": {
        "category": "NEFT Failure", "severity": 9, "sentiment_score": 9,
        "language": "English", "urgency": "Immediate",
        "summary": "₹45,000 NEFT transfer debited but not credited to beneficiary for 4 days.",
        "root_cause": "Transaction stuck in suspense account during NEFT batch processing.",
        "draft_reply": (
            "Dear Mr. Ramesh Sharma,\n\n"
            "We sincerely apologise for the inconvenience. Your complaint is registered as "
            "SR: UBI2024031547.\n\n"
            "Our NEFT reconciliation team is investigating UTR UBI20240303487291 on priority. "
            "Resolution expected within 24 hours. As per RBI guidelines, compensation of "
            "₹100/day for the delay will be credited automatically.\n\n"
            "Thank you for your patience.\nUnion Bank of India"
        ),
    },
    "UBI2024031548": {
        "category": "UPI Failure", "severity": 10, "sentiment_score": 10,
        "language": "English", "urgency": "Immediate — Social P0",
        "summary": "₹12,000 UPI payment failed but money deducted 3 days ago. Viral tweet — 312 retweets.",
        "root_cause": "UPI transaction in NPCI pending reconciliation queue.",
        "draft_reply": (
            "Dear Valued Customer,\n\n"
            "We are extremely sorry and are treating this as our highest priority. "
            "SR: UBI2024031548.\n\n"
            "Your ₹12,000 UPI transaction is being investigated by our payments team "
            "right now. We will resolve this within 2 hours. Please DM us your "
            "registered mobile number so we can call you directly.\n\n"
            "Union Bank of India"
        ),
    },
    "UBI2024031549": {
        "category": "Credit Card Fraud", "severity": 10, "sentiment_score": 9,
        "language": "English", "urgency": "Immediate",
        "summary": "Fraudulent transactions of ₹18,500 on credit card while customer is in a different city.",
        "root_cause": "Card details compromised — possible card cloning.",
        "draft_reply": (
            "Dear Ms. Anita Singh,\n\n"
            "Your card ending 4521 has been BLOCKED immediately. SR: UBI2024031549.\n\n"
            "Chargeback for ₹18,500 has been initiated. Provisional credit within "
            "7 working days. Please visit nearest branch for replacement card.\n\n"
            "Union Bank Fraud Prevention Team"
        ),
    },
    "UBI2024031550": {
        "category": "Unauthorized Debit", "severity": 7, "sentiment_score": 7,
        "language": "English", "urgency": "Within 24 hrs",
        "summary": "Unauthorized debit of ₹2,500 from savings account.",
        "root_cause": "Possible auto-debit mandate triggered incorrectly.",
        "draft_reply": (
            "Dear Ms. Priya Mehta,\n\n"
            "We apologise for the debit of ₹2,500. SR: UBI2024031550.\n\n"
            "Our team is investigating and will provide resolution within 24 hours. "
            "If confirmed unauthorized, the amount will be reversed immediately.\n\n"
            "Union Bank of India"
        ),
    },
    "UBI2024031551": {
        "category": "KYC Update", "severity": 5, "sentiment_score": 6,
        "language": "Hindi", "urgency": "Within 5 days",
        "summary": "Address update submitted 3 times at branch but not processed.",
        "root_cause": "KYC update pending in backend processing queue.",
        "draft_reply": (
            "प्रिय श्री सुरेश पटेल,\n\n"
            "आपकी शिकायत के लिए हम खेद व्यक्त करते हैं। SR: UBI2024031551.\n\n"
            "आपका address update 48 घंटों में पूरा किया जाएगा। SMS से सूचित किया जाएगा।\n\n"
            "यूनियन बैंक ऑफ इंडिया"
        ),
    },
    "UBI2024031552": {
        "category": "Net Banking Access", "severity": 6, "sentiment_score": 7,
        "language": "English", "urgency": "Within 24 hrs",
        "summary": "Net banking locked due to security trigger, EMI payment due today.",
        "root_cause": "Multiple failed login attempts triggered security lock.",
        "draft_reply": (
            "Dear Ms. Kavita Rao,\n\n"
            "We apologise for the inconvenience. SR: UBI2024031552.\n\n"
            "Your net banking access will be restored within 2 hours. For today's EMI, "
            "use UPI or visit nearest branch. We have also escalated the 45-minute "
            "hold issue to our contact centre management.\n\n"
            "Union Bank of India"
        ),
    },
}

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
for k, v in {
    "page": "inbox", "sel": None,
    "api_key": "", "demo": True,
    "states": {},
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def cs(cid):
    if cid not in st.session_state.states:
        st.session_state.states[cid] = {
            "status": None, "csat": None,
            "res_time": None, "ai": None,
            "t0": None, "round": 1,
        }
    return st.session_state.states[cid]

def by_id(cid):
    return next((c for c in COMPLAINTS if c["id"] == cid), None)

# ══════════════════════════════════════════
# HELPERS — return clean HTML strings
# ══════════════════════════════════════════
def sev_badge(sev, is_social=False):
    if is_social:
        return '<span class="b-social">SOCIAL P0</span>'
    m = {"Critical": "b-crit", "High": "b-high", "Medium": "b-med", "Low": "b-low"}
    return f'<span class="{m.get(sev, "b-low")}">{sev.upper()}</span>'

def status_pill(state_status, orig):
    if state_status == "pending_csat":
        return '<span class="p-csat">Pending CSAT</span>'
    if state_status == "resolved":
        return '<span class="p-done">Resolved ✅</span>'
    if state_status == "2nd_attempt":
        return '<span class="p-2nd">2nd Attempt</span>'
    if orig == "Escalated":
        return '<span class="p-esc">Escalated</span>'
    return '<span class="p-open">Open</span>'

def sla_color(h):
    return CRIT if h < 1 else HIGH if h < 4 else GOOD

def frus_color(f):
    return CRIT if f >= 8 else HIGH if f >= 6 else GOOD

def bar_html(pct, color):
    return (
        '<div class="bar-wrap">'
        f'<div class="bar-fill" style="width:{pct}%;background:{color}"></div>'
        '</div>'
    )

# ══════════════════════════════════════════
# CLAUDE API
# ══════════════════════════════════════════
def call_ai(text, cid):
    if st.session_state.demo or not st.session_state.api_key:
        time.sleep(1.2)
        return DEMO.get(cid, DEMO["UBI2024031550"])
    if not ANTHROPIC_OK:
        st.error("Run: pip install anthropic")
        return DEMO.get(cid, DEMO["UBI2024031550"])
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key.strip())
        SYS = (
            "You are ComplainIQ — complaint analysis AI for Union Bank of India. "
            "Return ONLY valid JSON, no markdown, no extra text. "
            'Keys: "category","severity"(1-10),"sentiment_score"(1-10),'
            '"language","urgency","summary","root_cause","draft_reply"'
        )
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800, system=SYS,
            messages=[{"role": "user", "content": f"Analyze:\n{text}"}],
        )
        raw = r.content[0].text.strip()
        if "```" in raw:
            for p in raw.split("```"):
                p = p.strip().lstrip("json").strip()
                if p.startswith("{"):
                    raw = p
                    break
        return json.loads(raw)
    except json.JSONDecodeError:
        return DEMO.get(cid, DEMO["UBI2024031550"])
    except Exception as e:
        msg = str(e)
        if "401" in msg:
            st.error("Invalid API key — check console.anthropic.com")
        elif "429" in msg:
            st.error("Rate limit — using demo response")
        else:
            st.error(f"API error: {msg}")
        return DEMO.get(cid, DEMO["UBI2024031550"])

# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:8px 0 18px'>"
        "<div style='font-size:34px'>🏦</div>"
        "<div style='font-size:17px;font-weight:800;letter-spacing:2px;color:white'>ComplainIQ</div>"
        "<div style='font-size:11px;color:#F5A623;margin-top:2px'>Union Bank of India</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    nav = st.radio("Navigate", ["📥  Inbox", "📊  Analytics", "⚙️  Settings"], index=0)
    page_sel = nav.split("  ")[1]
    st.markdown("---")

    # stats
    open_n  = sum(1 for c in COMPLAINTS if cs(c["id"])["status"] not in ("resolved",))
    soc_n   = sum(1 for c in COMPLAINTS if c["is_social"] and cs(c["id"])["status"] != "resolved")
    csat_n  = sum(1 for c in COMPLAINTS if cs(c["id"])["status"] == "pending_csat")
    sec_n   = sum(1 for c in COMPLAINTS if cs(c["id"])["status"] == "2nd_attempt")
    done_n  = sum(1 for c in COMPLAINTS if cs(c["id"])["status"] == "resolved")

    def stat_row(label, n, color):
        return (
            f"<div style='display:flex;justify-content:space-between;"
            f"align-items:center;margin-bottom:5px'>"
            f"<span style='color:white;font-size:13px'>{label}</span>"
            f"<span style='background:{color};color:white;padding:1px 9px;"
            f"border-radius:9px;font-size:12px'>{n}</span></div>"
        )

    st.markdown(
        "<div style='font-size:10px;color:#aaa;text-transform:uppercase;"
        "letter-spacing:1px;margin-bottom:8px'>LIVE STATS</div>"
        + stat_row("Open", open_n, "#1565C0")
        + stat_row("Social P0 🔴", soc_n, CRIT)
        + stat_row("CSAT pending", csat_n, "#856404")
        + stat_row("2nd attempt", sec_n, HIGH)
        + stat_row("Resolved ✅", done_n, GOOD),
        unsafe_allow_html=True,
    )
    st.markdown("---")
    mode_txt = "Demo mode (no API key needed)" if st.session_state.demo else "Live AI mode"
    mode_col = GOLD if st.session_state.demo else "#4CAF50"
    st.markdown(
        f"<div style='color:{mode_col};font-size:11px'>● {mode_txt}</div>"
        "<div style='color:rgba(255,255,255,0.35);font-size:10px;margin-top:3px'>"
        "Agent: Riya Wagh | Mumbai</div>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════
# GLOBAL HEADER
# ══════════════════════════════════════════
st.markdown(
    "<div class='header-bar'>"
    "<div><h2>🏦 ComplainIQ</h2>"
    "<div class='header-sub'>AI-Powered Complaint Resolution · Union Bank · iDEA 2.0 PS5</div>"
    "</div>"
    "<div class='header-right'>"
    "<div class='header-team'>Team Avinya</div>"
    "<div class='header-tag'>One Dashboard. Every Complaint. Zero Delays.</div>"
    "</div></div>",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: COMPLAINT DETAIL
# ══════════════════════════════════════════════════════════════════════
if st.session_state.page == "detail" and st.session_state.sel:
    cid = st.session_state.sel
    c   = by_id(cid)
    s   = cs(cid)

    if st.button("← Back to Inbox"):
        st.session_state.page = "inbox"
        st.rerun()

    st.markdown(f"<div class='sec-h'>Complaint Detail — {cid}</div>", unsafe_allow_html=True)

    # ── 4 info cards ──
    sc = CRIT if c["severity"] == "Critical" else HIGH if c["severity"] == "High" else MED
    fc = frus_color(c["frustration"])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div style='font-size:11px;color:#888'>Customer</div>"
            f"<div style='font-size:14px;font-weight:700;color:{BLUE};margin-top:3px'>{c['customer']}</div>"
            f"<div style='font-size:11px;color:#aaa'>{c['phone']}</div>"
            "</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div style='font-size:11px;color:#888'>Channel</div>"
            f"<div style='font-size:22px;margin-top:2px'>{c['icon']}</div>"
            f"<div style='font-size:12px;font-weight:600;color:{BLUE}'>{c['channel']}</div>"
            "</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(
            f"<div class='metric-card' style='border-left-color:{sc}'>"
            f"<div style='font-size:11px;color:#888'>Severity</div>"
            f"<div style='margin-top:5px'>{sev_badge(c['severity'], c['is_social'])}</div>"
            f"<div style='font-size:11px;color:{sc};margin-top:4px'>SLA: {c['sla']:.1f}h left</div>"
            "</div>", unsafe_allow_html=True)
    with col4:
        st.markdown(
            f"<div class='metric-card' style='border-left-color:{fc}'>"
            f"<div style='font-size:11px;color:#888'>Frustration score</div>"
            f"<div style='font-size:26px;font-weight:800;color:{fc};margin-top:2px'>{c['frustration']}/10</div>"
            "</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Social media banner ──
    if c["is_social"]:
        viral = c["shares"] * 10
        st.markdown(
            f"<div class='social-alert'>"
            f"🚨 SOCIAL MEDIA — PRIORITY 0 &nbsp;|&nbsp; "
            f"Viral Risk Score: <strong>{viral}</strong> &nbsp;|&nbsp; "
            f"Retweets: <strong>{c['shares']}</strong> &nbsp;|&nbsp; "
            f"SLA: <strong>1 hour</strong> &nbsp;|&nbsp; Public reply — professional tone required"
            "</div>", unsafe_allow_html=True)

    # ── 2nd attempt banner ──
    if s["round"] == 2:
        st.markdown(
            "<div class='second-bar'>"
            "🔄 2ND RESOLUTION ATTEMPT — Senior Agent Assigned &nbsp;|&nbsp; "
            "Customer was unsatisfied with first reply &nbsp;|&nbsp; "
            "Higher urgency SLA applied"
            "</div>", unsafe_allow_html=True)

    # ── Complaint text ──
    st.markdown("**📝 Original Complaint**")
    st.markdown(
        f"<div class='card' style='border-left:4px solid {BLUE};"
        f"font-size:14px;line-height:1.8;color:#333'>{c['text']}</div>",
        unsafe_allow_html=True)

    # ──────────────────────────────────────
    #  STATE: RESOLVED
    # ──────────────────────────────────────
    if s["status"] == "resolved":
        stars = "★" * (s["csat"] or 5)
        st.markdown(
            f"<div class='resolved-bar'>"
            f"✅ Complaint Officially Resolved — Customer Confirmed Satisfaction<br>"
            f"<span style='font-size:13px;font-weight:400'>"
            f"Resolved in {s.get('res_time','N/A')}s &nbsp;|&nbsp; "
            f"CSAT: {stars} &nbsp;|&nbsp; RBI Log Filed"
            f"</span></div>", unsafe_allow_html=True)

    # ──────────────────────────────────────
    #  STATE: PENDING CSAT
    # ──────────────────────────────────────
    elif s["status"] == "pending_csat":
        st.markdown(
            "<div class='csat-bar'>"
            "<strong>⏳ Pending Customer Confirmation (CSAT)</strong><br>"
            "<span style='font-size:12px;color:#666'>"
            "Reply sent. Complaint stays OPEN until customer confirms satisfaction "
            "— as required by RBI complaint resolution guidelines."
            "</span></div>", unsafe_allow_html=True)

        st.markdown("**Simulate Customer Response:**")
        score = st.slider("Customer satisfaction (1=very unhappy, 5=very happy)", 1, 5, 4)
        c1, c2 = st.columns(2)
        with c1:
            btn_label = "✅ Customer Satisfied — Close Complaint" if score >= 4 else "Customer gave neutral score"
            if score >= 4:
                if st.button(btn_label, type="primary", use_container_width=True):
                    s["status"] = "resolved"
                    s["csat"] = score
                    s["res_time"] = s.get("res_time", random.randint(35, 80))
                    st.rerun()
            else:
                st.info(f"Score {score}/5 — use button below to trigger 2nd resolution")
        with c2:
            if st.button("😞 Customer Unsatisfied — Open 2nd Resolution", use_container_width=True):
                s["status"] = "2nd_attempt"
                s["csat"] = score
                s["round"] = 2
                s["ai"] = None
                st.rerun()

    # ──────────────────────────────────────
    #  STATE: 2ND ATTEMPT
    # ──────────────────────────────────────
    elif s["status"] == "2nd_attempt":
        if s["ai"] is None:
            if st.button("⚡ Re-Analyze with AI — 2nd Attempt (Higher Urgency)", type="primary"):
                with st.spinner("Re-analyzing with escalated urgency..."):
                    result = call_ai(c["text"], cid)
                    result["severity"] = min(10, result.get("severity", 5) + 2)
                    result["urgency"] = "Immediate — 2nd Attempt"
                    result["summary"] = "[2ND ATTEMPT] " + result.get("summary", "")
                    s["ai"] = result
                    s["t0"] = time.time()
                    st.rerun()
        else:
            # Fall through to show AI card below
            pass

    # ──────────────────────────────────────
    #  STATE: OPEN (or 2nd attempt with AI ready)
    # ──────────────────────────────────────
    if s["status"] in (None, "2nd_attempt") and s["status"] != "pending_csat" and s["status"] != "resolved":
        if s["ai"] is None:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚡ Analyze with AI", type="primary"):
                with st.spinner("🤖 ComplainIQ AI analyzing complaint..."):
                    result = call_ai(c["text"], cid)
                    s["ai"] = result
                    s["t0"] = time.time()
                    st.rerun()

        if s["ai"] is not None:
            r = s["ai"]
            sv = r.get("severity", 5)
            sc_col = CRIT if sv >= 8 else HIGH if sv >= 5 else GOOD

            # AI Analysis Card — built with concatenation to avoid f-string quote issues
            ai_html = (
                "<div class='ai-card'>"
                "<div style='font-size:15px;font-weight:700;color:" + BLUE + ";margin-bottom:12px'>"
                "🤖 ComplainIQ AI Analysis</div>"
                "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px'>"

                "<div><div style='font-size:10px;color:#666;text-transform:uppercase;"
                "letter-spacing:1px'>Category</div>"
                "<div style='font-size:13px;font-weight:700;color:" + BLUE + ";margin-top:3px'>"
                + str(r.get("category", "—")) + "</div></div>"

                "<div><div style='font-size:10px;color:#666;text-transform:uppercase;"
                "letter-spacing:1px'>Severity</div>"
                "<div style='font-size:24px;font-weight:800;color:" + sc_col + ";margin-top:1px'>"
                + str(r.get("severity", "—")) + "/10</div></div>"

                "<div><div style='font-size:10px;color:#666;text-transform:uppercase;"
                "letter-spacing:1px'>Sentiment</div>"
                "<div style='font-size:24px;font-weight:800;color:" + sc_col + ";margin-top:1px'>"
                + str(r.get("sentiment_score", "—")) + "/10</div></div>"

                "<div><div style='font-size:10px;color:#666;text-transform:uppercase;"
                "letter-spacing:1px'>Urgency</div>"
                "<div style='font-size:12px;font-weight:700;color:" + CRIT + ";margin-top:4px'>"
                + str(r.get("urgency", "—")) + "</div></div>"
                "</div>"

                "<div style='border-top:1px solid #C5CAE9;padding-top:8px;margin-bottom:6px'>"
                "<span style='font-size:10px;color:#666;text-transform:uppercase;letter-spacing:1px'>"
                "Language</span>"
                "<span style='font-size:13px;color:#333;margin-left:8px'>"
                + str(r.get("language", "—")) + "</span></div>"

                "<div style='margin-bottom:6px'>"
                "<div style='font-size:10px;color:#666;text-transform:uppercase;letter-spacing:1px'>"
                "Summary</div>"
                "<div style='font-size:13px;color:#333;margin-top:3px'>"
                + str(r.get("summary", "—")) + "</div></div>"

                "<div><div style='font-size:10px;color:#666;text-transform:uppercase;letter-spacing:1px'>"
                "Root cause</div>"
                "<div style='font-size:13px;color:#333;margin-top:3px'>"
                + str(r.get("root_cause", "—")) + "</div></div>"
                "</div>"
            )
            st.markdown(ai_html, unsafe_allow_html=True)

            # Draft reply
            st.markdown("**✍️ AI Draft Reply — Review & Edit**")
            draft = str(r.get("draft_reply", "")).replace("[SR_NUM]", cid)
            edited = st.text_area("", value=draft, height=200,
                                  key=f"draft_{cid}_{s['round']}")

            st.markdown("<br>", unsafe_allow_html=True)
            ca, cb, cc = st.columns(3)
            with ca:
                if st.button("✅ Approve & Send Reply", type="primary", use_container_width=True):
                    elapsed = round(time.time() - (s["t0"] or time.time()))
                    s["status"] = "pending_csat"
                    s["res_time"] = elapsed + random.randint(10, 20)
                    st.rerun()
            with cb:
                if st.button("🔺 Escalate to Manager", use_container_width=True):
                    st.warning("Escalated to Branch Manager — Senior officer notified.")
            with cc:
                if st.button("🔄 Re-analyze", use_container_width=True):
                    s["ai"] = None
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════
#  PAGE: INBOX
# ══════════════════════════════════════════════════════════════════════
elif page_sel == "Inbox" and st.session_state.page != "detail":

    st.markdown("<div class='sec-h'>📥 Complaint Inbox</div>", unsafe_allow_html=True)

    # Social banner
    soc_open = [c for c in COMPLAINTS if c["is_social"] and cs(c["id"])["status"] != "resolved"]
    if soc_open:
        total_shares = sum(c["shares"] for c in soc_open)
        st.markdown(
            f"<div class='social-alert'>"
            f"🚨 {len(soc_open)} SOCIAL MEDIA COMPLAINT(S) — PRIORITY 0 &nbsp;|&nbsp; "
            f"Total viral reach: {total_shares} shares &nbsp;|&nbsp; SLA: 1 hour — assign immediately"
            "</div>", unsafe_allow_html=True)

    # Filters
    c1, c2, c3 = st.columns([2, 2, 4])
    with c1:
        fsev = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
    with c2:
        fchan = st.selectbox("Channel", ["All", "Social Media", "WhatsApp", "Email",
                                          "Branch", "Mobile App", "Net Banking"])
    with c3:
        search = st.text_input("🔍 Search customer or SR number", "")

    st.markdown("---")

    # Sort: social first, then by frustration desc
    sorted_c = sorted(COMPLAINTS, key=lambda x: (0 if x["is_social"] else 1, -x["frustration"]))

    shown = 0
    for c in sorted_c:
        s = cs(c["id"])
        eff_status = s["status"] or c["status"]

        if fsev != "All" and c["severity"] != fsev: continue
        if fchan == "Social Media" and not c["is_social"]: continue
        if fchan not in ("All", "Social Media") and c["channel"] != fchan: continue
        if search and search.lower() not in c["customer"].lower() \
                  and search.lower() not in c["id"].lower(): continue

        sla_pct = max(4, min(100, int((c["sla"] / 48) * 100)))
        sla_c   = sla_color(c["sla"])
        f_pct   = int(c["frustration"] * 10)
        f_c     = frus_color(c["frustration"])
        card_cls = "card-social" if c["is_social"] else "card"

        soc_tag = '<span class="b-social">SOCIAL P0</span>&nbsp;' if c["is_social"] else ""
        viral_tag = ""
        if c["is_social"]:
            viral_tag = (
                f"<span style='color:{CRIT};font-size:12px;font-weight:600'>"
                f"🔥 {c['shares']} shares &nbsp;|&nbsp; "
                f"Viral risk: {c['shares']*10}"
                f"</span>"
            )

        col_card, col_btn = st.columns([9, 1])
        with col_card:
            html = (
                f"<div class='{card_cls}'>"

                # Row 1: name + badges
                "<div style='display:flex;justify-content:space-between;"
                "align-items:center;margin-bottom:8px'>"
                "<div>"
                f"<span style='font-weight:700;font-size:15px;color:{BLUE}'>{c['customer']}</span>"
                f"<span style='color:#888;font-size:12px;margin-left:10px'>#{c['id']}</span>"
                "</div>"
                f"<div style='display:flex;gap:6px;align-items:center'>"
                f"{soc_tag}{sev_badge(c['severity'])}&nbsp;{status_pill(eff_status, c['status'])}"
                "</div></div>"

                # Row 2: meta
                "<div style='display:flex;gap:18px;align-items:center;margin-bottom:8px;"
                "flex-wrap:wrap'>"
                f"<span style='font-size:13px'>{c['icon']} {c['channel']}</span>"
                f"<span style='color:{BLUE};font-weight:600;font-size:13px'>📋 {c['type']}</span>"
                f"<span style='color:{sla_c};font-weight:600;font-size:12px'>⏱ {c['sla']:.1f}h SLA</span>"
                f"<span style='color:#888;font-size:12px'>🕐 {c['time']}</span>"
                f"{viral_tag}"
                "</div>"

                # Row 3: bars + preview
                "<div style='display:flex;gap:14px;align-items:center'>"

                "<div style='min-width:110px'>"
                "<div style='font-size:10px;color:#888;margin-bottom:2px'>SLA remaining</div>"
                + bar_html(sla_pct, sla_c) +
                "</div>"

                "<div style='min-width:110px'>"
                f"<div style='font-size:10px;color:#888;margin-bottom:2px'>Frustration {c['frustration']}/10</div>"
                + bar_html(f_pct, f_c) +
                "</div>"

                f"<div style='font-size:12px;color:#555;overflow:hidden;"
                f"white-space:nowrap;text-overflow:ellipsis;flex:1'>"
                f"&ldquo;{c['text'][:95]}...&rdquo;"
                "</div>"

                "</div>"  # row 3
                "</div>"  # card
            )
            st.markdown(html, unsafe_allow_html=True)

        with col_btn:
            st.markdown("<div style='padding-top:22px'>", unsafe_allow_html=True)
            if st.button("Open →", key=f"btn_{c['id']}"):
                st.session_state.sel = c["id"]
                st.session_state.page = "detail"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        shown += 1

    if shown == 0:
        st.info("No complaints match your filters.")

# ══════════════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════
elif page_sel == "Analytics":
    st.markdown("<div class='sec-h'>📊 Analytics Dashboard</div>", unsafe_allow_html=True)

    res_n  = sum(1 for c in COMPLAINTS if cs(c["id"])["status"] == "resolved")
    csat_n = sum(1 for c in COMPLAINTS if cs(c["id"])["status"] == "pending_csat")
    sec_n  = sum(1 for c in COMPLAINTS if cs(c["id"])["status"] == "2nd_attempt")

    m1, m2, m3, m4 = st.columns(4)
    def mcard(val, label, color=BLUE):
        return (
            f"<div class='metric-card' style='border-left-color:{color}'>"
            f"<div style='font-size:30px;font-weight:700;color:{color}'>{val}</div>"
            f"<div style='font-size:12px;color:#666;margin-top:3px'>{label}</div>"
            "</div>"
        )
    with m1: st.markdown(mcard(len(COMPLAINTS), "Total complaints today"), unsafe_allow_html=True)
    with m2: st.markdown(mcard(res_n, "CSAT-confirmed resolved", GOOD), unsafe_allow_html=True)
    with m3: st.markdown(mcard(csat_n, "Pending CSAT", "#856404"), unsafe_allow_html=True)
    with m4: st.markdown(mcard(sec_n, "2nd resolution attempts", HIGH), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns(2)

    with cl:
        fig = go.Figure(go.Bar(
            x=["NEFT Failure", "UPI Failure", "Fraud", "KYC", "Net Banking", "Wrong Debit"],
            y=[34, 28, 19, 15, 22, 18],
            marker_color=[BLUE, CRIT, CRIT, GOLD, BLUE, HIGH],
            text=[34, 28, 19, 15, 22, 18], textposition="outside",
        ))
        fig.update_layout(
            title="Complaints by category (this week)",
            plot_bgcolor="white", paper_bgcolor="white",
            height=300, margin=dict(t=40, b=60, l=10, r=10),
            xaxis=dict(tickangle=-30, tickfont=dict(size=11)),
            yaxis=dict(gridcolor="#EEE"), showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with cr:
        fig2 = go.Figure(go.Pie(
            labels=["Auto-resolved L1", "One-click L2", "Escalated L3"],
            values=[61, 34, 5], hole=0.55,
            marker_colors=[GOOD, GOLD, CRIT],
        ))
        fig2.update_layout(
            title="Resolution levels — agentic AI",
            paper_bgcolor="white", height=300,
            margin=dict(t=40, b=20, l=10, r=10),
            legend=dict(orientation="h", y=-0.1),
            annotations=[dict(text="<b>61%</b><br>auto",
                              x=0.5, y=0.5, font_size=14,
                              showarrow=False, font_color=GOOD)],
        )
        st.plotly_chart(fig2, use_container_width=True)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=days, y=[42,58,51,67,73,38,29],
                              name="Received", line=dict(color=BLUE,width=3), mode="lines+markers"))
    fig3.add_trace(go.Scatter(x=days, y=[38,54,48,63,70,36,27],
                              name="CSAT Confirmed", line=dict(color=GOOD,width=3,dash="dot"),
                              mode="lines+markers", fill="tozeroy",
                              fillcolor="rgba(46,125,50,0.05)"))
    fig3.add_trace(go.Scatter(x=days, y=[3,6,4,8,7,3,2],
                              name="2nd Attempt", line=dict(color=HIGH,width=2,dash="dash"),
                              mode="lines+markers"))
    fig3.update_layout(
        title="7-day volume: received vs CSAT-confirmed vs 2nd attempts",
        plot_bgcolor="white", paper_bgcolor="white",
        height=280, margin=dict(t=40, b=20, l=10, r=10),
        legend=dict(orientation="h", y=1.15),
        yaxis=dict(gridcolor="#EEE"), hovermode="x unified",
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(
        "<div class='impact-row'>"
        "<div><div class='impact-num'>70%</div><div class='impact-lbl'>Faster resolution</div></div>"
        "<div><div class='impact-num'>3x</div><div class='impact-lbl'>Agent capacity</div></div>"
        "<div><div class='impact-num'>61%</div><div class='impact-lbl'>Zero-touch auto-resolve</div></div>"
        "<div><div class='impact-num'>85%+</div><div class='impact-lbl'>CSAT target</div></div>"
        "<div><div class='impact-num'>₹0</div><div class='impact-lbl'>RBI penalty target</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════
#  PAGE: SETTINGS
# ══════════════════════════════════════════════════════════════════════
elif page_sel == "Settings":
    st.markdown("<div class='sec-h'>⚙️ Settings</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            "<div class='card'>"
            f"<div style='font-size:15px;font-weight:700;color:{BLUE};margin-bottom:10px'>Claude API Key</div>"
            "<p style='color:#555;font-size:13px;line-height:1.7'>"
            "Get free key at <a href='https://console.anthropic.com' target='_blank'>"
            "console.anthropic.com</a><br>"
            "The app works in <strong>Demo Mode</strong> without a key — realistic pre-computed responses.<br>"
            "Add your key for <strong>live AI analysis</strong> on any complaint text."
            "</p></div>",
            unsafe_allow_html=True,
        )
        key_in = st.text_input("API Key", value=st.session_state.api_key,
                               type="password", placeholder="sk-ant-api03-...")
        ca, cb = st.columns(2)
        with ca:
            if st.button("💾 Save & Enable Live AI", type="primary", use_container_width=True):
                if key_in.strip().startswith("sk-ant"):
                    st.session_state.api_key = key_in.strip()
                    st.session_state.demo = False
                    st.success("✅ API key saved — Live AI mode enabled!")
                elif key_in.strip():
                    st.error("Key must start with sk-ant-api03-...")
                else:
                    st.warning("Enter your API key first")
        with cb:
            if st.button("🎭 Use Demo Mode", use_container_width=True):
                st.session_state.demo = True
                st.session_state.api_key = ""
                st.success("Demo mode enabled!")

    with col2:
        dm = st.session_state.demo
        st.markdown(
            "<div class='card'>"
            f"<div style='font-size:12px;color:#666;margin-bottom:8px'>Current mode</div>"
            f"<div style='color:{GOOD if dm else '#aaa'};font-weight:700;margin-bottom:4px'>"
            f"{'● ' if dm else '○ '}Demo: {'Active' if dm else 'Inactive'}</div>"
            f"<div style='color:{GOOD if not dm else '#aaa'};font-weight:700'>"
            f"{'● ' if not dm else '○ '}Live AI: {'Active' if not dm else 'Inactive'}</div>"
            "<div style='color:#888;font-size:11px;margin-top:10px'>"
            "Model: claude-haiku-4-5-20251001<br>"
            "Cost: ~$0.001 per analysis<br>"
            "Free tier: 1000+ calls/day"
            "</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='card' style='background:#FFF8E1;border-left:4px solid #F5A623;margin-top:14px'>"
        f"<strong style='color:{BLUE}'>🚀 Quick Start</strong>"
        "<ol style='color:#555;font-size:13px;margin-top:8px;line-height:2.2'>"
        "<li>Demo mode works instantly — no setup needed</li>"
        "<li>Go to <strong>Inbox</strong> → click <strong>Open →</strong> on any complaint</li>"
        "<li>Click <strong>Analyze with AI</strong> → see category, severity, draft reply</li>"
        "<li>Click <strong>Approve &amp; Send</strong> → complaint moves to CSAT pending</li>"
        "<li>Rate customer satisfaction (1–5) → see full CSAT lifecycle</li>"
        "<li>Try the <strong>Twitter complaint</strong> — Social Media Priority 0 alert</li>"
        "<li>Rate 1–3 stars to trigger the <strong>2nd Resolution Engine</strong></li>"
        "</ol></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='card' style='margin-top:12px'>"
        f"<strong style='color:{BLUE}'>About ComplainIQ v3.0</strong>"
        "<p style='color:#555;font-size:13px;margin-top:6px;line-height:1.7'>"
        "<strong>Hackathon:</strong> iDEA 2.0 — PSBs Hackathon Series 2026 | Union Bank<br>"
        "<strong>Problem:</strong> PS5 — Unified Customer Complaint Communication Dashboard<br>"
        "<strong>Team:</strong> Avinya — Gauri · Sharayu · Riya · Shweta<br>"
        "<strong>v3 fixes:</strong> HTML rendering bug · CSAT loop · 2nd resolution · Social P0"
        "</p></div>",
        unsafe_allow_html=True,
    )