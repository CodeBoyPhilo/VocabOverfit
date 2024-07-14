from pandas._libs.tslibs.offsets import BYearEnd

import streamlit as st
from streamlit import session_state as session

# ==============================
# CONSTANT VARIABLES
# ==============================

GREETER = """
# Welcome to VocabOverfit <a href="#"><img src="https://media.giphy.com/media/hvRJCLFzcasrR4ia7z/giphy.gif" width="35px" height="35px"></a> !
"""

BYLINE = """
### by [CodeBoyPhilo](https://github.com/CodeBoyPhilo)
"""

ACKNOWLEDGEMENT = """
## 	:bulb: Acknowledgement 
The vocabulary details are adapted from [**liurui39660/3000**](https://github.com/liurui39660/3000) and **张巍老师GRE**.
"""

INTRO_HEADER = """
## :package: How to get the most out of VocabOverfit?
"""

INTRO_INFO = """
the VocabOverfit has three implemented modules: `Vocab2Math`, `VocabEval`, and `VocabRevise`, each has its own purpose.
"""

VOCAB2MATH_DESC = """
### :notebook_with_decorative_cover: Vocab2Math 
Use Vocab2Math to study and memorise the vocabularies:
1. Select `study` mode first
2. Try to memorise the Chinese definition of the word and make sense of the vocab equations
3. Select `review` mode next
4. Try to recall the Chinese definition of the word using the vocab equations as hints
"""

VOCAB2MATH_INFO = """
The vocab equations may not suit everyone, don't let it overwhelm you!Feel free to use these equations to help you memorise the vocabularies!
"""

VOCABEVAL_DESC = """
### :pencil: VocabEval
Use VocabEval to test your knowledge about the vocabularies:
1. Press the `Start` button on the sidebar to begin
2. Hit the `Submit` button to submit and evaluate your selection
3. Good luck, have fun
"""

VOCABEVAL_WARNING = """
The order of the vocabularies will be randomly shuffled by default.
Your current evaluation result will only be saved when you finished the list and saw the exit message.
"""

VOCABREVISE_DESC = """
### :bookmark_tabs: VocabRevise
Use VocabRevise to revise for the vocabularies that you ill-memorised:
1. Select `revise` on the sidebar to go through the ill-memorised vocabularies
2. Select `test` to evaluate your knowledge again
"""

VOCABREVISE_INFO = """
You need to succeed the `test` **three** times to empty a revision list
"""

# ==============================
# INITIATE SESSION STATE
# ==============================
if "vocab_list" not in session:
    session.vocab_list = "list1"


# ==============================
# MAIN APP EXECUTION STARTS HERE
# ==============================

session.vocab_list = st.sidebar.selectbox(
    "**Select a vocabulary list**",
    [f"list{i}" for i in range(1, 33)],
    label_visibility="visible",
)

# -----------Homepage Message-----------

st.markdown(GREETER, unsafe_allow_html=True)

left, mid, right = st.columns(3)
with right:
    st.markdown(BYLINE)

st.markdown(ACKNOWLEDGEMENT)

st.markdown(INTRO_HEADER)
st.info(INTRO_INFO)

vocab2math_tab, vocabeval_tab, vocabrevise_tab = st.tabs(
    [
        ":notebook_with_decorative_cover: Vocab2Math",
        ":pencil: VocabEval",
        ":bookmark_tabs: VocabRevise",
    ]
)

with vocab2math_tab:
    st.markdown(VOCAB2MATH_DESC)
    st.info(VOCAB2MATH_INFO)

with vocabeval_tab:
    st.markdown(VOCABEVAL_DESC)
    st.warning(VOCABEVAL_WARNING)

with vocabrevise_tab:
    st.markdown(VOCABREVISE_DESC)
    st.warning(VOCABREVISE_INFO)

st.divider()
