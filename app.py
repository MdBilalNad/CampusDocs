import streamlit as st
from rag import recommend

st.set_page_config(
    page_title="ProjectFinder",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Dark Mode Custom CSS ---
st.markdown("""
<style>
/* Layout */
.block-container {
    max-width: 1100px;
    padding-top: 3rem;
    padding-bottom: 4rem;
}
/* Typography */
h1 { font-weight: 600 !important; letter-spacing: -0.03em !important; font-size: 2rem !important; color: #ffffff !important; }
h2 { font-weight: 500 !important; letter-spacing: -0.02em !important; color: #ffffff !important; }
p, label { font-size: 0.95rem !important; }

/* Result Card Styling */
.result-card {
    border-top: 1px solid #30363d;
    padding-top: 1.5rem;
    margin-bottom: 1.5rem;
}
.result-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.2rem;
}
.result-meta {
    font-size: 0.85rem;
    color: #8b949e;
    margin-bottom: 0.8rem;
}
.result-reason {
    font-size: 0.95rem;
    color: #c9d1d9;
    line-height: 1.5;
    margin-bottom: 1rem;
}
.tag {
    background: #21262d;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    color: #c9d1d9;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
    display: inline-block;
    border: 1px solid #30363d;
}
.score {
    font-size: 0.9rem;
    font-weight: 600;
    color: #ffffff;
    background: #238636; /* GitHub green for match score */
    padding: 0.3rem 0.6rem;
    border-radius: 6px;
    border: 1px solid #2ea043;
}
/* --- Fix Multiselect Chips (Skills) --- */
[data-testid="stSidebar"] span[data-baseweb="tag"] {
    background-color: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] span[data-baseweb="tag"] span {
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] span[data-baseweb="tag"] svg {
    fill: #c9d1d9 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### Profile")
    interests = st.text_area(
        "Interests",
        placeholder="e.g. NLP, chatbots, retrieval systems",
        height=100,
    )
    skills = st.multiselect(
        "Skills",
        ["Python", "JavaScript", "React", "Node.js", "PyTorch", "TensorFlow",
         "OpenCV", "Flask", "FastAPI", "SQL", "MongoDB", "AWS", "Solidity",
         "Go", "Java", "C++", "Android", "Flutter", "Arduino"],
    )

    st.divider()
    st.markdown("### Constraints")
    domain = st.selectbox(
        "Domain",
        ["Any", "NLP", "Computer Vision", "Web Development",
         "Machine Learning", "Blockchain", "IoT", "Security", "Systems"],
    )
    difficulty = st.selectbox(
        "Difficulty",
        ["Any", "easy", "medium", "hard"],
    )
    weeks = st.slider("Weeks available", 4, 16, 8)
    team_size = st.slider("Team size", 1, 4, 2)

    st.divider()
    st.markdown("### Preferences")
    top_k = st.slider("Number of results", 3, 10, 5)
    strict_skill = st.toggle("Strict skill matching", value=False)

    st.divider()
    go = st.button("Find projects", use_container_width=True, type="primary")
    reset = st.button("Reset", use_container_width=True)

if reset:
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# ---------------- Main ----------------
st.title("ProjectFinder")
st.markdown(
    "A retrieval-based recommender for B.Tech CSE final-year projects. "
    "Describe your interests and constraints; results are ranked against a catalog of past projects."
)
st.write("") # spacer

if go:
    profile = {
        "interests": interests,
        "skills": skills,
        "domain": domain,
        "difficulty": difficulty,
        "team_size": team_size,
        "weeks": weeks,
        "max_weeks": weeks + 2,
    }

    with st.spinner("Ranking candidates..."):
        results = recommend(profile, strict_skill=strict_skill, top_k=top_k)

    # Active-filter summary
    parts = []
    if domain != "Any": parts.append(f"domain = {domain}")
    if difficulty != "Any": parts.append(f"difficulty = {difficulty}")
    if skills: parts.append(f"skills = {', '.join(skills)}")
    if strict_skill: parts.append("strict skills")
    parts.append(f"top {top_k}")

    st.divider()
    st.caption(" · ".join(parts))

    if not results:
        st.warning("No matches. Try widening your filters or disabling strict skill matching.")
    else:
        for r in results:
            # Build HTML chunks
            tags_html = "".join(f'<span class="tag">{s}</span>' for s in r["skills"])
            stack_html = "".join(f'<span class="tag">{s}</span>' for s in r["tech_stack"])
            src_html = f'<br><br><a href="{r["source_url"]}" target="_blank" style="color: #58a6ff;">View source ↗</a>' if r.get("source_url") else ""

            # Render the card
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f'<div class="result-title">{r["title"]}</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div style="text-align: right;"><span class="score">{r["score"]}/100</span></div>', unsafe_allow_html=True)
                
                st.markdown(
                    f'<div class="result-meta">{r["domain"]} · {r["difficulty"]} · {r["estimated_weeks"]} weeks · Team of {r["team_size"]}</div>', 
                    unsafe_allow_html=True
                )
                st.markdown(f'<div class="result-reason">{r["reason"]}</div>', unsafe_allow_html=True)
                st.markdown(f'**Skills:** {tags_html}', unsafe_allow_html=True)
                st.markdown(f'**Stack:** {stack_html}', unsafe_allow_html=True)
                if src_html:
                    st.markdown(src_html, unsafe_allow_html=True)
            
            st.markdown('<div class="result-card"></div>', unsafe_allow_html=True)

else:
    st.info("👈 Fill in your profile in the sidebar and click **Find projects** to begin.")