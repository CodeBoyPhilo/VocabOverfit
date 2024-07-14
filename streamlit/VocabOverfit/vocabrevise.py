import json
import os
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import DataFrame

import streamlit as st
from streamlit import session_state as session


def show_revise_exit_message():
    st.balloons()
    st.markdown("### You have finished this list! Congrats!")
    st.markdown("#### Select `test` on the sidebar to evaluate your revision!")


def show_test_exit_message():
    if session.vr_correct_rate_tracker[-1] == 100:
        st.balloons()
        st.header(":trophy: Fantastic! Keep coming back to test yourself!")

    elif session.vr_correct_rate_tracker[-1] >= 80:
        st.header("	:mortar_board: Practice makes Perfect!")
    else:
        st.header(":sweat_smile: Ehh! You should seriously revise the list again!")
    st.markdown("#### Select `revise` on the sidebar to start your revision!")
    show_metric()


def show_vocab(current_vocab: DataFrame):
    vocabulary = current_vocab["vocabulary"]

    st.markdown(f"## {vocabulary}")


def show_equation(current_vocab: DataFrame):
    equation_1 = current_vocab["equation_1"].split("=")[-1]
    equation_2 = current_vocab["equation_2"].split("=")[-1]

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


def _parse_option(opt):
    return opt.split("=")[1]


def make_question():
    eq_idx = random.randint(1, 2)

    session.vr_correct_opt = _parse_option(
        session.vr_current_vocab[f"equation_{eq_idx}"]
    )
    session.vr_opt_1 = _parse_option(
        session.vr_other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.vr_opt_2 = _parse_option(
        session.vr_other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.vr_opt_3 = _parse_option(
        session.vr_other_data.sample(1)[f"equation_{eq_idx}"].values[0]
    )
    session.vr_options = [
        session.vr_correct_opt,
        session.vr_opt_1,
        session.vr_opt_2,
        session.vr_opt_3,
    ]
    random.shuffle(session.vr_options)


def show_question():

    st.write(f"**Question {session.vr_cur_v_idx +1 } / {session.vr_n_vocab}**")
    left, right = st.columns(2)
    with left:
        st.markdown(f"## {session.vr_current_vocab['vocabulary']}")
        session.vr_selected = st.radio(
            "dummy label", session.vr_options, label_visibility="hidden", index=None
        )
    with right:
        show_metric()

    if st.button("Submit", type="primary", use_container_width=True):
        session.vr_n_finished += 1

        if session.vr_selected == session.vr_correct_opt:
            st.write(":green[**Fantastic!**]")
            session.vr_n_correct += 1

            session.vr_cur_history[session.vr_current_vocab["vocabulary"]] -= 1

            if session.vr_cur_history[session.vr_current_vocab["vocabulary"]] == 0:
                session.vr_cur_history.pop(session.vr_current_vocab["vocabulary"])
        else:
            text = f"""
            :red[**Wrong** - {session.vr_selected}]\n
            :green[**Correct** - {session.vr_correct_opt}]
            """
            st.write(text)

        session.vr_correct_rate_tracker.append(
            np.round((session.vr_n_correct / session.vr_n_finished) * 100, 2)
        )


def show_metric():

    if session.vr_correct_rate_tracker[-1] == 0:
        value = f"N/A"
        return st.metric("Accuracy", value=value, delta=value)
    else:
        value = session.vr_correct_rate_tracker[-1]
        delta = np.round(
            (session.vr_correct_rate_tracker[-1] - session.vr_correct_rate_tracker[-2]),
            2,
        )
        return st.metric("Accuracy", value=f"{value}%", delta=f"{delta}%")


def load_cur_history():
    with open(os.path.join(HISTORY_DIR, f"{session.vocab_list}.json"), "r") as fin:
        session.vr_cur_history = json.load(fin)


def save_cur_history():
    try:
        with open(os.path.join(HISTORY_DIR, f"{session.vocab_list}.json"), "w") as fout:
            json.dump(session.vr_cur_history, fout)
    except Exception as e:
        st.error(e)


# ==============================
# CONSTANT VARIABLES
# ==============================
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "gre_3000.csv"
HISTORY_DIR = os.path.expanduser("~/.streamlit/history")
ERROR_MSG = """
You have not studied **anything**!

you must select a list to study and evaluate first, before you can revise anything!
"""

if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

try:
    assert len(os.listdir(HISTORY_DIR)) != 0

    # ==============================
    # INITIATE SESSION STATE
    # ==============================
    if "vr_cur_v_idx" not in session:
        session.vr_cur_v_idx = 0
    if "vr_prev_q_idx" not in session:
        session.vr_prev_q_idx = -1
    if "vr_prev_vocab_list" not in session:
        session.vr_prev_vocab_list = "list1"
    if "vr_revise_data" not in session:
        session.vr_revise_data = None
    if "vr_current_vocab" not in session:
        session.vr_current_vocab = None
    # if "vocab_list" not in session:
    #     session.vocab_list = None
    if "vr_prev_mode" not in session:
        session.vr_prev_mode = "NA"
    if "vr_cur_history" not in session:
        session.vr_cur_history = None
    # ==============================
    # MAIN APP EXECUTION STARTS HERE
    # ==============================

    # -------Sidebar Element-------
    session.vr_mode = st.sidebar.radio("**Mode**", ["revise", "test"])

    data = pd.read_csv(DATA_DIR)
    data = data[data["list"].isnull() == False]
    if "vr_data" not in session:
        session.vr_data = data.sample(frac=1).reset_index(
            drop=True
        )  # shuffle the vocabularies by default

    if session.vr_cur_history is None:
        load_cur_history()

    session.vr_revise_data = session.vr_data[
        session.vr_data["vocabulary"].isin(session.vr_cur_history.keys())
    ].reset_index(drop=True)

    session.vr_n_vocab = session.vr_revise_data.shape[0]
    session.vr_other_data = session.vr_data[
        session.vr_data["list"] != session.vocab_list
    ]

    if session.vocab_list != session.vr_prev_vocab_list:
        load_cur_history()
        session.vr_prev_vocab_list = session.vocab_list
        session.vr_cur_v_idx = 0

    if session.vr_n_vocab != 0:
        left, right = st.columns(2)
        if left.button(
            "Previous", key="Previous", type="secondary", use_container_width=True
        ):
            session.vr_cur_v_idx -= 1
            if session.vr_cur_v_idx < 0:
                session.vr_cur_v_idx = 0

        if right.button("Next", key="Next", type="secondary", use_container_width=True):
            # to ensure that the user can hit Previous once to return to the last vocabulary
            if session.vr_cur_v_idx + 1 > session.vr_n_vocab:
                session.vr_cur_v_idx = session.vr_n_vocab - 1
            session.vr_cur_v_idx += 1

        if session.vr_mode == "revise":
            if session.vr_mode != session.vr_prev_mode:
                session.vr_cur_v_idx = 0
                session.vr_prev_mode = session.vr_mode
            if session.vr_cur_v_idx + 1 > session.vr_n_vocab:
                show_revise_exit_message()

            else:
                session.vr_current_vocab = session.vr_revise_data.iloc[
                    session.vr_cur_v_idx, :
                ]
                with left:
                    show_vocab(session.vr_current_vocab)
                    show_definition(session.vr_current_vocab)
                with right:
                    st.markdown("## ")  # placeholder for visual enhancements
                    show_equation(session.vr_current_vocab)

                st.markdown(
                    f"#### Progress: {session.vr_cur_v_idx+1} / {session.vr_n_vocab}"
                )
        else:
            if session.vr_mode != session.vr_prev_mode:
                session.vr_cur_v_idx = 0
                session.vr_n_correct = 0
                session.vr_n_finished = 0
                session.vr_correct_rate_tracker = [0]
                session.vr_prev_mode = session.vr_mode
            if session.vr_cur_v_idx + 1 > session.vr_n_vocab:
                show_test_exit_message()
                save_cur_history()
            else:
                session.vr_current_vocab = session.vr_revise_data.iloc[
                    session.vr_cur_v_idx, :
                ]
                if session.vr_prev_q_idx != session.vr_cur_v_idx:
                    session.vr_prev_q_idx = session.vr_cur_v_idx
                    make_question()
                show_question()

    else:
        st.balloons()
        st.header(f"Real genius? No more to revise for {session.vocab_list}!")
        save_cur_history()


except Exception as e:
    st.markdown("# Error 404")
    st.markdown("## Huh…You really don't study at all?")

    st.error(ERROR_MSG)

    session.vr_cur_history = None
