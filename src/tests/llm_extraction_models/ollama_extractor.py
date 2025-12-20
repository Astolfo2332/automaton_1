from tests.llm_extraction_models.base_extractor import BaseExtractor
from langchain_ollama import ChatOllama
from scripts.data_models.invoices import Invoice


class OllamaExtractor(BaseExtractor):
    def __init__(self, model_name:str=None):
        super().__init__()

        if not model_name:
            raise ValueError("model_name must be provided for OllamaExtractor")

        self.model = ChatOllama(
            model=model_name,
        )
        self.model_structure = self.model.with_structured_output(Invoice)
