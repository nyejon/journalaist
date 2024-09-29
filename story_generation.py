import os
import streamlit as st

from mistralai import Mistral, UserMessage, SystemMessage, AssistantMessage
import streamlit as st
import os

import prompts
from markdown_formatter import markdown_insert_images
import re
import base64
from pathlib import Path
import shutil

if "written" not in st.session_state:
    st.session_state.written = False

def story_generation(client):
    st.title("Your Personal JournalAIst")
    st.write("""
            ### I will now generate a story for you. 
            ### Please select the writing style, viewpoint, and story type you would like me to use.
    """)

    # Create columns for horizontal layout
    col1, col2, col3 = st.columns(3)

    # Create radio buttons for each configuration option in separate columns
    with col1:
        st.session_state.CONFIG["style"] = st.radio(
            "Select the writing style:",
            ["Bill Bryson", "Hemingway", "J.K. Rowling", "Neil Gaiman"],
            index=["Bill Bryson", "Hemingway", "J.K. Rowling", "Neil Gaiman"].index(st.session_state.CONFIG["style"]),
        )

    with col2:
        st.session_state.CONFIG["viewpoint"] = st.radio(
            "Select the viewpoint:",
            ["first-person", "second-person", "third-person"],
            index=["first-person", "second-person", "third-person"].index(st.session_state.CONFIG["viewpoint"]),
        )

    with col3:
        st.session_state.CONFIG["story_type"] = st.radio(
            "Select the story type:",
            ["blog post", "short story", "article"],
            index=["blog post", "short story", "article"].index(st.session_state.CONFIG["story_type"]),
        )

    start_writing_button = st.empty()
    start_writing = start_writing_button.button("Start writing!")


    if start_writing:
        start_writing_button.empty()
        # Export conversation history
        with open("conversation_histories/conversation_history.txt", "w") as f:
            print("Exporting conversation history...")
            for message in st.session_state.messages:
                f.write(f"{message.role}: {message.content}\n")

        st.session_state.written = True

        # Clear conversation history
        conversation_log = st.session_state.messages
        st.session_state.messages = []

        # Read the conversation log from the text file
        with open('conversation_histories/conversation_history.txt', 'r') as f:
            conversation_text = f.read()

        # Use the Mistral API to generate a story based on the conversation log
        #story_prompt = f"Write a short, evocative story based on the following conversation log. Use markdown formatting where appropriate:\n\n{conversation_text}\n\nStory:"
        story_prompt = prompts.render_template_from_file(
            "prompts/story_teller.md",
            style=st.session_state.CONFIG['style'],
            viewpoint=st.session_state.CONFIG['viewpoint'],
            story_type=st.session_state.CONFIG['story_type'],
            background_info_interview=conversation_text,
            # TODO add pictures
            n_pictures=st.session_state.n_pictures)

        #print(story_prompt)
        client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        story_response = client.chat.complete(
            model=st.session_state["mistral_model"],
            messages=[UserMessage(role="user", content=story_prompt)],
        )
        story = story_response.choices[0].message.content

        # Save the story to a markdown file
        with open('stories/story.md', 'w') as f:
            f.write(story)

        with open('stories/story.md', "r") as story_file:
            story = story_file.read()

        story = markdown_insert_images(story)
        with st.container():
            st.markdown(story, unsafe_allow_html=True)


    if st.session_state.written:

        shutil.make_archive("story", 'zip', "stories/")

        with open("story.zip", "rb") as fp:
            download_button = st.download_button(
                label="Download story",
                data=fp,
                file_name="story.zip",
                mime="application/zip"
            )