import random
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import DataFrame

import streamlit as st
from streamlit import session_state as session


def _parse_option(opt):
    return opt.split("=")[1]


def make_question():
    vocab = session.current_vocab["vocabulary"]
    eq_idx = random.randint(1, 2)

    session.correct_opt = _parse_option(session.current_vocab[f"equation_{eq_idx}"])
    session.opt_1 = _parse_option(
        session.other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.opt_2 = _parse_option(
        session.other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.opt_3 = _parse_option(
        session.other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.options = [session.correct_opt, session.opt_1, session.opt_2, session.opt_3]
    random.shuffle(session.options)


def show_question():

    st.write(f"**Question {session.cur_v_idx +1 } / {session.n_vocab}**")
    left, right = st.columns(2)
    with left:
        st.markdown(f"## {session.current_vocab['vocabulary']}")
        session.selected = st.radio(
            "dummy label", session.options, label_visibility="hidden", index=None
        )
    with right:
        show_metric()

    if st.button("Submit", type="primary", use_container_width=True):
        session.n_finished += 1

        if session.selected == session.correct_opt:
            st.write(":green[**Fantastic!**]")
            session.n_correct += 1
        else:
            text = f"""
            :red[**Wrong** - {session.selected}]\n
            :green[**Correct** - {session.correct_opt}]
            """
            st.write(text)

        session.correct_rate_tracker.append(
            np.round((session.n_correct / session.n_finished) * 100, 2)
        )


def show_metric():

    if session.correct_rate_tracker[-1] == 0:
        value = f"N/A"
        return st.metric("Accuracy", value=value, delta=value)
    else:
        value = session.correct_rate_tracker[-1]
        delta = np.round(
            (session.correct_rate_tracker[-1] - session.correct_rate_tracker[-2]),
            2,
        )
        return st.metric("Accuracy", value=f"{value}%", delta=f"{delta}%")


def show_exit_message():
    st.balloons()

    if session.correct_rate_tracker[-1] >= 80:
        st.header(":trophy: Fantastic! You are ready to be deployed!")

    elif session.correct_rate_tracker[-1] >= 50:
        st.header("	:mortar_board: Maybe study the list again?")
    else:
        st.header(":sweat_smile: Ehh! You should seriously study the list again!")
    show_metric()


# ==============================
# CONSTANT VARIABLES
# ==============================
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "gre_3000.csv"

# ==============================
# DEFINE SESSION STATES
# ==============================
if "vocab_list" not in session:
    session.vocab_list = None
if "list_data" not in session:
    session.list_data = None
if "cur_v_idx" not in session:
    session.cur_v_idx = 0
if "prev_q_idx" not in session:
    session.prev_q_idx = -1
if "prev_vocab_list" not in session:
    session.prev_vocab_list = "list1"
if "start" not in session:
    session.start = False
# ==============================
# MAIN APP EXECUTION STARTS HERE
# ==============================
session.vocab_list = st.sidebar.selectbox(
    "**Select a vocabulary list**",
    [f"list{i}" for i in range(1, 33)],
    label_visibility="visible",
)

data = pd.read_csv(DATA_DIR)
data = data[data["list"].isnull() == False]
if "data" not in session:
    session.data = data
    session.data = session.data.sample(frac=1).reset_index(
        drop=True
    )  # shuffle the vocabularies by default

if session.vocab_list is not None:
    session.list_data = session.data[session.data["list"] == session.vocab_list]
    session.other_data = session.data[session.data["list"] != session.vocab_list]
    session.n_vocab = session.list_data.shape[0]

    if session.vocab_list != session.prev_vocab_list:
        session.start = False
        session.prev_vocab_list = session.vocab_list
        session.cur_v_idx = 0

if st.sidebar.button(
    "**Start**",
    type="primary",
):
    session.start = True

    session.n_correct = 0
    session.n_finished = 0
    session.correct_rate_tracker = [0]

if session.start:

    left, right = st.columns(2)

    if left.button(
        "Previous", key="Previous", type="secondary", use_container_width=True
    ):
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
        session.current_vocab = session.list_data.iloc[session.cur_v_idx, :]
        if session.prev_q_idx != session.cur_v_idx:
            session.prev_q_idx = session.cur_v_idx
            make_question()
        show_question()

else:
    pass
