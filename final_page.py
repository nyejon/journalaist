import streamlit as st
from markdown_formatter import markdown_insert_images

import shutil

def final_page():
    
    with open(f"stories/{st.session_state.session_id}/story.md", "r") as story_file:
        story = story_file.read()
    story = markdown_insert_images(story, session_id=st.session_state.session_id)
    with st.container():
        st.markdown(story, unsafe_allow_html=True)


    story_dir = f"./stories/{st.session_state.session_id}"
    story_path = f"{story_dir}/story"
    story_zip = f"{story_dir}/story.zip"
    
    shutil.make_archive(story_path, 'zip', story_dir)

    with open(story_zip, "rb") as fp:
        download_button = st.download_button(
            label="Download story",
            data=fp,
            file_name=story_zip,
            mime="application/zip"
            )