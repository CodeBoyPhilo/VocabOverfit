import json
import os
import random
import time

import numpy as np
import pandas as pd

import streamlit as st


def sample_questions(show: int = 10, difficulty: str = "easy") -> pd.DataFrame:
    filtered = st.session_state.data[st.session_state.data["DIFFICULTY"] == difficulty]
    populationQuestionID = sorted(filtered["QUESTIONID"].unique())
    sampledQuestionID = random.sample(populationQuestionID, show)
    sampledQuestions = filtered[filtered["QUESTIONID"].isin(sampledQuestionID)]
    return sampledQuestions.to_dict("records")


def parse_sampled_question(sampled_question):
    parsed = dict()
    tracker = 0
    current_id = 0  # just that pyright does not through unbounded error
    for ID, question in enumerate(sampled_question):
        if tracker % 9 == 0:
            current_id = ID // 9
            questionID = question["QUESTIONID"]
            sectionID = question["SECTION"]

            if questionID % 10 == 0:
                subQuestionID = 10
            else:
                subQuestionID = questionID % 10

            difficulty = question["DIFFICULTY"]
            questionText = question["QUESTIONTEXT"]
            parsed[current_id + 1] = {
                "QuestionID": questionID,
                "Section": sectionID,
                "SubQuestionID": subQuestionID,
                "Difficulty": difficulty,
                "Question": questionText,
                "Choices": {
                    question["CHOICELABEL"]: [
                        question["CHOICETEXT"],
                        question["ISCORRECT"],
                    ]
                },
            }

            tracker += 1
        else:
            parsed[current_id + 1]["Choices"][question["CHOICELABEL"]] = [
                question["CHOICETEXT"],
                question["ISCORRECT"],
            ]
            tracker += 1
    return parsed


def show_questions(parsed):
    left, middle, right = st.columns([3, 1, 1])
    with left:
        st.markdown(f"### Question {st.session_state.current_qid}")
        st.markdown(f"##### ID: {parsed['Section']} - {parsed['SubQuestionID']}")
        st.markdown(f"##### Level: {parsed['Difficulty']}")
    with right:
        show_metric()

    st.write(parsed["Question"])

    st.session_state.choices = list()
    for label in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
        if parsed["Choices"][label][0] is not None:
            st.session_state.choices.append(
                f"**{label}:  {parsed['Choices'][label][0]}**"
            )

    answer_cols = len(st.session_state.choices) // 3

    (
        st.session_state.set1_choice,
        st.session_state.set2_choice,
        st.session_state.set3_choice,
    ) = st.columns(3)

    if answer_cols == 1:
        st.session_state.choice[0] = st.session_state.set1_choice.radio(
            "", st.session_state.choices, key="Case_1_answer_set1", index=None
        )
        st.session_state.choice[1] = None
        st.session_state.choice[2] = None

    elif answer_cols == 2:
        st.session_state.choice[0] = st.session_state.set1_choice.radio(
            "", st.session_state.choices[:3], key="Case_2_answer_set1", index=None
        )
        st.session_state.choice[1] = st.session_state.set2_choice.radio(
            "", st.session_state.choices[3:6], key="Case_2_answer_set2", index=None
        )
        st.session_state.choice[2] = None

    else:
        st.session_state.choice[0] = st.session_state.set1_choice.radio(
            "", st.session_state.choices[:3], key="Case_3_answer_set1", index=None
        )
        st.session_state.choice[1] = st.session_state.set2_choice.radio(
            "", st.session_state.choices[3:6], key="Case_3_answer_set2", index=None
        )
        st.session_state.choice[2] = st.session_state.set3_choice.radio(
            "", st.session_state.choices[6:], key="Case_3_answer_set3", index=None
        )


def check_answer(parsed):
    if st.session_state.finished_check is False:
        correct_label = list()
        correct_text = list()

        for label, status in parsed["Choices"].items():
            if status[1] == "True":
                correct_label.append(label)
                correct_text.append(status[0])

        sub_label = []
        for submitted in range(3):
            if st.session_state.choice[submitted] is not None:
                sub_label.append(
                    st.session_state.choice[submitted].split(": ")[0].split("**")[1]
                )

        results = [sub == correct for (sub, correct) in zip(sub_label, correct_label)]
        st.session_state.total_blanks += len(correct_label)
        st.session_state.total_correct += sum(results)
        value = np.round(
            (st.session_state.total_correct / st.session_state.total_blanks) * 100, 2
        )
        st.session_state.correct_rate_tracker.append(value)

        for choice_idx, result in enumerate(results):
            choice = st.session_state.choice[choice_idx]
            if result:
                st.session_state.choices[choice_idx] = f":green{choice}"
            else:
                st.session_state.choices[choice_idx] = f":red{choice}"

        if sum(results) == len(correct_label):
            st.write(":green[**Fantastic! You fit this question well!**]")
            st.session_state.n_correct += 1
        else:
            cols = list(st.columns(3))
            for idx, result, submitted, label, text in zip(
                range(3), results, st.session_state.choice, correct_label, correct_text
            ):
                if result is True:
                    with cols[idx]:
                        text = f"""
                        :green[**Correct - {label}: {text}**]
                        """
                        st.write(text)
                    st.session_state.history[parsed["QuestionID"]] = "True"
                else:
                    with cols[idx]:
                        text = f"""
                        :red[**Wrong** - {submitted}]\n
                        :green[**Correct - {label}: {text}**]
                        """
                        st.write(text)
                    st.session_state.history[parsed["QuestionID"]] = "False"
        st.session_state.finished_check = True


def show_metric():

    if st.session_state.correct_rate_tracker[-1] == 0:
        value = f"N/A"
        return st.metric("Accuracy", value=value, delta=value)
    else:
        value = st.session_state.correct_rate_tracker[-1]
        delta = np.round(
            (
                st.session_state.correct_rate_tracker[-1]
                - st.session_state.correct_rate_tracker[-2]
            ),
            2,
        )
        return st.metric("Accuracy", value=f"{value}%", delta=f"{delta}%")


def show_greeting_message():
    html_content = """
    # <a href="#"><img src="https://media.giphy.com/media/hvRJCLFzcasrR4ia7z/giphy.gif" width="25px" height="25px"></a> Welcome to QuestionOverfit!
    """
    acknowledgement = """
    ## 	:bulb: Acknowledgement
    Raw questions are sourced from [张巍老师GRE: Verbal机经1600题](https://mp.weixin.qq.com/s/bPUOg1DyviBpME3xLdTaPA).
    """

    how_to_use = """
    ## 	:package: How to use?
    With the **sidebar** on your left:
    1. Select a number of questions to fit! 
    2. Select a difficulty level!
    3. Begin `Fit`! Everytime you hit the `Fit` button, a number of random question of the difficulty level you selected would be sampled without replacement.
    """

    st.markdown(html_content, unsafe_allow_html=True)
    st.markdown("")
    st.markdown("Author: [CodeBoyPhilo](https://github.com/CodeBoyPhilo)")
    st.divider()
    st.markdown(acknowledgement)
    st.markdown(how_to_use)
    st.warning(
        "The raw questions are extracted using OCR algorithm.\n Some questions are incomplete, missing blanks and choices, or are formatted wrongly.\n If you encountered such question, please report the Question ID to the author!",
        icon="⚠️",
    )


def show_batch_summary():
    text1 = f"""
    ##### Total Questions Fit: {st.session_state.show}\n
    ##### Total Correct: {st.session_state.n_correct}\n
    """
    if st.session_state.correct_rate_tracker[-1] >= 80:
        st.header(":trophy: Fantastic! You are ready to be deployed!")

    elif st.session_state.correct_rate_tracker[-1] >= 50:
        st.header("	:mortar_board: Great! You are nearly there!")
    else:
        st.header(":sweat_smile: Ehh! You should fit with another batch!")

    st.markdown(text1)
    show_metric()
    st.session_state.not_show_summary = True
    with open("philo/history.json", "w") as file:
        json.dump(st.session_state.history, file)


difficulty_mapper = {
    "**Easy** :baby_chick: ": "easy",
    "**Medium** :bird: ": "medium",
    "**Hard** 	:penguin: ": "hard",
}

conn = st.connection("gre_verbal_db", type="sql")
# conn = st.connection('snowflake')
data = conn.query("SELECT * FROM verbal.QUESTIONS_CHOICES_ANSWERS")
data.columns = data.columns.str.upper()
data["ISCORRECT"] = data["ISCORRECT"].astype(str)

if "history" not in st.session_state:
    with open("philo/history.json", "r") as file:
        st.session_state.history = json.load(file)
if "data" not in st.session_state:
    data = data[~data["QUESTIONID"].isin(st.session_state.history.keys())]
    st.session_state.data = data
if "show" not in st.session_state:
    st.session_state.show = None
if "level" not in st.session_state:
    st.session_state.level = list()


st.sidebar.markdown("# 	:100: I will fit with: ")
st.session_state.show = st.sidebar.slider(
    "***Select a number of questions to fit***",
    min_value=1,
    max_value=20,
    value=10,
    step=1,
)

st.session_state.level = st.sidebar.radio(
    "",
    ["**Easy** :baby_chick: ", "**Medium** :bird: ", "**Hard** 	:penguin: "],
    index=None,
)


if "current_qid" not in st.session_state:
    st.session_state.current_qid = None

if "set1_choice" not in st.session_state:
    st.session_state.set1_choice = None
if "set2_choice" not in st.session_state:
    st.session_state.set2_choice = None
if "set3_choice" not in st.session_state:
    st.session_state.set3_choice = None
if "choice" not in st.session_state:
    st.session_state.choice = [None] * 3
if "not_show_prev_next" not in st.session_state:
    st.session_state.not_show_prev_next = True
if "finished_check" not in st.session_state:
    st.session_state.finished_check = False
if "not_show_summary" not in st.session_state:
    st.session_state.not_show_summary = True


if st.session_state.level is not None:
    if st.sidebar.button("**Fit**", type="primary", use_container_width=True):
        st.balloons()
        time.sleep(2)
        st.write(" ")
        st.session_state.current_qid = 1
        st.session_state.parsed_sample_questions = parse_sampled_question(
            sample_questions(
                show=st.session_state.show,
                difficulty=difficulty_mapper.get(st.session_state.level),
            )
        )
        st.session_state.not_show_prev_next = False
        st.session_state.total_blanks = 0
        st.session_state.total_correct = 0
        st.session_state.correct_rate_tracker = [0]
        st.session_state.n_correct = 0

try:
    if st.session_state.not_show_summary:
        if not st.session_state.not_show_prev_next:
            left, right = st.columns(2)
            if left.button(
                "Previous", key="Previous", type="secondary", use_container_width=True
            ):
                if st.session_state.current_qid > 1:
                    st.session_state.current_qid -= 1
            if right.button(
                "Next", key="Next", type="secondary", use_container_width=True
            ):
                if st.session_state.current_qid < st.session_state.show:
                    st.session_state.current_qid += 1
                    st.session_state.finished_check = False

        show_questions(
            st.session_state.parsed_sample_questions[st.session_state.current_qid]
        )

        check = st.button(
            "Check", key="Check_show", type="primary", use_container_width=True
        )
        if check:
            check_answer(
                st.session_state.parsed_sample_questions[st.session_state.current_qid]
            )
            if st.session_state.current_qid == st.session_state.show:
                placeholder1, placeholder2, placeholder3 = st.columns(3)
                with placeholder2:
                    st.session_state.not_show_summary = st.button(
                        "Show My Batch Result", use_container_width=True
                    )

    else:
        show_batch_summary()
        # BUG: when the user fits one batch and immediately wants to fit another batch, it fails to properly do so. The slider will update the question shown, and the first question fails to be checked.


except AttributeError:
    show_greeting_message()
