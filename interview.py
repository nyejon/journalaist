import os
import streamlit as st

from mistralai import Mistral, UserMessage, SystemMessage, AssistantMessage
import streamlit as st
import os
from PIL import Image

import mistral_files
import prompts

def interview(client: Mistral):
    st.title("Your Personal JournalAIst")
    st.write("""
            Hi! What did you get up to today?  
            Upload some pictures if you wish, and give me a short description of your day. 
    """)

    # Add system prompt as a UserMessage if it doesn't exist
    if st.session_state["system_prompt"] and not any(
        message.role == "system" for message in st.session_state.messages
    ):
        st.session_state.messages.insert(
            0, SystemMessage(content=st.session_state["system_prompt"])
        )
        # Add system message to the conversation log
        intro_message = AssistantMessage(content="Hi! What did you get up to today?")
        st.session_state.messages.append(intro_message)

    st.session_state.n_pictures = 0
    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "png"], accept_multiple_files=True)
    if uploaded_files:
        if not os.path.exists("./stories"):
            os.makedirs("./stories")

        cols = st.columns(len(uploaded_files))
        for col, uploaded_file in zip(cols, uploaded_files):
            st.session_state.n_pictures += 1
            image = Image.open(uploaded_file)
            col.image(image, use_column_width=True)
            image.convert("RGB").save(f"./stories/picture_{st.session_state.n_pictures}.jpg")

    for message in st.session_state.picture_messages:
        if message.role != "system":  # Skip system messages for UI
            with st.chat_message(message.role):  # Use dot notation here
                st.markdown(message.content)  # And here

    for message in st.session_state.messages:
        if message.role != "system":  # Skip system messages for UI
            with st.chat_message(message.role):  # Use dot notation here
                st.markdown(message.content)  # And here


    if st.session_state.uploaded_files != uploaded_files and uploaded_files:

        # print("in here")
        file_info = mistral_files.handle_files(uploaded_files, client, model=st.session_state["pixtral_model"])

        picture_response = ""
        message_placeholder = st.empty()
        if file_info:
            for response in file_info:
                picture_response += response.data.choices[0].delta.content or ""
                message_placeholder.markdown(picture_response + "▌")
            message_placeholder.markdown(picture_response)
        else:
            # Handle the case where response_generator is None
            st.error("Failed to generate response")
            message_placeholder.markdown(picture_response)

        st.session_state.picture_messages.append(AssistantMessage(content=picture_response))

        st.session_state.uploaded_files = uploaded_files

    if prompt := st.chat_input("What event would you like me to write a story about?"):
        new_message = UserMessage(role="user", content=prompt)
        st.session_state.messages.append(new_message)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response_generator = client.chat.stream(
                model=st.session_state["mistral_model"],
                messages=st.session_state.messages,  # Pass the entire messages list
            )

        if response_generator is not None:
            for response in response_generator:
                full_response += response.data.choices[0].delta.content or ""
                message_placeholder.markdown(full_response + " ")
            message_placeholder.markdown(full_response)
        else:
            # Handle the case where response_generator is None
            st.error("Failed to generate response")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append(AssistantMessage(content=full_response))


    # Add end conversation button outside of the chat input condition
    end_conversation = st.button("End Conversation")

    if end_conversation:
        st.session_state.page = 'story'
        st.rerun()
