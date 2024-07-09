import streamlit as st

html_content = """
# <a href="#"><img src="https://media.giphy.com/media/hvRJCLFzcasrR4ia7z/giphy.gif" width="25px" height="25px"></a> Welcome to Vocab2Math!
"""
acknowledgement = """
## 	:bulb: Acknowledgement
The vocabulary details are adapted from [**liurui39660/3000**](https://github.com/liurui39660/3000) and **张巍老师GRE**.
"""

how_to_use = """
## 	:package: How to use?
With the sidebar on the left:
1. To start revising the vocabularies, select `Vocab2Math`
2. To start examining your knowledge, select `VocabRevise`
3. Finished? Select a new list! 
"""

st.markdown(html_content, unsafe_allow_html=True)
st.markdown("")
st.markdown("Author: [CodeBoyPhilo](https://github.com/CodeBoyPhilo)")
st.divider()
st.markdown(acknowledgement)
st.markdown(how_to_use)
