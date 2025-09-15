from transformers import AutoTokenizer, AutoProcessor, AutoModelForImageTextToText

class TransformersLLM:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            attn_implementation="flash_attention_2"
        )
        self.model.eval()
        self.model_loaded = True

    def generate(self, inputs, **kwargs) -> str:
        text = self.processor.apply_chat_template(inputs, tokenize=False, add_generation_prompt=True)

        if image := kwargs.get("image"):
            processed_inputs = self.processor(images=image, text=text, return_tensors="pt", padding=True)
        else:
            processed_inputs = self.processor(text=text, return_tensors="pt", padding=True)

        processed_inputs = processed_inputs.to(self.model.device)

        output_ids = self.model.generate(**processed_inputs, do_sample=False)
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(processed_inputs.input_ids, output_ids)]

        output_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return output_text[0]

    def unload_model(self):
        del self.model
        del self.processor
        del self.tokenizer
        import torch
        torch.cuda.empty_cache()
        self.model_loaded = False

    def load_model(self, model_name: str):
        self.__init__(model_name)
        self.model_loaded = True

def prompt_for_transformers_ocr(system_prompt_ocr_mk: str, user_prompt_ocr_mk: str):

    data = [
        {
            "role": "system", "content": system_prompt_ocr_mk
        },
        {
            "role": "user", "content": [
            {"type": "image", "image": "<image>"},
            {"type": "text", "text": user_prompt_ocr_mk}
        ]
        }
    ]

    return data
