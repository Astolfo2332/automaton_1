import os

import ollama
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
# from ollama_ocr import OCRProcessor
from dotenv import load_dotenv


from src.scripts.data_models.invoices import Invoice
from src.scripts.utils.prompts.prompts import system_prompt, system_prompt_ocr, system_prompt_ocr_mk, system_prompt_xml
import json
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
    model = OllamaLLM(model=os.getenv("VISION_MODEL"), temperature=0.0)
    for k, i in enumerate(img):
        text += f"Page N {k + 1}\n"
        prompt_ocr = ChatPromptTemplate.from_messages([
            ("system", system_prompt_ocr)
        ])

        formated_prompt = prompt_ocr.format_messages()
        #ocr
        model_with_image = model.bind(images=[i])
        response = model_with_image.invoke(formated_prompt)

        text += response + "\n"

    # print("OCR response: ", text)

    return text

def query_model_ocr_ollama(path:str) -> str:
    # ocr = OCRProcessor(model_name=os.getenv("VISION_MODEL"))
    # result = ocr.process_image(path, language="Español", format_type="table")
    pass

    # return result

def query_model_structured(ocr_response:str) -> Invoice:
    #structured
    model = ChatOllama(model=os.getenv("GENERAL_MODEL"), temperature=0.0)
    model_structured = model.with_structured_output(Invoice)
    response = model_structured.invoke(ocr_response)

    return response

def query_model_structure_xml(xml:str) -> Invoice:
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_xml),
        ("user", f"Extrae la siguiente información de la factura xml: {xml}")
    ])
    #structured
    model = ChatOllama(model=os.getenv("GENERAL_MODEL"), temperature=0.0)
    model_structured = model.with_structured_output(Invoice)
    response = model_structured.invoke(prompt.format_messages())

    return response

if __name__ == "__main__":
    # Test the function with a sample image
    img = ""
    response = query_model_estructured(img, "cual es el valor total?")
    print(response)