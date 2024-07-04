import re

from pandas import DataFrame

import streamlit as st
from streamlit import session_state as session


def start_revise(current_vocab: DataFrame):

    vocabulary = current_vocab["vocabulary"]
    equation_1 = current_vocab["equation_1"].split("=")[-1]
    equation_2 = current_vocab["equation_2"].split("=")[-1]

    st.markdown(f"## {vocabulary}")
    st.markdown(f"##### = {equation_1}")
    st.markdown(f"##### = {equation_2}")


def show_definition(current_vocab: DataFrame):
    ch_meaning = current_vocab["ch_meaning"].split("；")  # Chinese semicolon
    en_meaning_full = current_vocab["en_meaning"]
    if "1" not in en_meaning_full:
        en_meaning = [en_meaning_full]
    else:
        pattern = r"\d+\.\s*([^;]+)(?:;|\s|$)"
        en_meaning = re.findall(pattern, en_meaning_full)

    # st.markdown("**Definition:**")
    for ch, en in zip(ch_meaning, en_meaning):

        meaning = f"""
                {ch.strip()}\\
                {en.split('.')[-1]}
        """
        st.markdown(meaning)


def show_exit_message():
    st.balloons()
    st.markdown("### You have finished this list! Congrats!")


# ==============================
# DEFINE SESSION STATES
# ==============================
if "cur_q_idx" not in session:
    session.cur_q_idx = 0
if "init_sample" not in session:
    session.init_sample = True
if "start" not in session:
    session.start = True
if "prev_vocab_list" not in session:
    session.prev_vocab_list = "list1"
if "vocab_list" not in session:
    session.vocab_list = None
if "list_data" not in session:
    session.list_data = None
if "current_vocab" not in session:
    session.current_vocab = None
# ==============================
# MAIN APP EXECUTION STARTS HERE
# ==============================
st.sidebar.markdown("# Select Vocabulary list:")
session.vocab_list = st.sidebar.selectbox(
    "dummy label", [f"list{i}" for i in range(1, 33)], label_visibility="hidden"
)
session.always_show_def = st.sidebar.radio(
    "**Vocabulary Definition**", ["Show", "Hide"]
)

conn = st.connection("gre_vocabulary_db", type="sql")
data = conn.query("SELECT * FROM vocabulary.gre_3000 WHERE equation_1 IS NOT NULL")
if "data" not in session:
    session.data = data

if session.vocab_list is not None:
    session.list_data = session.data[session.data["list"] == session.vocab_list]
    session.n_vocab = session.list_data.shape[0]

    if session.vocab_list != session.prev_vocab_list:
        session.prev_vocab_list = session.vocab_list
        session.cur_q_idx = 0

if session.init_sample:
    session.data = session.data.sample(frac=1).reset_index(drop=True)
    session.init_sample = False
else:
    pass

left, right = st.columns(2)
if left.button("Previous", key="Previous", type="primary", use_container_width=True):
    session.cur_q_idx -= 1

if right.button("Next", key="Next", type="primary", use_container_width=True):
    if session.cur_q_idx + 1 > session.n_vocab:
        session.cur_q_idx = session.n_vocab - 1
    session.cur_q_idx += 1

if session.cur_q_idx + 1 > session.n_vocab:
    show_exit_message()
else:
    left, right = st.columns(2)
    session.current_vocab = session.list_data.iloc[session.cur_q_idx, :]
    with left:
        start_revise(session.current_vocab)
    with right:
        st.markdown("##")  # placeholder for visual enhancements
        if session.always_show_def == "Show":
            show_definition(session.current_vocab)
        else:
            click_show_definition = st.button("show definition", type="secondary")
            if click_show_definition:
                show_definition(session.current_vocab)

    st.markdown(f"#### Progress: {session.cur_q_idx+1} / {session.n_vocab}")
