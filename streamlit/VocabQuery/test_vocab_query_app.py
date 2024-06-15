from pandas import DataFrame

import streamlit as st


def start_revise(current_vocab: DataFrame):

    vocabulary = current_vocab["vocabulary"]
    ch_meaning = current_vocab["ch_meaning"].split("；")  # Chinese semicolon
    en_meaning = current_vocab["en_meaning"].split("; ")  # English semicolon
    equation_1 = current_vocab["equation_1"]
    equation_2 = current_vocab["equation_2"]

    st.markdown(f"## {vocabulary}")
    st.markdown("**Definition:**")
    for ch, en in zip(ch_meaning, en_meaning):
        meaning = f"""
                {ch.strip()}\\
                {en.split('.')[-1]}
        """
        st.markdown(meaning)
    # for meaning in ch_meaning:
    #     st.write(f"{meaning}")
    # st.markdown("**英文释义:**")
    # for meaning in en_meaning:
    #     st.write(f"{meaning}")
    st.markdown(f"##### {equation_1}")
    st.markdown(f"##### {equation_2}")


# ==============================
# DEFINE SESSION STATES
# ==============================
if "cur_q_idx" not in st.session_state:
    st.session_state.cur_q_idx = 0
if "init_sample" not in st.session_state:
    st.session_state.init_sample = True
if "start" not in st.session_state:
    st.session_state.start = True

# ==============================
# MAIN APP EXECUTION STARTS HERE
# ==============================
conn = st.connection("gre_vocabulary_db", type="sql")
data = conn.query("SELECT * FROM vocabulary.gre_3000 WHERE equation_1 IS NOT NULL")
if "data" not in st.session_state:
    st.session_state.data = data

if st.session_state.init_sample:
    st.session_state.data = st.session_state.data.sample(frac=1).reset_index(drop=True)
    st.session_state.init_sample = False
else:
    pass

if st.session_state.start:
    st.session_state.start = False
    current_vocab = st.session_state.data.iloc[st.session_state.cur_q_idx, :]
    start_revise(current_vocab)

left, right = st.columns(2)
if left.button("Previous", key="Previous", type="primary", use_container_width=True):
    st.session_state.cur_q_idx -= 1
    current_vocab = st.session_state.data.iloc[st.session_state.cur_q_idx, :]
    start_revise(current_vocab)
if right.button("Next", key="Next", type="primary", use_container_width=True):
    st.session_state.cur_q_idx += 1
    current_vocab = st.session_state.data.iloc[st.session_state.cur_q_idx, :]
    start_revise(current_vocab)
