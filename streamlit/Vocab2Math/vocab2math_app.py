import re
from pathlib import Path

import pandas as pd
from pandas import DataFrame

import streamlit as st
from streamlit import session_state as session


def show_greeting_message():
    html_content = """
    # <a href="#"><img src="https://media.giphy.com/media/hvRJCLFzcasrR4ia7z/giphy.gif" width="25px" height="25px"></a> Welcome to Vocab2Math!
    """
    acknowledgement = """
    ## 	:bulb: Acknowledgement
    The vocabulary details are adapted from [**liurui39660/3000**](https://github.com/liurui39660/3000) and **张巍老师GRE**.
    """

    how_to_use = """
    ## 	:package: How to use?
    1. Select a vocabulary list!
    2. Start learning!
    3. Finished? Select a new list! 
    """

    st.sidebar.markdown(html_content, unsafe_allow_html=True)
    st.sidebar.markdown("")
    st.sidebar.markdown("Author: [CodeBoyPhilo](https://github.com/CodeBoyPhilo)")
    st.sidebar.divider()
    st.sidebar.markdown(acknowledgement)
    st.sidebar.markdown(how_to_use)


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
# CONSTANT VARIABLES
# ==============================
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "gre_3000.csv"

# ==============================
# DEFINE SESSION STATES
# ==============================
if "cur_v_idx" not in session:
    session.cur_v_idx = 0
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

# -------Sidebar Element-------
show_greeting_message()
session.vocab_list = st.selectbox(
    "**Select a vocabulary list**",
    [f"list{i}" for i in range(1, 33)],
    label_visibility="visible",
)

left, right = st.columns(2)
session.always_show_def = st.radio("**Vocabulary Definition**", ["Show", "Hide"])


# Load data
# conn = st.connection("gre_vocabulary_db", type="sql")
# data = conn.query("SELECT * FROM vocabulary.gre_3000 WHERE equation_1 IS NOT NULL")

data = pd.read_csv(DATA_DIR)
if "data" not in session:
    session.data = data
if st.sidebar.button("Shuffle the order", type="primary"):
    session.data = session.data.sample(frac=1).reset_index(drop=True)
    session.cur_v_idx = 0

if session.vocab_list is not None:
    session.list_data = session.data[session.data["list"] == session.vocab_list]
    session.n_vocab = session.list_data.shape[0]

    if session.vocab_list != session.prev_vocab_list:
        session.prev_vocab_list = session.vocab_list
        session.cur_v_idx = 0

# Previous and Next button
left, right = st.columns(2)
if left.button("Previous", key="Previous", type="secondary", use_container_width=True):
    session.cur_v_idx -= 1
    if session.cur_v_idx < 0:
        session.cur_v_idx = 0

if right.button("Next", key="Next", type="secondary", use_container_width=True):
    # to ensure that the user can hit Previous once to return to the last vocabulary
    if session.cur_v_idx + 1 > session.n_vocab:
        session.cur_v_idx = session.n_vocab - 1
    session.cur_v_idx += 1

# Start revising
if session.cur_v_idx + 1 > session.n_vocab:
    show_exit_message()
else:
    left, right = st.columns(2)
    session.current_vocab = session.list_data.iloc[session.cur_v_idx, :]
    with left:
        start_revise(session.current_vocab)
    with right:
        if session.always_show_def == "Show":
            st.markdown("##")  # placeholder for visual enhancements
            show_definition(session.current_vocab)
        else:
            st.markdown("")  # placeholder for visual enhancements
            click_show_definition = st.button("show definition", type="secondary")
            if click_show_definition:
                show_definition(session.current_vocab)

    st.markdown(f"#### Progress: {session.cur_v_idx+1} / {session.n_vocab}")
