from openai import OpenAI
import requests
client = OpenAI()
def prompt_image(prompt,size = "1024x1024",quality = "standard",n=1,model = "dall-e-3"):
    response = client.images.generate(
    model=model,
    prompt=prompt,
    size=size,
    quality=quality,
    n=n,
    )
    image_url = response.data[0].url
    return image_url

def get_image_from_url(image_url):
    return requests.get(image_url).content

def archive_image(image_url,filename):
    # save the image
    generated_image_url =image_url  # extract image URL from response
    generated_image = get_image_from_url(generated_image_url)
    with open(filename, "wb+") as image_file:
        image_file.write(generated_image)  # write the image to the file


from PIL import Image
from io import BytesIO

def edit_image(image_path, prompt, n=1, size="1024x1024"):
    image_content=get_image_from_url(image_path)
    img = Image.open(BytesIO(image_content))
    img = img.convert("RGBA")  # Convert to the required format
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = buffered.getvalue()

    response = client.images.edit(
        model="dall-e-2",
        image=img_str,
        prompt=prompt,
        n=n,
        size=size
    )
    image_url = response.data[0].url
    return image_url

def generate_variation(image_path,n=1,size = "1024x1024"):
    image_content = get_image_from_url(image_path)
    response = client.images.create_variation(
    image=image_content,
    n=n,
    size=size
    )

    image_url = response.data[0].url
    return image_url