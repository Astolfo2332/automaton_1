import subprocess
from pruebas.base_ocr_model import BaseOcrModel

class DeepseekOllamaManager(BaseOcrModel):
    def __init__(self):
        super().__init__()
        pass

    def process(self, image_file: str) -> str:
        return run_deepseek_ollama(image_file)

def run_deepseek_ollama(image_file:str) -> str:
    prompt = "<|grounding|>Convert the document to markdown."

    full_prompt = f"{image_file}\n{prompt}"

    process = subprocess.run(
        ["ollama", "run", "deepseek-ocr"],
        input=full_prompt,
        text=True,
        capture_output=True,
        encoding="utf-8"
    )

    return process.stdout
