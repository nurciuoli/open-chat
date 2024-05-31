import logging
from openai import OpenAI

client = OpenAI()

def create_file(filepath, purpose='assistants'):
    file = client.files.create(
        file=open(filepath, "rb"),
        purpose=purpose
    )
    return file

def encode_image_file(image_path):
    file = client.files.create(
        file=open(image_path, "rb"),
        purpose="vision"
    )
    return file

def append_content_w_images(prompt, images):
    content = []
    content.append({"type": "text", "text": prompt})
    for image in images:
        file = encode_image_file(image)
        content.append({
            "type": "image_file",
            "image_file": {
                "file_id": file.id,
            }
        })
    return content