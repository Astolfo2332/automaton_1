import os

import ollama
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
# from ollama_ocr import OCRProcessor
from dotenv import load_dotenv


from src.scripts.data_models.invoices import Invoice
from src.scripts.utils.prompts.prompts import (system_prompt,
system_prompt_ocr, system_prompt_ocr_mk, system_prompt_xml,
                                               user_prompt_ocr_mk)
# from src.scripts.utils.transformers_process import TransformersLLM, prompt_for_transformers_ocr
import json
from src.scripts.utils.llm_ocr_models.gemini import GeminiManager

load_dotenv()

def query_model(img:str, prompt:str) -> str:
    response = ollama.generate(
        model="llama3.2-vision:11b",
        prompt=prompt,
        system=system_prompt,
        images=[img],
        options={
            "temperature": 0.0
        }
    )
    try:
        data = response["response"]
        data = json.loads(data)
        return list(data.values())[0]
    except:
        return response["response"]


def query_model_ocr(img:list[str]) -> str:
    text = ""
    model = OllamaLLM(model=os.getenv("VISION_MODEL"), temperature=0.0, num_predict=15000)

    prompt_ocr = ChatPromptTemplate.from_messages([
        ("system", system_prompt_ocr_mk)
    ])
    for k, i in enumerate(img):
        text += f"Page N {k + 1}\n"
        formated_prompt = prompt_ocr.format_messages()
        #ocr
        model_with_image = model.bind(images=[i])
        response = model_with_image.invoke(formated_prompt)

        text += response + "\n"

    # print("OCR response: ", text)

    return text

def query_model_ocr_transformers(img:list[str]) -> str:
    # model_name = "nanonets/Nanonets-OCR-s"
    # llm_nanonets = TransformersLLM(model_name=model_name)
    #
    # if not llm_nanonets.model_loaded:
    #     llm_nanonets.load_model(model_name)
    #
    # prompt_ocr = prompt_for_transformers_ocr(system_prompt_ocr_mk, user_prompt_ocr_mk)
    # text = ""
    # for k, i in enumerate(img):
    #     text += f"Page N {k + 1}\n"
    #     response = llm_nanonets.generate(prompt_ocr, image=i)
    #     text += response + "\n"
    #
    # return text
    pass

def query_model_ocr_ollama(path:str) -> str:
    pass

def query_model_structured(ocr_response:str) -> Invoice:
    #structured
    model = ChatOllama(model=os.getenv("GENERAL_MODEL"), temperature=0.0)
    model_structured = model.with_structured_output(Invoice)
    response = model_structured.invoke(ocr_response)

    return response

gemini_manager = GeminiManager()
def query_model_one_shot_batch(imgs:list[list[str]]):
    response, cost = gemini_manager.batch_structured_process(imgs, Invoice)
    # Precio en batches es la mitad
    print("Total cost for batch: ", cost / 2)
    return response, cost

def query_model_structure_xml(xml:list[str]):

    #structured
    response, cost = gemini_manager.batch_structured_process_xml(xml, Invoice)
    print("Total cost for XML batch: ", cost / 2)

    return response, cost
