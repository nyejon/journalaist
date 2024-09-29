from mistralai import Mistral
from mistralai.utils import BackoffStrategy, RetryConfig
import streamlit as st
import os
import uuid


import interview, story_generation, final_page


def reset_state():
    for key in st.session_state:
        del st.session_state[key]



# Get the API key from the environment variables or the user
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = st.text_input(
            "Enter your API key", type="password"
        )
    api_key = st.session_state["api_key"]
else:
    if expected_password := os.getenv("PASSWORD"):
        password = st.text_input("What's the secret password?", type="password")
        # Check if the entered key matches the expected password
        if password != expected_password:
            api_key = ""
            st.error("Unauthorized access.")
            reset_state()  # This line will reset the script
        else:
            api_key = os.getenv("MISTRAL_API_KEY")

# Initialize the model in session state if it's not already set
if "mistral_model" not in st.session_state:
    st.session_state["mistral_model"] = "mistral-large-latest"
if "pixtral_model" not in st.session_state:
    st.session_state["pixtral_model"] = "pixtral-12b-2409"

# st.text_input('System Prompt', value=st.session_state["system_prompt"], key="system_prompt")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "picture_messages" not in st.session_state:
    st.session_state.picture_messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "photo_upload" not in st.session_state:
    st.session_state.photo_upload = None

if "CONFIG" not in st.session_state:
    st.session_state.CONFIG = {
        "style": "Bill Bryson",
        "viewpoint": "first-person",
        "story_type": "blog post",
    }

if "page" not in st.session_state:
    st.session_state.page = "chat"

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4()

    if not os.path.exists("./stories/" + str(st.session_state.session_id)):
        os.makedirs("./stories/" + str(st.session_state.session_id))

client = Mistral(
    api_key=api_key,
    timeout_ms=60000,
    # retry_config=RetryConfig("backoff", BackoffStrategy(5000, 60000, 1.5, 300000), True),
)

if st.session_state.page == "chat":
    interview.interview(client)
elif st.session_state.page == "story":
    story_generation.story_generation(client)
elif st.session_state.page == "final":
    final_page.final_page(client)
