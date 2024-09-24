import os
import re
import time

import openai
import requests
from openai import OpenAI


# Set up your OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]


def get_picture(description: str, model: str = "dall-e-3", size: str = "1024x1024", quality="standard", n: int = 1) -> str:
    """
    See https://platform.openai.com/docs/guides/images/usage?context=node
    :return: URL
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.images.generate(
        model=model,
        prompt=description,
        size=size,
        quality=quality,
        n=n,
    )
    image_url = response.data[0].url
    return image_url


def get_picture_and_download(save_loc: str, description: str, model: str = "dall-e-3", size: str = "1024x1024", quality="standard", n: int = 1):
    image_url = get_picture(description, model, size, quality, n)
    print("Got art at URL: ", image_url)
    # os.system(f"wget {image_url} -O {save_loc}")
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_loc, 'wb') as file:
            file.write(response.content)
            print(f"Saved file! {save_loc}")


if __name__ == "__main__":
    description = "A depiction of ethereal figures, akin to Shade Wraiths, in ancient tapestries or sculptures, in a style reminiscent of medieval or Renaissance paintings."
    pic = get_picture(description)
    print(pic)