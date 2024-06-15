import os

import streamlit as st


def show_greeter():
    html_content = """
    # <a href="#"><img src="https://media.giphy.com/media/hvRJCLFzcasrR4ia7z/giphy.gif" width="25px" height="25px"></a> Welcome to VocabQuery!
    """

    acknowledgement = """
    ## :bulb: Acknowledgement
    Raw vocabulary data are sourced from [liurui39660/3000](https://github.com/liurui39660/3000)
    """

    # TODO: add a how to use instruction
    how_to_use = None

    st.markdown(html_content, unsafe_allow_html=True)
    st.markdown("")
    st.markdown("Author: [CodeBoyPhilo](https://github.com/CodeBoyPhilo)")
    st.divider()
    st.markdown(acknowledgement)


def build_user_profile():

    name = st.text_input("Profile name, no special characters allowed!")

    build = st.button("Build")

    try:
        if build:
            st.session_state.current_profile = name
            os.makedirs(
                os.path.join(app_dir, st.session_state.current_profile), exist_ok=False
            )
            st.balloons()
            st.session_state.build_profile = False
        else:
            pass
    except Exception as e:
        st.write(e)


# ==============================
# DEFINE SESSION STATES
# ==============================
if "data" not in st.session_state:
    st.session_state.data = None
if "build_profile" not in st.session_state:
    st.session_state.build_profile = False
if "current_profile" not in st.session_state:
    st.session_state.current_profile = ""

# ==============================
# MAIN APP EXECUTION STARTS HERE
# ==============================
app_dir = os.getcwd()

conn = st.connection("gre_vocabulary_db", type="sql")
data = conn.query("SELECT * FROM vocabulary.gre_3000")
st.session_state.data = data

# Home Page
show_greeter()
st.write(st.session_state.build_profile)
st.markdown("I am:")
left, right = st.columns(2)
if left.button(
    "Existing Profile", key="Existing", type="primary", use_container_width=True
):
    pass
if right.button("New Profile", key="New", type="primary", use_container_width=True):
    st.session_state.build_profile = True

if st.session_state.build_profile:
    st.write(st.session_state.build_profile)
    build_user_profile()
