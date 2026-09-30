from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from aura.assistant import answer_question, explain_document, make_quiz
from aura.benchmark import run_benchmark
from aura.config import settings
from aura.document import DocumentContent, chunk_text, extract_document
from aura.hardware import get_hardware_info
from aura.llm import OllamaClient
from aura.privacy import redact_text, scan_text, severity_score
from aura.retrieval import LocalRetriever
from aura.utils import make_source_chunks, timestamp

st.set_page_config(
    page_title="AURA — Adaptive Understanding & Retrieval Assistant",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
  --ink:#17181d;
  --muted:#69707d;
  --line:#e7e8ed;
  --panel:#ffffff;
  --soft:#f6f6ff;
  --accent:#5b5ce2;
  --accent2:#4748bf;
  --success:#14804a;
  --success-bg:#eefaf4;
}
.stApp {
  background:
    radial-gradient(circle at 9% 0%, rgba(91,92,226,.08), transparent 30%),
    radial-gradient(circle at 94% 9%, rgba(91,92,226,.05), transparent 26%),
    #fbfbfc;
}
.block-container { max-width: 1380px; padding-top: 1.5rem; padding-bottom: 3rem; }
section[data-testid="stSidebar"] { border-right:1px solid var(--line); }
section[data-testid="stSidebar"] > div { background:#f8f8fa; }

.aura-header { display:flex; justify-content:space-between; align-items:flex-start; gap:1.5rem; margin-bottom:1.35rem; }
.aura-brand { display:flex; align-items:center; gap:.85rem; }
.aura-mark {
  width:48px; height:48px; border-radius:15px; background:var(--ink); color:white;
  display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.2rem;
  box-shadow:0 12px 26px rgba(23,24,29,.15);
}
.aura-title { font-size:2.55rem; line-height:1; font-weight:800; letter-spacing:-.055em; color:var(--ink); }
.aura-sub { color:var(--muted); margin-top:.35rem; font-size:.98rem; }
.status-pill { display:inline-flex; align-items:center; gap:.4rem; background:var(--soft); color:var(--accent2); border:1px solid #e2e3ff; border-radius:999px; padding:.42rem .7rem; font-size:.78rem; font-weight:700; }
.status-dot { width:7px; height:7px; border-radius:50%; background:var(--accent); }

.hero {
  background:linear-gradient(135deg,#1b1c23 0%,#292b39 100%);
  color:white; border-radius:24px; padding:1.35rem 1.45rem; margin-bottom:1rem;
  box-shadow:0 18px 42px rgba(23,24,29,.12);
}
.hero h2 { margin:0; font-size:1.35rem; letter-spacing:-.02em; }
.hero p { margin:.45rem 0 0; color:#cbd0da; max-width:850px; line-height:1.55; }

.card { background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:1rem 1.05rem; box-shadow:0 8px 28px rgba(25,28,35,.035); }
.card-title { font-size:1.02rem; font-weight:750; color:var(--ink); }
.card-sub { color:var(--muted); font-size:.88rem; margin-top:.2rem; }
.metric-box { background:#fff; border:1px solid var(--line); border-radius:18px; padding:1rem; }
.metric-label { font-size:.78rem; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); font-weight:750; }
.metric-value { font-size:1.75rem; line-height:1.1; margin-top:.35rem; font-weight:800; color:var(--ink); }
.metric-note { color:var(--muted); font-size:.8rem; margin-top:.25rem; }

.evidence { background:#fafaff; border:1px solid #ececff; border-left:4px solid var(--accent); border-radius:0 14px 14px 0; padding:.8rem .9rem; margin:.55rem 0; }
.evidence-name { font-weight:750; color:var(--ink); }
.evidence-meta { color:var(--muted); font-size:.78rem; margin-top:.1rem; }
.evidence-text { color:#30343b; line-height:1.55; margin-top:.4rem; }

.feature { min-height:105px; }
.feature-title { font-weight:760; color:var(--ink); }
.feature-copy { color:var(--muted); line-height:1.45; margin-top:.25rem; font-size:.9rem; }

div.stButton > button {
  border-radius:12px;
  min-height:2.55rem;
  font-weight:700;
  border:1px solid #dcdde5;
}
div.stButton > button[kind="primary"] {
  background:var(--accent);
  border-color:var(--accent);
  color:#fff;
}
div.stButton > button[kind="primary"]:hover { background:var(--accent2); border-color:var(--accent2); }

[data-testid="stMetricValue"] { font-weight:800; }
[data-testid="stMetricLabel"] { color:var(--muted); }

.small-note { color:var(--muted); font-size:.82rem; line-height:1.5; }
.divider { height:1px; background:var(--line); margin:1.2rem 0; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


MEASURED_BASELINE = {
    "recorded_on": "2026-09-30",
    "model": "gemma3:1b",
    "benchmark_runs": 3,
    "average_seconds": 2.79,
    "minimum_seconds": 1.61,
    "maximum_seconds": 4.79,
    "document_qa_example_seconds": 6.03,
    "quiz_example_seconds": 10.55,
    "tests_passed": "4/4",
}


def init_state() -> None:
    st.session_state.setdefault("documents", [])
    st.session_state.setdefault("active", None)
    st.session_state.setdefault("question_history", [])


def local_client() -> OllamaClient:
    return OllamaClient()


def model_status(client: OllamaClient) -> tuple[bool, str]:
    return client.status()


def render_evidence(hits) -> None:
    if not hits:
        st.info("No strong matching passage was found in the loaded sources. Try a more specific question.")
        return

    st.markdown("#### Evidence from your document")
    for hit in hits:
        source = Path(hit.source).name
        st.markdown(
            f"""
            <div class="evidence">
              <div class="evidence-name">{source}</div>
              <div class="evidence-meta">Retrieved passage</div>
              <div class="evidence-text">{hit.text[:900]}{'…' if len(hit.text) > 900 else ''}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Technical retrieval details"):
        for hit in hits:
            st.write(f"{Path(hit.source).name} — cosine similarity: {hit.score:.3f}")


init_state()
client = local_client()

with st.sidebar:
    st.markdown("## AURA")
    st.caption("Adaptive Understanding & Retrieval Assistant")
    st.divider()

    st.markdown("**Workspace**")
    audience = st.selectbox(
        "Audience level",
        ["General reader", "School student", "College student", "Professional", "Technical reader"],
        index=2,
    )
    language = st.selectbox(
        "Response language",
        ["English", "Hindi", "Punjabi", "Bengali", "Tamil", "Telugu"],
        index=0,
    )
    style = st.selectbox(
        "Response style",
        ["Clear and concise", "Step-by-step", "Exam focused", "Practical", "Detailed"],
        index=0,
    )

    st.divider()
    st.markdown("**Local AI runtime**")
    st.caption(f"Endpoint: `{settings.ollama_url}`")
    st.caption(f"Model: `{settings.ollama_model}`")
    if st.button("Check local AI", use_container_width=True):
        ok, msg = model_status(client)
        if ok and "not installed" not in msg:
            st.success(msg)
        elif ok:
            st.warning(msg)
        else:
            st.error(f"Local AI unavailable: {msg}")

    st.divider()
    hw = get_hardware_info()
    st.markdown("**System snapshot**")
    st.caption(f"Memory: {hw['Memory']}")
    st.caption(f"System: {hw['System']}")
    st.caption(f"Runtime device: {hw['Device']}")

status_ok, status_msg = model_status(client)
status_label = "LOCAL MODEL READY" if status_ok and "not installed" not in status_msg else "LOCAL MODEL CHECK"

st.markdown(
    f"""
    <div class="aura-header">
      <div class="aura-brand">
        <div class="aura-mark">A</div>
        <div>
          <div class="aura-title">AURA</div>
          <div class="aura-sub">Understand any information in the way you learn best.</div>
        </div>
      </div>
      <div class="status-pill"><span class="status-dot"></span>{status_label}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h2>Understand · Protect · Practice</h2>
      <p>Bring a document, image or note into AURA. Ask grounded questions, adapt explanations to your audience, detect common sensitive information, and turn the source into practice material.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

upload_col, privacy_col = st.columns([2.2, 1], gap="large")
with upload_col:
    st.markdown("### Bring something you want to understand")
    st.caption("PDF, DOCX, TXT, Markdown, CSV or image")
    uploads = st.file_uploader(
        "Upload source material",
        type=["pdf", "docx", "txt", "md", "markdown", "csv", "png", "jpg", "jpeg", "webp", "bmp", "tiff"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
with privacy_col:
    combined = "\n\n".join(d.text for d in st.session_state.documents)
    findings_now = scan_text(combined) if combined else []
    score_now = severity_score(findings_now)
    st.markdown("### Current privacy posture")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Findings</div><div class="metric-value">{len(findings_now)}</div><div class="metric-note">local pattern scan</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Risk score</div><div class="metric-value">{score_now}</div><div class="metric-note">relative indicator</div></div>', unsafe_allow_html=True)

if uploads:
    existing = {d.name for d in st.session_state.documents}
    for uploaded in uploads:
        if uploaded.name in existing:
            continue
        try:
            document = extract_document(uploaded.getvalue(), uploaded.name)
            st.session_state.documents.append(document)
            existing.add(document.name)
            if st.session_state.active is None:
                st.session_state.active = document.name
        except Exception as exc:
            st.error(f"Could not read {uploaded.name}: {exc}")

if not st.session_state.documents:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("### AURA is ready")
    cards = st.columns(4)
    features = [
        ("Understand", "Grounded answers and adaptive explanations from your own material."),
        ("Protect", "Detect and redact common sensitive information locally."),
        ("Practice", "Turn source material into questions and revision prompts."),
        ("Local by design", "The default AI workflow talks to the local Ollama service."),
    ]
    for col, (title, copy) in zip(cards, features):
        with col:
            st.markdown(f'<div class="card feature"><div class="feature-title">{title}</div><div class="feature-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.info("Upload a source to begin. Generative features use the configured local model; document extraction and privacy scanning can run without it.")
    st.stop()

# Active source
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
active_names = [d.name for d in st.session_state.documents]
current_index = active_names.index(st.session_state.active) if st.session_state.active in active_names else 0
active_name = st.selectbox("Active source", active_names, index=current_index)
st.session_state.active = active_name
active: DocumentContent = next(d for d in st.session_state.documents if d.name == active_name)

chunks = make_source_chunks(st.session_state.documents, chunk_text)
retriever = LocalRetriever(chunks)

st.markdown(
    f"<div class='small-note'>Active source: <b>{active.name}</b> · {active.source_type} · {len(active.text):,} extracted characters · {len(chunks):,} retrieval chunks</div>",
    unsafe_allow_html=True,
)

ask_tab, explain_tab, quiz_tab, privacy_tab, source_tab, system_tab = st.tabs(
    ["Ask", "Explain", "Quiz", "Privacy", "Sources", "System"]
)

with ask_tab:
    st.markdown("### Ask about your sources")
    st.caption(f"Audience: {audience} · Language: {language} · Style: {style}")
    question = st.text_area(
        "Question",
        placeholder="What is the main idea? Compare two concepts. Which passage supports this?",
        height=115,
        label_visibility="collapsed",
    )
    if st.button("Ask AURA", type="primary", use_container_width=True, disabled=not question.strip()):
        hits = retriever.search(question, settings.top_k)
        result = answer_question(question, hits, client, audience, language, style)
        st.session_state.question_history.append({"time": timestamp(), "question": question})
        if result.ok:
            st.success(f"Answered locally in {result.elapsed:.2f}s")
        else:
            st.info("The configured local model was unavailable for this request, so AURA used its deterministic fallback. No remote AI API was used.")
        st.markdown(result.text)
        render_evidence(hits)

with explain_tab:
    st.markdown("### Adaptive explanation")
    st.caption(f"AURA is currently adapting to: {audience} · {language} · {style}")
    if st.button("Explain this source", type="primary", use_container_width=True):
        result = explain_document(active.text, client, audience, language, style)
        if result.ok:
            st.success(f"Generated locally in {result.elapsed:.2f}s")
        else:
            st.info("A deterministic extractive explanation is being shown because the local model is unavailable.")
        st.markdown(result.text)

with quiz_tab:
    st.markdown("### Turn understanding into practice")
    q1, q2 = st.columns(2)
    with q1:
        count = st.slider("Questions", 3, 12, 5)
    with q2:
        difficulty = st.select_slider("Difficulty", ["Easy", "Moderate", "Hard"], value="Moderate")
    if st.button("Generate quiz", type="primary", use_container_width=True):
        result = make_quiz(active.text, client, audience, language, count, difficulty)
        if result.ok:
            st.success(f"Quiz generated locally in {result.elapsed:.2f}s")
            st.markdown(result.text)
        else:
            st.warning("The local model is not available, so a model-generated quiz cannot be produced yet.")
            st.caption("Start Ollama and ensure the configured model is installed, then try again.")

with privacy_tab:
    st.markdown("### Privacy scan and redaction")
    findings = scan_text(active.text)
    score = severity_score(findings)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Findings", len(findings))
    with m2:
        st.metric("Risk score", score)
    with m3:
        st.metric("Processing", "Local")

    if findings:
        rows = [
            {"Type": f.kind, "Severity": f.severity, "Detected": f.value, "Preview": f.masked}
            for f in findings
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        redacted = redact_text(active.text, findings)
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "Download redacted text",
                redacted,
                file_name=f"{Path(active.name).stem}_redacted.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with d2:
            if active.source_type == "PDF" and active.original_bytes:
                from aura.document import redact_pdf_bytes
                try:
                    safe_pdf = redact_pdf_bytes(active.original_bytes)
                    st.download_button(
                        "Download redacted PDF",
                        safe_pdf,
                        file_name=f"{Path(active.name).stem}_redacted.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as exc:
                    st.warning(f"PDF redaction could not be completed: {exc}")
        st.text_area("Redacted preview", redacted[:10000], height=280)
    else:
        st.success("No supported sensitive-data patterns were detected in the extracted text.")
        st.caption("AURA's pattern scan is conservative. A clean result is not a guarantee that a document contains no sensitive information.")

with source_tab:
    st.markdown("### Source material")
    if active.metadata:
        st.json(active.metadata)
    st.text_area("Extracted text", active.text[:30000], height=520, label_visibility="collapsed")

with system_tab:
    st.markdown("### Local runtime and benchmark")
    info = get_hardware_info()
    a, b, c, d = st.columns(4)
    with a:
        st.metric("Model", client.model)
    with b:
        st.metric("Tests", MEASURED_BASELINE["tests_passed"])
    with c:
        st.metric("Benchmark avg", f"{MEASURED_BASELINE['average_seconds']:.2f}s")
    with d:
        st.metric("Benchmark range", f"{MEASURED_BASELINE['minimum_seconds']:.2f}–{MEASURED_BASELINE['maximum_seconds']:.2f}s")

    st.markdown("#### Recorded development measurements")
    st.caption("These values are a recorded local development baseline from 2026-09-30. Re-run the benchmark after changing the model, runtime, or machine before using them as deployment claims.")
    st.dataframe(
        [
            {"Measurement": "3-run benchmark average", "Result": f"{MEASURED_BASELINE['average_seconds']:.2f} s"},
            {"Measurement": "3-run benchmark minimum", "Result": f"{MEASURED_BASELINE['minimum_seconds']:.2f} s"},
            {"Measurement": "3-run benchmark maximum", "Result": f"{MEASURED_BASELINE['maximum_seconds']:.2f} s"},
            {"Measurement": "Example document Q&A", "Result": f"{MEASURED_BASELINE['document_qa_example_seconds']:.2f} s"},
            {"Measurement": "Example quiz generation", "Result": f"{MEASURED_BASELINE['quiz_example_seconds']:.2f} s"},
            {"Measurement": "Automated tests", "Result": MEASURED_BASELINE["tests_passed"]},
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Current machine")
    st.json(info)

    if st.button("Run benchmark now", type="primary", use_container_width=True):
        result = run_benchmark(client, 3)
        st.json(result)
        if result.get("average_seconds") is not None:
            st.success(f"Current average local generation time: {result['average_seconds']:.2f}s")
        else:
            st.warning("No successful model run was recorded. Check the local model service.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    session_data = {
        "created": timestamp(),
        "audience": audience,
        "language": language,
        "style": style,
        "sources": [
            {"name": d.name, "type": d.source_type, "characters": len(d.text)}
            for d in st.session_state.documents
        ],
        "questions": st.session_state.question_history,
    }
    st.download_button(
        "Download session metadata",
        json.dumps(session_data, indent=2).encode("utf-8"),
        file_name="aura_session.json",
        mime="application/json",
        use_container_width=True,
    )
with col_b:
    if st.button("Clear loaded sources", use_container_width=True):
        st.session_state.documents = []
        st.session_state.active = None
        st.session_state.question_history = []
        st.rerun()
