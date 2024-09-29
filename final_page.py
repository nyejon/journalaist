from mistralai import SystemMessage, UserMessage
import streamlit as st
from markdown_formatter import markdown_insert_images
import luma_generate
import shutil
import os


def final_page(client):


    with open(f"stories/{st.session_state.session_id}/story.md", "r") as story_file:
        story = story_file.read()

    story = markdown_insert_images(story, session_id=st.session_state.session_id)

    with st.container():
        st.markdown(story, unsafe_allow_html=True)


    story_dir = f"./stories/{st.session_state.session_id}"
    story_path = f"{story_dir}_story"
    story_zip = f"{story_dir}_story.zip"

    if not st.session_state.saved:

        if not os.path.exists(story_zip):
            #os.makedirs(story_dir)
            shutil.make_archive(story_path, "zip", story_dir)
        st.session_state.saved = True


    with open(story_zip, "rb") as fp:
        download_button = st.download_button(
            label="Download story", data=fp, file_name=story_zip, mime="application/zip"
        )

        
    with open(f"stories/{st.session_state.session_id}/story.md", "r") as story_file:
        story = story_file.read()



    story_response = client.chat.complete(
        model=st.session_state["mistral_model"],
        messages=[
            UserMessage(
                role="user",
                content="Create a prompt to generate a 5 second video of this story. It should be less than 50 words"
                + story,
            ),
        ],
    )
    video_response = story_response.choices[0].message.content

    video_path = luma_generate.generate_video(
        st.session_state.session_id, prompt=video_response
    )

    st.video(video_path)
