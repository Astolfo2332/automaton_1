from pruebas.base_ocr_model import BaseOcrModel
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image

class PaddleOCRManager(BaseOcrModel):
    def __init__(self):
        super().__init__()
        self.model_name_or_path = "PaddlePaddle/PaddleOCR-VL"
        self.processor = None
        self.model = None
        self.prompts = {
            "ocr": "OCR:",
            "table": "Table Recognition:",
            "formula": "Formula Recognition:",
            "chart": "Chart Recognition:",
        }

    def start(self):
        if self.model is None or self.processor is None:
            self.processor = AutoProcessor.from_pretrained(self.model_name_or_path)

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name_or_path,
                torch_dtype="auto",
                device_map="auto"
            )

    def process(self, image_file: str) -> str:
        if self.model is None or self.processor is None:
            raise ValueError("Model and processor must be initialized. Call start() before process().")

        image = Image.open(image_file).convert("RGB")

        messages = [
            {"role": "user",
             "content": [
                 {"type": "image", "image": image},
                 {"type": "text", "text": self.prompts["ocr"]},
             ]
             }
        ]

        inputs = self.processor.apply_chat_template(
                    messages,
                    tokenize=True,
                    add_generation_prompt=True,
                    return_dict=True,
                    return_tensors="pt"
                    ).to(self.model.device)

        outputs= self.model.generate(**inputs, do_sample=False,
                                     max_new_tokens=16384)
        outputs = self.processor.batch_decode(outputs,
                                              skip_special_tokens=True)[0]

        return outputs

    def delete(self):
        del self.model
        del self.processor
        import torch
        torch.cuda.empty_cache()
