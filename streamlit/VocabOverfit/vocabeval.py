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


def show_definition(current_vocab: DataFrame):
    ch_meaning = current_vocab["ch_meaning"].split("；")  # Chinese semicolon
    en_meaning_full = current_vocab["en_meaning"]
    if "1" not in en_meaning_full:
        if en_meaning_full[-1] == ".":
            en_meaning_full = en_meaning_full[:-1]
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
    if "=" in opt:
        parsed = opt.split("=")[1]
        if parsed[-1] == "\\":
            parsed = parsed[:-1]
        return parsed
    else:
        return opt


def make_question():
    match session.ve_choice_type:
        case "Chinese":
            choice = "ch_meaning"
        case "equations":
            eq_idx = random.randint(1, 2)
            choice = f"equation_{eq_idx}"
        case "random":
            choice_type = random.randint(0, 1)
            if choice_type == 0:
                choice = "ch_meaning"
            else:
                eq_idx = random.randint(1, 2)
                choice = f"equation_{eq_idx}"

    session.ve_correct_opt = _parse_option(session.ve_current_vocab[choice])
    session.ve_opt_1 = _parse_option(session.ve_other_data.sample(1)[choice].values[0])
    session.ve_opt_2 = _parse_option(session.ve_other_data.sample(1)[choice].values[0])
    session.ve_opt_3 = _parse_option(session.ve_other_data.sample(1)[choice].values[0])
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

        if session.ve_answer_mode == "selection":
            session.ve_selected = st.radio(
                "dummy label", session.ve_options, label_visibility="hidden", index=None
            )
        else:
            for key, opt in zip(["a", "s", "d", "f"], session.ve_options):
                st.write(f"`{key}`: {opt}")
    with right:
        show_metric()


def check_answer():

    session.ve_answered_cur_q = False

    if session.ve_answer_mode == "selection":

        if st.button("Submit", type="primary", use_container_width=True):
            session.ve_n_finished += 1
            session.ve_answered_cur_q = True

    else:
        mapper = {"a": 0, "s": 1, "d": 2, "f": 3, "v": None}

        try:
            session.ve_selected = session.ve_options[mapper[session.ve_cmd]]
            session.ve_n_finished += 1
            session.ve_answered_cur_q = True
        except KeyError:
            pass
        except TypeError:
            session.ve_selected = None
            session.ve_n_finished += 1
            session.ve_answered_cur_q = True

    if session.ve_answered_cur_q:

        if session.ve_selected == session.ve_correct_opt:
            st.write(":green[**Fantastic!**]")
            session.ve_n_correct += 1
        else:
            text = f"""
            :red[**Wrong** - {session.ve_selected}]\n
            :green[**Correct** - {session.ve_correct_opt}]
            """

            left, right = st.columns(2)
            with left:
                st.write(text)
            with right:
                show_definition(session.ve_current_vocab)

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


def submit_key_in_answer():
    session.ve_cmd = session.ve_key_in_answer
    session.ve_key_in_answer = ""


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
if "ve_key_in_answer" not in session:
    session.ve_key_in_answer = ""
if "ve_cmd" not in session:
    session.ve_cmd = ""
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
        session.ve_cmd = ""

with st.sidebar:
    side_left, side_right = st.columns(2)

    with side_left:
        session.ve_answer_mode = st.radio("Answer Mode:", ["selection", "key-in"])
    with side_right:
        session.ve_choice_type = st.radio(
            "Choices:",
            ["Chinese", "equations", "random"],
            on_change=submit_key_in_answer,
        )

    if st.button("**Start**", type="primary", use_container_width=True):
        session.ve_start = True

        session.ve_n_correct = 0
        session.ve_n_finished = 0
        session.ve_correct_rate_tracker = [0]
        session.ve_cur_v_idx = 0

if session.ve_start:

    if session.ve_answer_mode == "selection":

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

    else:
        st.text_input(
            "Your answer:", "", key="ve_key_in_answer", on_change=submit_key_in_answer
        )
        ve_cmd = session.ve_cmd

        if ve_cmd == ";":
            session.ve_cur_v_idx -= 1
            if session.ve_cur_v_idx < 0:
                session.ve_cur_v_idx = 0
        elif ve_cmd == "'":
            if session.ve_cur_v_idx + 1 > session.ve_n_vocab:
                session.ve_cur_v_idx = session.ve_n_vocab - 1
            session.ve_cur_v_idx += 1

        # try:
        #     session.ve_cmd = list(session.ve_cmd)[-1]
        # except Exception as e:
        #     pass

        # if session.ve_cmd == ";":
        #     session.ve_cur_v_idx -= 1
        #     if session.ve_cur_v_idx < 0:
        #         session.ve_cur_v_idx = 0
        # elif session.ve_cmd == "'":
        #     if session.ve_cur_v_idx + 1 > session.ve_n_vocab:
        #         session.ve_cur_v_idx = session.ve_n_vocab - 1
        #     session.ve_cur_v_idx += 1

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

        check_answer()

else:
    pass
