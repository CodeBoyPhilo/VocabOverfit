import streamlit as st
from streamlit import session_state as session

homepage = st.Page("homepage.py", title="HomePage", icon="🏠")
vocab2math = st.Page("vocab2math.py", title="Vocab2Math", icon="📔")
vocabeval = st.Page("vocabeval.py", title="VocabEval", icon="📝")
vocabrevise = st.Page("vocabrevise.py", title="VocabRevise", icon="📑")

pg = st.navigation([homepage, vocab2math, vocabeval, vocabrevise])

st.set_page_config(page_title="VocabOverfit", page_icon="random")

session.vocab_list = st.sidebar.selectbox(
    "**Select a vocabulary list**",
    [f"list{i}" for i in range(1, 33)],
    label_visibility="visible",
)

pg.run()
