"""
F&B Multi-Agent AI System — Streamlit UI
"""
import streamlit as st
import time
from dotenv import load_dotenv

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="F&B AI System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main container */
    .block-container { padding-top: 1.5rem; }

    /* Brand header */
    .brand-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #e94560;
    }
    .brand-header h1 { color: #ffffff; margin: 0; font-size: 1.8rem; }
    .brand-header p  { color: #a8b2c1; margin: 0.3rem 0 0; font-size: 0.9rem; }

    /* Answer card */
    .answer-card {
        background: #0e1117;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        line-height: 1.7;
        font-size: 0.97rem;
    }

    /* Badge chips */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
    }
    .badge-intent  { background: #1e3a5f; color: #60a5fa; }
    .badge-agent   { background: #1e3d2f; color: #4ade80; }
    .badge-mode    { background: #3d2020; color: #f87171; }

    /* Pipeline step rows */
    .step-row {
        display: flex;
        align-items: center;
        padding: 0.45rem 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.3rem;
        font-size: 0.82rem;
        background: #161b22;
        border-left: 3px solid transparent;
    }
    .step-done   { border-left-color: #4ade80; }
    .step-block  { border-left-color: #f87171; }
    .step-skip   { border-left-color: #374151; opacity: 0.5; }
    .step-icon   { font-size: 1rem; margin-right: 0.5rem; min-width: 1.2rem; }
    .step-label  { flex: 1; color: #d1d5db; }
    .step-detail { color: #6b7280; font-size: 0.72rem; }

    /* Score bar */
    .score-bar-bg {
        background: #21262d;
        border-radius: 4px;
        height: 6px;
        margin-top: 3px;
    }
    .score-bar-fill {
        height: 6px;
        border-radius: 4px;
        background: linear-gradient(90deg, #4ade80, #22d3ee);
    }

    /* Sample queries */
    .sample-label { color: #6b7280; font-size: 0.8rem; margin-bottom: 0.5rem; }

    /* Citation list */
    .citation { color: #60a5fa; font-size: 0.8rem; }

    /* Blocked / redacted banner */
    .blocked-banner {
        background: #2d1515;
        border: 1px solid #f87171;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        color: #fca5a5;
        margin-top: 1rem;
    }
    .redacted-banner {
        background: #2d2010;
        border: 1px solid #fbbf24;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        color: #fde68a;
        margin-top: 1rem;
    }

    /* Metric cards */
    .metric-row { display: flex; gap: 1rem; margin-top: 0.8rem; }
    .metric-card {
        flex: 1;
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        text-align: center;
    }
    .metric-val  { font-size: 1.3rem; font-weight: 700; color: #e2e8f0; }
    .metric-lbl  { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }

    /* Hide Streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar — Architecture Guide ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ Pipeline Architecture")
    st.markdown("Each query travels through **10 stages**:")

    PIPELINE_STAGES = [
        ("🔄", "Query Reformation",     "Rewrites for clarity & precision"),
        ("🛡️", "Input Guardrail",        "Regex PII/injection + F&B topic check"),
        ("🧠", "Orchestrator",           "Classifies intent, picks agents"),
        ("✅", "Pre-Tool Guardrail",     "Validates agent params"),
        ("⚡", "Agent Execution",        "Parallel/sequential subagents"),
        ("🔗", "Response Aggregation",   "Merges all agent outputs"),
        ("📊", "Answer Evaluation",      "Scores relevance & completeness"),
        ("🔒", "Output Guardrail",       "Checks hallucinations & PII"),
        ("🎙️", "Tone of Voice",          "Aligns to F&B brand voice"),
        ("📤", "Final Response",         "Answer + citations + timer"),
    ]

    for icon, label, desc in PIPELINE_STAGES:
        st.markdown(
            f'<div class="step-row step-done">'
            f'<span class="step-icon">{icon}</span>'
            f'<span class="step-label"><b>{label}</b><br>'
            f'<span class="step-detail">{desc}</span></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🤖 Available Agents")
    agents_info = {
        "recipe_agent": "Recipes & cooking steps",
        "nutrition_agent": "Nutritional facts",
        "menu_agent": "Menu items & pricing",
        "recommendation_agent": "Personalised picks",
        "dietary_agent": "Dietary restrictions",
        "allergen_agent": "Allergen info",
        "pricing_agent": "Price queries",
        "inventory_agent": "Availability",
        "beverage_pairing_agent": "Wine & drink pairings",
        "comparison_agent": "Compare dishes",
        "sustainability_agent": "Eco-friendly options",
        "feedback_agent": "Reviews & ratings",
    }
    for name, desc in agents_info.items():
        st.markdown(f"- **{name.replace('_', ' ').title()}** — {desc}")

    st.markdown("---")
    st.markdown(
        '<p style="color:#6b7280;font-size:0.75rem;line-height:1.6;">'
        "Powered by GPT + LangGraph<br>"
        "© 2025 F&amp;B AI System<br><br>"
        '<b style="color:#a8b2c1;">Built by</b> '
        '<a href="https://www.linkedin.com/in/nisargkadam" target="_blank" '
        'style="color:#60a5fa;text-decoration:none;">Nisarg Kadam</a><br>'
        '<a href="mailto:nisargkadam23@gmail.com" '
        'style="color:#60a5fa;text-decoration:none;">nisargkadam23@gmail.com</a>'
        "</p>",
        unsafe_allow_html=True,
    )


# ─── Main Area ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
  <h1>🍽️ F&amp;B Multi-Agent AI System</h1>
  <p>Ask anything about our menu, recipes, nutrition, orders, and more — powered by 20 specialized AI agents.</p>
</div>
""", unsafe_allow_html=True)

# Sample quick-queries
SAMPLES = [
    "What vegetarian dishes do you have?",
    "How do I make the Mushroom Risotto?",
    "What are the calories in Chicken Biryani?",
    "Do you have anything gluten-free for dessert?",
    "Recommend a dish for a romantic dinner.",
    "What wine pairs with the Beef Tenderloin?",
]

st.markdown('<p class="sample-label">💡 Try a sample query:</p>', unsafe_allow_html=True)
sample_cols = st.columns(3)
for i, sample in enumerate(SAMPLES):
    if sample_cols[i % 3].button(sample, use_container_width=True, key=f"sample_{i}"):
        st.session_state["query_box"] = sample
        st.rerun()

# Query input
st.markdown("#### Your Question")
query_input = st.text_input(
    label="Query",
    label_visibility="collapsed",
    placeholder="e.g. What are your vegan options?",
    key="query_box",
)

ask_col, clear_col = st.columns([5, 1])
ask_btn   = ask_col.button("🔍 Ask", type="primary", use_container_width=True)
clear_btn = clear_col.button("✕ Clear", use_container_width=True)

if clear_btn:
    st.session_state.pop("last_query", None)
    st.session_state.pop("result", None)
    st.rerun()

# ─── Execute ─────────────────────────────────────────────────────────────────
if ask_btn and query_input.strip():
    st.session_state["last_query"] = query_input.strip()

    # Import here to avoid slow cold-start on page load
    from graph.main_graph import execute_query

    progress_placeholder = st.empty()

    # Simulate visible pipeline steps while the real graph runs
    steps_display = [
        "🔄 Reforming your query...",
        "🛡️ Running input guardrails...",
        "🧠 Classifying intent...",
        "✅ Validating agent parameters...",
        "⚡ Executing subagents...",
        "🔗 Aggregating responses...",
        "📊 Evaluating answer quality...",
        "🔒 Running output guardrails...",
        "🎙️ Checking tone of voice...",
        "📤 Building final response...",
    ]

    with progress_placeholder.container():
        status_box = st.status("Running pipeline...", expanded=True)
        for step in steps_display:
            status_box.write(step)
            time.sleep(0.15)

    with st.spinner(""):
        t0 = time.time()
        result = execute_query(query_input.strip())
        elapsed = time.time() - t0

    progress_placeholder.empty()
    st.session_state["result"] = result
    st.session_state["elapsed"] = elapsed

# ─── Display Result ───────────────────────────────────────────────────────────
if "result" in st.session_state:
    result  = st.session_state["result"]
    elapsed = st.session_state.get("elapsed", 0.0)
    status  = result.get("status", "SUCCESS")

    st.markdown("---")

    if status == "BLOCKED":
        st.markdown(
            f'<div class="blocked-banner">'
            f'<b>🚫 Query Blocked</b><br>'
            f'{result.get("message", result.get("reason", "This query was blocked by input guardrails."))}'
            f'</div>',
            unsafe_allow_html=True,
        )

    elif status == "REDACTED":
        st.markdown(
            f'<div class="redacted-banner">'
            f'<b>⚠️ Response Redacted</b><br>'
            f'{result.get("reason", "The response was redacted by output guardrails.")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    else:
        # ── Metadata badges ──────────────────────────────────────────────────
        intent = result.get("intent", "—")
        agents = result.get("agents_used", [])
        reformed = result.get("reformed_query", "")

        badge_html = (
            f'<span class="badge badge-intent">🎯 {intent.replace("_", " ").title()}</span>'
        )
        for a in agents:
            badge_html += f'<span class="badge badge-agent">🤖 {a.replace("_", " ").title()}</span>'

        st.markdown(badge_html, unsafe_allow_html=True)

        if reformed and reformed != st.session_state.get("last_query", ""):
            st.caption(f"*Reformulated:* {reformed}")

        # ── Answer ───────────────────────────────────────────────────────────
        st.markdown("#### 💬 Answer")
        answer_text = result.get("answer", "No answer generated.")
        st.markdown(
            f'<div class="answer-card">{answer_text}</div>',
            unsafe_allow_html=True,
        )

        # ── Citations ────────────────────────────────────────────────────────
        citations = result.get("citations", [])
        if citations:
            st.markdown("#### 📚 Sources")
            for c in citations:
                st.markdown(f'<span class="citation">• {c}</span>', unsafe_allow_html=True)

        # ── Metrics ──────────────────────────────────────────────────────────
        st.markdown("#### 📈 Pipeline Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⏱ Time",        f"{elapsed:.2f}s")
        m2.metric("🤖 Agents Used", len(agents))
        m3.metric("📄 Citations",   len(citations))
        m4.metric("✅ Status",      status)

    # ── Pipeline trace ───────────────────────────────────────────────────────
    with st.expander("🔍 Pipeline Trace", expanded=False):
        trace_stages = [
            ("🔄", "Query Reformation",   result.get("reformed_query", "—")),
            ("🛡️", "Input Guardrail",     "PASS" if status != "BLOCKED" else "BLOCKED"),
            ("🧠", "Orchestrator",         result.get("intent", "—")),
            ("✅", "Pre-Tool Guardrail",  "PASS" if status != "BLOCKED" else "BLOCKED"),
            ("⚡", "Agent Execution",     ", ".join(result.get("agents_used", [])) or "—"),
            ("🔗", "Response Aggregation", "Completed"),
            ("📊", "Answer Evaluation",    "Completed"),
            ("🔒", "Output Guardrail",     "PASS" if status != "REDACTED" else "REDACTED"),
            ("🎙️", "Tone of Voice",        "Aligned"),
            ("📤", "Final Response",       f"{elapsed:.2f}s total"),
        ]

        for icon, label, detail in trace_stages:
            blocked = (label in ("Input Guardrail", "Pre-Tool Guardrail") and status == "BLOCKED") \
                   or (label == "Output Guardrail" and status == "REDACTED")
            css_class = "step-block" if blocked else "step-done"
            st.markdown(
                f'<div class="step-row {css_class}">'
                f'<span class="step-icon">{icon}</span>'
                f'<span class="step-label"><b>{label}</b></span>'
                f'<span class="step-detail">{detail}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ─── Query History ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state["history"] = []

if ask_btn and query_input.strip() and "result" in st.session_state:
    entry = {
        "query":   query_input.strip(),
        "status":  st.session_state["result"].get("status", "?"),
        "intent":  st.session_state["result"].get("intent", "?"),
        "elapsed": round(st.session_state.get("elapsed", 0.0), 2),
    }
    if not st.session_state["history"] or st.session_state["history"][-1]["query"] != entry["query"]:
        st.session_state["history"].append(entry)

if st.session_state.get("history"):
    with st.expander(f"📋 Query History ({len(st.session_state['history'])} queries)", expanded=False):
        for i, h in enumerate(reversed(st.session_state["history"][-10:]), 1):
            icon = "✅" if h["status"] == "SUCCESS" else "🚫"
            st.markdown(
                f"**{i}.** {icon} `{h['query']}` — "
                f"*{h['intent']}* — {h['elapsed']}s"
            )
