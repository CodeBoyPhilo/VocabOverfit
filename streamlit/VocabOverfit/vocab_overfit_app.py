import streamlit as st

home = st.Page("home.py", title="Home", icon=":material/add_circle:")

vocab2math = st.Page("vocab2math.py", title="Vocab2Math", icon=":material/add_circle:")

vocab_revise = st.Page("vocabrevise.py", title="VocabRevise", icon=":material/delete:")

pg = st.navigation([home, vocab2math, vocab_revise])
st.set_page_config(page_title="VocabOverfit", page_icon=":material/edit:")
pg.run()
