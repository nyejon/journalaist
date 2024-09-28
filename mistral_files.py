import base64
from PIL import Image
import prompts
from mistralai import (
    Mistral,
    UserMessage,
    SystemMessage,
    AssistantMessage,
    UserMessageContent,
)


def encode_image_base64(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


def handle_files(files: list, client: Mistral, model: str):
    content = []
    for file in files:
        if file.type.startswith("image/jpeg"):
            list_image = encode_image_base64(file)
            content.append(
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{list_image}"}
            )
        elif file.type.startswith("image/png"):
            list_image = encode_image_base64(file)
            content.append(
                {"type": "image_url", "image_url": f"data:image/png;base64,{list_image}"}
            )

    system_messages = SystemMessage(
        content=prompts.render_template_from_file("prompts/picture_information.md")
    )
    picture_messages = UserMessage(content=content)
    chat_response = client.chat.stream(
        model=model,
        messages=[system_messages, picture_messages],
    )

    return chat_response
