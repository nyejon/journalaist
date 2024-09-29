import os
import time
from lumaai import LumaAI
import requests
import streamlit as st


def generate_video(session_id, prompt):

    client = LumaAI(
        auth_token=os.environ.get("LUMA_API_KEY"),
    )

    generation = client.generations.create(
        prompt=prompt,
    )

    completed = False

    with st.spinner(text=f"Status: {generation.state}"):
        while not completed:
            generation = client.generations.get(id=generation.id)  # type: ignore
            if generation.state == "completed":
                completed = True
            elif generation.state == "failed":
                raise RuntimeError(f"Generation failed: {generation.failure_reason}")
            # st.info(f"Status: {generation.state}")
            print(f"Status: {generation.state}")

            time.sleep(3)

    video_url = generation.assets.video  # type: ignore

    # download the video
    response = requests.get(video_url, stream=True)  # type: ignore
    file_path = f"stories/{session_id}/{generation.id}.mp4"
    with open(file_path, "wb") as file:
        file.write(response.content)
    print(f"File downloaded as {generation.id}.mp4")
    return file_path
