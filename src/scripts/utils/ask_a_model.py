from PIL import Image
from io import BytesIO
import base64
import ollama
from src.scripts.utils.prompts.prompts import system_prompt
import json

def query_model(img:Image.Image, prompt:str) -> str:
    print("[INFO] Querying model with image and prompt...")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    response = ollama.generate(
        model="llama3.2-vision:11b",
        prompt=prompt,
        system=system_prompt,
        images=[img_b64],
        options={
            "temperature": 0.0
        }
    )

    return response["response"]
