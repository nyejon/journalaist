import os
import streamlit as st

from mistralai import Mistral, UserMessage, SystemMessage, AssistantMessage
import streamlit as st
import os

import prompts
import re
import base64
from pathlib import Path

def markdown_images(markdown):
    # example image markdown:
    # ![Test image](images/test.png "Alternate text")
    images = re.findall(r'(!\[(?P<image_title>[^\]]+)\]\((?P<image_path>[^\)"\s]+)\s*([^\)]*)\))', markdown)
    return images


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def img_to_html(img_path, img_alt):
    img_format = img_path.split(".")[-1]
    img_html = f'<img src="data:stories/{img_format.lower()};base64,{img_to_bytes(img_path)}" alt="{img_alt}" style="max-width: 100%;">'

    return img_html


def markdown_insert_images(markdown):
    images = markdown_images(markdown)

    for image in images:
        image_markdown = image[0]
        image_alt = image[1]
        image_path = image[2]
        if os.path.exists(image_path):
            markdown = markdown.replace(image_markdown, img_to_html(image_path, image_alt))
    return markdown



def story_generation(client):
    st.title("Your Personal JournalAIst")
    st.write("""
            I will now generate a story for you. 
            Please select the writing style, viewpoint, and story type you would like me to use.
    """)

    # Create columns for horizontal layout
    col1, col2, col3 = st.columns(3)

    # Create radio buttons for each configuration option in separate columns
    with col1:
        st.session_state.CONFIG["style"] = st.radio(
            "Select the writing style:",
            ["Bill Bryson", "Hemingway", "J.K. Rowling"],
            index=["Bill Bryson", "Hemingway", "J.K. Rowling"].index(st.session_state.CONFIG["style"]),
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

    if st.button("Start writing!"):
        # Export conversation history
        with open("conversation_histories/conversation_history.txt", "w") as f:
            print("Exporting conversation history...")
            for message in st.session_state.messages:
                f.write(f"{message.role}: {message.content}\n")

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


 
