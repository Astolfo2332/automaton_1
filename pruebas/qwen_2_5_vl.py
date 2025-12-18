import os
from src.scripts.utils.prompts.prompts import system_prompt_ocr_mk
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from PIL import Image
from src.scripts.utils.pdf_loader import convert_img_to_bytes
from pruebas.base_ocr_model import BaseOcrModel

class Qwen25vlManager(BaseOcrModel):
    def __init__(self):
        super().__init__()
        self.model = OllamaLLM(model=os.getenv("VISION_MODEL"),
                               temperature=0.0,
                               num_predict=15000)

        self.prompt_ocr = ChatPromptTemplate.from_messages([
            ("system", system_prompt_ocr_mk)
        ])

    def process(self, image_path: str) -> str:
        img = Image.open(image_path)
        img = convert_img_to_bytes([img])
        formated_prompt = self.prompt_ocr.format_messages()
        model_with_image = self.model.bind(images=img)
        response = model_with_image.invoke(formated_prompt)
        return response


