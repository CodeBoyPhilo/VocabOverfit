from pathlib import Path

import pandas as pd
from numpy import fromfile

import streamlit as st
from streamlit import session_state as session


def sample_question():
    

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
if "prev_vocab_list" not in session:
    session.prev_vocab_list = "list1"
# ==============================
# MAIN APP EXECUTION STARTS HERE
# ==============================
session.vocab_list = st.sidebar.selectbox(
    "**Select a vocabulary list**",
    [f"list{i}"for i in range(1,33)],
    label_visibility="visible"
)

data = pd.read_csv(DATA_DIR)
if "data" not in session:
    session.data = data
    session.data = session.data.sample(frac=1).reset_index(drop=True)

if session.vocab_list is not None:
    session.list_data = session.data[session.data["list"] == session.vocab_list]
    session.n_vocab = session.list_data.shape[0]

session.start = st.sidebar.button(
    "**Start**",
    type = "primary",
)

if session.start:
    # start 
    pass
else:
    pass

