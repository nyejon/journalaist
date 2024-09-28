
from mistralai import Mistral, UserMessage, SystemMessage, AssistantMessage
import streamlit as st
import os
from PIL import Image

import mistral_files
import prompts
st.title("Your Personal JournalAIst")
st.write("""
        Hi! Did you have a cool experience recently? Maybe a fun trip? 
        Upload some photos, let me ask you a few question,
        and I'll help you write a story about it!
""")


# TODO: set up config before process starts

CONFIG = {"style": "Bill Bryson", 
          "viewpoint": "first-person",
          "story_type": "blog post",}




# Function to reset the state
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

client = Mistral(api_key=api_key)

# Initialize the model in session state if it's not already set
if "mistral_model" not in st.session_state:
    st.session_state["mistral_model"] = "mistral-large-latest"

if "pixtral_model" not in st.session_state:
    st.session_state["pixtral_model"] = "pixtral-12b-2409"

# Add system prompt input
if "system_prompt" not in st.session_state:
    # Load prompt from file
    st.session_state["system_prompt"] = prompts.render_template_from_file(
        "prompts/interview.md"
    )
# st.text_input('System Prompt', value=st.session_state["system_prompt"], key="system_prompt")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Add system prompt as a UserMessage if it doesn't exist
if st.session_state["system_prompt"] and not any(
    message.role == "system" for message in st.session_state.messages
):
    st.session_state.messages.insert(
        0, SystemMessage(content=st.session_state["system_prompt"])
    )

n_pictures = 0
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "png"], accept_multiple_files=True)
if uploaded_files:
    cols = st.columns(len(uploaded_files))
    for col, uploaded_file in zip(cols, uploaded_files):
        n_pictures += 1
        image = Image.open(uploaded_file)
        col.image(image, use_column_width=True)
        image.save(f"/tmp/picture_{n_pictures}.jpg")

    file_info = mistral_files.handle_files(uploaded_files, client, model=st.session_state["pixtral_model"])

    st.session_state.messages.append(file_info)

for message in st.session_state.messages:
    if message.role != "system":  # Skip system messages for UI
        with st.chat_message(message.role):  # Use dot notation here
            st.markdown(message.content)  # And here

# Add system message to the conversation log
intro_message = AssistantMessage(content="Hi! What did you get up to today?")
st.session_state.messages.append(intro_message)

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
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    else:
        # Handle the case where response_generator is None
        st.error("Failed to generate response")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append(AssistantMessage(content=full_response))


# Add end conversation button outside of the chat input condition
end_conversation = st.button("End Conversation")

if end_conversation:
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
         style=CONFIG['style'], 
         viewpoint=CONFIG['viewpoint'],
         story_type=CONFIG['story_type'],
         background_info_interview=conversation_text, 
         # TODO add pictures
         n_pictures=n_pictures)
    
    print(story_prompt)
    story_response = client.chat.complete(
        model=st.session_state["mistral_model"],
        messages=[UserMessage(role="user", content=story_prompt)],
    )
    story = story_response.choices[0].message.content

    # Format the story as markdown
    st.markdown(story)

        # Save the story to a markdown file
    with open('stories/story.md', 'w') as f:
        f.write(story)


