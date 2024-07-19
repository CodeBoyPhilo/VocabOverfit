import json
import os
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
    vocab = session.ve_current_vocab["vocabulary"]
    eq_idx = random.randint(1, 2)

    session.ve_correct_opt = _parse_option(
        session.ve_current_vocab[f"equation_{eq_idx}"]
    )
    session.ve_opt_1 = _parse_option(
        session.ve_other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.ve_opt_2 = _parse_option(
        session.ve_other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.ve_opt_3 = _parse_option(
        session.ve_other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.ve_options = [
        session.ve_correct_opt,
        session.ve_opt_1,
        session.ve_opt_2,
        session.ve_opt_3,
    ]
    random.shuffle(session.ve_options)


def show_question():

    st.write(f"**Question {session.ve_cur_v_idx +1 } / {session.ve_n_vocab}**")
    left, right = st.columns(2)
    with left:
        st.markdown(f"## {session.ve_current_vocab['vocabulary']}")
        session.ve_selected = st.radio(
            "dummy label", session.ve_options, label_visibility="hidden", index=None
        )
    with right:
        show_metric()

    if st.button("Submit", type="primary", use_container_width=True):
        session.ve_n_finished += 1

        if session.ve_selected == session.ve_correct_opt:
            st.write(":green[**Fantastic!**]")
            session.ve_n_correct += 1
        else:
            text = f"""
            :red[**Wrong** - {session.ve_selected}]\n
            :green[**Correct** - {session.ve_correct_opt}]
            """
            st.write(text)
            session.ve_cur_history[session.ve_current_vocab["vocabulary"]] = 3

        session.ve_correct_rate_tracker.append(
            np.round((session.ve_n_correct / session.ve_n_finished) * 100, 2)
        )


def show_metric():

    if session.ve_correct_rate_tracker[-1] == 0:
        value = f"N/A"
        return st.metric("Accuracy", value=value, delta=value)
    else:
        value = session.ve_correct_rate_tracker[-1]
        delta = np.round(
            (session.ve_correct_rate_tracker[-1] - session.ve_correct_rate_tracker[-2]),
            2,
        )
        return st.metric("Accuracy", value=f"{value}%", delta=f"{delta}%")


def load_cur_history():
    try:
        with open(os.path.join(HISTORY_DIR, f"{session.vocab_list}.json"), "r") as fin:
            session.ve_cur_history = json.load(fin)
    except Exception as e:
        session.ve_cur_history = dict()


def save_cur_history():
    try:
        with open(os.path.join(HISTORY_DIR, f"{session.vocab_list}.json"), "w") as fout:
            json.dump(session.ve_cur_history, fout)
    except Exception as e:
        st.error(e)


def show_exit_message():

    if session.ve_correct_rate_tracker[-1] >= 80:
        st.balloons()
        st.header(":trophy: Fantastic! You are ready to be deployed!")

    elif session.ve_correct_rate_tracker[-1] >= 50:
        st.header("	:mortar_board: Maybe study the list again?")
    else:
        st.header(":sweat_smile: Ehh! You should seriously study the list again!")
    show_metric()
    save_cur_history()


# ==============================
# CONSTANT VARIABLES
# ==============================
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "gre_3000.csv"

HISTORY_DIR = os.path.expanduser("~/.streamlit/history")
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# ==============================
# DEFINE session.ve_STATES
# ==============================
# if "vocab_list" not in session:
#     session.vocab_list = None
if "ve_list_data" not in session:
    session.ve_list_data = None
if "ve_cur_v_idx" not in session:
    session.ve_cur_v_idx = 0
if "ve_prev_q_idx" not in session:
    session.ve_prev_q_idx = -1
if "ve_prev_vocab_list" not in session:
    session.ve_prev_vocab_list = "list1"
if "ve_start" not in session:
    session.ve_start = False
if "ve_cur_history" not in session:
    load_cur_history()
if "ve_first_q" not in session:
    session.ve_first_q = True
# ==============================
# MAIN APP EXECUTION STARTS HERE
# ==============================
# session.vocab_list = st.sidebar.selectbox(
#     "**Select a vocabulary list**",
#     [f"list{i}" for i in range(1, 33)],
#     label_visibility="visible",
# )

data = pd.read_csv(DATA_DIR)
data = data[data["list"].isnull() == False]
if "ve_data" not in session:
    session.ve_data = data.sample(frac=1).reset_index(
        drop=True
    )  # shuffle the vocabularies by default

if session.vocab_list is not None:
    session.ve_list_data = session.ve_data[
        session.ve_data["list"] == session.vocab_list
    ]
    session.ve_other_data = session.ve_data[
        session.ve_data["list"] != session.vocab_list
    ]
    session.ve_n_vocab = session.ve_list_data.shape[0]

    if session.vocab_list != session.ve_prev_vocab_list:
        load_cur_history()
        session.ve_start = False
        session.ve_prev_vocab_list = session.vocab_list
        session.ve_cur_v_idx = 0
        session.ve_first_q = True

if st.sidebar.button("**Start**", type="primary", use_container_width=True):
    session.ve_start = True

    session.ve_n_correct = 0
    session.ve_n_finished = 0
    session.ve_correct_rate_tracker = [0]
    session.ve_cur_v_idx = 0

if session.ve_start:

    left, right = st.columns(2)

    if left.button(
        "Previous", key="Previous", type="secondary", use_container_width=True
    ):
        session.ve_cur_v_idx -= 1
        if session.ve_cur_v_idx < 0:
            session.ve_cur_v_idx = 0

    if right.button("Next", key="Next", type="secondary", use_container_width=True):
        # to ensure that the user can hit Previous once to return to the last vocabulary
        if session.ve_cur_v_idx + 1 > session.ve_n_vocab:
            session.ve_cur_v_idx = session.ve_n_vocab - 1
        session.ve_cur_v_idx += 1

    # Start revising
    if session.ve_cur_v_idx + 1 > session.ve_n_vocab:
        show_exit_message()
    else:
        session.ve_current_vocab = session.ve_list_data.iloc[session.ve_cur_v_idx, :]
        if session.ve_first_q:
            make_question()
            session.ve_first_q = False
        if session.ve_prev_q_idx != session.ve_cur_v_idx:
            session.ve_prev_q_idx = session.ve_cur_v_idx
            make_question()
        show_question()

else:
    pass
