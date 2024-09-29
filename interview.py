import os
import streamlit as st

from mistralai import Mistral, UserMessage, SystemMessage, AssistantMessage
import streamlit as st
import os
from PIL import Image

import mistral_files
import prompts

import base64
import requests

def interview(client: Mistral):


    # image = Image.open("journalaist_logo.webp")
    # col1, col2 = st.columns([4, 1])
    # with col1:
    st.title("Your Personal JournalAIst")
    # with col2:
    #     st.image(image, width=100)
    st.subheader("Generate a personal story by uploading pictures and answering a few questions.")
    st.write("""
            Hi! What did you get up to today?
            Upload some pictures and give me a short description of your day.
    """)

    if st.session_state.photo_upload is None:
        # Add end conversation button outside of the chat input condition
        st.write("Would you like to upload photos?")
        st.session_state.n_pictures = 0

        col1, col2 = st.columns(2)
        with col1:
            upload_photos_yes = st.button("Yes")
        with col2:
            upload_photos_no = st.button("No")

        if upload_photos_yes is True:
            st.session_state.photo_upload = True
        elif upload_photos_no is True:
            st.session_state.photo_upload = False


    if st.session_state.photo_upload:

        uploaded_files = st.file_uploader(
            "Choose images...", type=["jpg", "png"], accept_multiple_files=True
        )
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            if not os.path.exists("./stories"):
                os.makedirs("./stories")
            # st.session_state.photo_upload = False

    if len(st.session_state.uploaded_files) > 0:
        cols = st.columns(len(st.session_state.uploaded_files))
        for col, uploaded_file in zip(cols, st.session_state.uploaded_files):
            image = Image.open(uploaded_file)
            col.image(image, use_column_width=True)


        if "processed_uploaded_files" not in st.session_state:
            # Save uploaded files
            for uploaded_file in st.session_state.uploaded_files:
                st.session_state.n_pictures += 1
                image = Image.open(uploaded_file)
                image_location = f"./stories/{st.session_state.session_id}/picture_{st.session_state.n_pictures}.jpg"
                image.convert("RGB").save(image_location)

                ## uncomment to try upload to API
                """
                with open(image_location, "rb") as file:
                    url = "https://api.imgbb.com/1/upload"
                    payload = {
                        "key": os.getenv("IMGBB_API_KEY"),
                        "image": base64.b64encode(file.read()),
                    }
                    res = requests.post(url, payload)

                print(res)
                """


            file_info = mistral_files.handle_files(
                st.session_state.uploaded_files,
                client,
                model=st.session_state["pixtral_model"],
            )

            picture_response = ""
            #message_placeholder = st.empty()
            if file_info:
                picture_response += file_info.choices[0].message.content
                st.session_state.picture_information = picture_response
                #message_placeholder.markdown(picture_response + "▌")
                #message_placeholder.markdown(picture_response)
            else:
                # Handle the case where response_generator is None
                st.error("Failed to generate response")
                #message_placeholder.markdown(picture_response)

            st.session_state.picture_messages.append(
                AssistantMessage(content=picture_response)
            )

            st.session_state.processed_uploaded_files = True


    # Only show the system prompt and chat once the pictures are uploaded
    if (
        "processed_uploaded_files" in st.session_state
        or st.session_state.photo_upload is False
    ):

        # Add system prompt input
        if "system_prompt" not in st.session_state:
            picture_info = ""
            if st.session_state.photo_upload:
                picture_info = "The information about each picture is provided below: \n"
                for picture_message in st.session_state.picture_messages:
                    picture_info = picture_info + picture_message.content

            print(picture_info)
            # Load prompt from file
            st.session_state["system_prompt"] = prompts.render_template_from_file(
                "alt_prompts/interview.md", picture_info=picture_info
            )

            # print(st.session_state["system_prompt"])

        # Add system prompt as a UserMessage if it doesn't exist
        if st.session_state["system_prompt"] and not any(
            message.role == "system" for message in st.session_state.messages
        ):
            st.session_state.messages.insert(
                0, SystemMessage(content=st.session_state["system_prompt"])
            )

            if st.session_state.n_pictures > 0:
                intro_message = AssistantMessage(
                    content=f"Hi! I saw you uploaded {st.session_state.n_pictures} pictures. \
                    Give me a short summary of the images and what you did today? \
                    Just give me the bullet points, at least five if you can."
                )
            else:
            # Add system message to the conversation log
                intro_message = AssistantMessage(
                    content="Hi! Tell me about a meaningful event from in your life!"
                )
            st.session_state.messages.append(intro_message)


        #TODO: Comment out when we don't want to render the picture description
        #for message in st.session_state.picture_messages:
        #    if message.role != "system":  # Skip system messages for UI
        #        with st.chat_message(message.role):  # Use dot notation here
        #            st.markdown(message.content)  # And here

        for message in st.session_state.messages:
            if message.role != "system":  # Skip system messages for UI
                with st.chat_message(message.role):  # Use dot notation here
                    st.markdown(message.content)  # And here

        if prompt := st.chat_input(
            "What event would you like me to write a story about?"
        ):
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
            st.session_state.page = "story"
            st.rerun()
