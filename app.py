import streamlit as st
from rag import answer

st.set_page_config(page_title="CampusDocs", page_icon="📚")
st.title("📚 CampusDocs")
st.caption("Ask questions about your study materials")

if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if q := st.chat_input("Ask a question..."):
    st.session_state.history.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            text, chunks = answer(q)
        st.markdown(text)
        if chunks:
            with st.expander("📄 Sources"):
                for c in chunks:
                    st.markdown(f"**{c['source']}** — p. {c['page']}  ·  _distance {c['distance']:.3f}_")

    st.session_state.history.append({"role": "assistant", "content": text})