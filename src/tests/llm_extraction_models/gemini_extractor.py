from langchain_google_genai import ChatGoogleGenerativeAI

from scripts.data_models.invoices import Invoice


class GeminiExtractor:
    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        super().__init__()
        self.model = ChatGoogleGenerativeAI(model=model_name)
        self.model_structure = self.model.with_structured_output(Invoice)