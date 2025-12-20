from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage
from tests.llm_ocr_models.base_ocr_model import BaseOcrModel
import base64

from tenacity import retry, wait_fixed, stop_after_attempt


class GeminiManager(BaseOcrModel):
    def __init__(self, model_name: str = "gemini-3-flash-preview",
                 temperature: float = 1.0):
        super().__init__()
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
        )
        # self.model = self.model.with_structured_output(Invoice)
        self.prompt_ocr = """Perform Optical Character Recognition (OCR) on the following image data.
Extract the text from the above document as if you were reading it naturally. Return the tables in html format. Return the equations in LaTeX representation. If there is an image in the document and image caption is not present, add a small description of the image inside the <img></img> tag; otherwise, add the image caption inside <img></img>. Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY</watermark>. Page numbers should be wrapped in brackets. Ex: <page_number>14</page_number> or <page_number>9/22</page_number>. Prefer using ☐ and ☑ for check boxes.
 Review all the values carefully to ensure accuracy.
 The most important requirements are:
    - Dates
    - Numbers
    - Monetary amounts
    - Bills Numbers and identifiers.
"""


    @retry(wait=wait_fixed(60), stop=stop_after_attempt(3), reraise=True)
    def process(self, image_path:str) -> str:

        image = open(image_path, "rb").read()
        image = base64.b64encode(image).decode("utf-8")

        message = HumanMessage(
            content=[
                {"type": "text", "text": self.prompt_ocr},
                {"type": "image", "base64": image, "mime_type": "image/jpeg"}
            ]
        )

        response = self.model.invoke([message])

        if isinstance(response.content, list):
            response_data = response.content[0]
            if isinstance(response_data, dict):
                return response.content[0].get("text", "")
            else:
                return response_data

        return response.content

if __name__ == "__main__":
    from google import genai
    from dotenv import load_dotenv
    load_dotenv()

    client = genai.Client()
    models = client.models.list()
    print(models.page)



