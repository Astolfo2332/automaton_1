import os

from src.scripts.utils.prompts.prompts import system_prompt_ocr_mk
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from PIL import Image
from src.scripts.utils.pdf_loader import convert_img_to_bytes
from tests.llm_ocr_models.base_ocr_model import BaseOcrModel
from transformers import Qwen3VLForConditionalGeneration
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info


class QwenVlManager(BaseOcrModel):
    def __init__(self, model_name: str = None):
        super().__init__()
        model_name = model_name if model_name is not None else os.getenv("VISION_MODEL")
        self.model = OllamaLLM(model=model_name,
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


class Qwen25VlTransformersManager(BaseOcrModel):
    def __init__(self):
        super().__init__()
        self.model_name = "Qwen/Qwen2.5-VL-7B-Instruct"

    def start(self):
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            self.model_name,
            dtype="auto",
            device_map="auto",
        )

        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
        )
    def process(self, image_path: str) -> str:
        if self.model is None or self.processor is None:
            raise ValueError("Model and processor must be initialized. Call start() before process().")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": f"file://{image_path}",
                    },
                    {"type": "text", "text": system_prompt_ocr_mk},
                ],
            }
        ]

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=16384)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        return output_text[0]

    def delete(self):
        del self.model
        del self.processor
        import torch
        torch.cuda.empty_cache()


class QwenVlTransformersManager(BaseOcrModel):
    def __init__(self, model_name: str = None):
        super().__init__()
        self.model_name = "Qwen/Qwen3-VL-4B-Thinking" if model_name is None else model_name


    def start(self):

        self.model = Qwen3VLForConditionalGeneration.from_pretrained(
            self.model_name,
            dtype="auto",
            device_map="auto",
        )

        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
        )

    def process(self, image_path: str) -> str:
        if self.model is None or self.processor is None:
            raise ValueError("Model and processor must be initialized. Call start() before process().")

        image = Image.open(image_path).convert("RGB")

        messages = [
            {"role": "user",
             "content": [
                 {"type": "image", "image": image},
                 {"type": "text", "text": system_prompt_ocr_mk}
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
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, outputs)
        ]

        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        return output_text[0]

    def delete(self):
        del self.model
        del self.processor
        import torch
        torch.cuda.empty_cache()