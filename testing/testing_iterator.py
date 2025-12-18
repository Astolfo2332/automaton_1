import pandas as pd
import os
import mlflow
from tqdm.auto import tqdm

from time import time
from pruebas.base_ocr_model import BaseOcrModel
from pruebas.huyuan_ocr import HuyuanOCRManager
from pruebas.deepseek_ollama import DeepseekOllamaManager
from pruebas.mineru_2_5 import MineruManager
from pruebas.nanonets import NanonetsOCRManager
from pruebas.qwen_2_5_vl import Qwen25vlManager
from pruebas.paddle import PaddleOCRManager

from dotenv import load_dotenv

load_dotenv()


class ModelIterator:
    def __init__(self):
        self.models = {
            "HuyuanOCR": HuyuanOCRManager(),
            "DeepseekOllama": DeepseekOllamaManager(),
            "Mineru2.5": MineruManager(),
            "NanonetsOCR": NanonetsOCRManager(),
            "Qwen2.5VL": Qwen25vlManager(),
            "PaddleOCR": PaddleOCRManager()
        }

        self.current_model = None
    def select_model(self, model_name: str) -> BaseOcrModel:
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found in available models.")
        self.current_model = self.models[model_name]

        return self.current_model


def load_dataset():
    main = os.getcwd().split("testing")[0]
    data_path = os.path.join(main, "data", "test_dataset.csv")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"The dataset file was not found at {data_path}")

    df = pd.read_csv(data_path)

    return df

def make_a_test():
    model_iterator = ModelIterator()
    models_to_test = model_iterator.models.keys()
    test_files = os.listdir("../data/test_dataset_pdfs")
    test_files = [file for file in test_files if file.endswith(".jpg")]
    test_df = load_dataset()
    os.makedirs("../data/test_results", exist_ok=True)

    for model_name in models_to_test:
        print(f"Testing model: {model_name}")
        model = model_iterator.select_model(model_name)
        process_dataset(model, test_files, model_name, test_df)
        model.delete()

def process_dataset(model: BaseOcrModel,
                    test_files: list,
                    model_name: str,
                    test_df: pd.DataFrame):

    if os.path.exists("../data/test_results/" + model_name + "_results.csv"):
        results_df = pd.read_csv("../data/test_results/" + model_name + "_results.csv")
    else:
        results_df = pd.DataFrame(columns=["FILE_NAME", "EXTRACTION_TIME", "OCR_TEXT"])

    if len(results_df) == len(test_df):
        print(f"All files already processed for model: {model_name}")
        return

    print("Starting model...")
    model.start()

    for index, data in tqdm(test_df.iterrows(), total=len(test_df),
                            desc=f"Processing dataset with {model_name}",
                            unit="file"):
        if len(results_df) > index:
            print(f"Skipping already processed file: {data['FILE_NAME']}")
            continue

        file_name = data["FILE_NAME"]
        associated_files = [file for file in test_files if file.startswith(file_name)]
        associated_files = sorted(associated_files)
        if not associated_files:
            print(f"No associated files found for: {file_name}")
            continue

        time_for_files = []
        ocr_text = ""

        for ass_file_name in associated_files:
            file_path = os.path.join("../data/test_dataset_pdfs", ass_file_name)

            start_time = time()
            ocr_text_extraction = model.process(file_path)
            end_time = time()

            extraction_time = end_time - start_time

            time_for_files.append(extraction_time)

            page = ass_file_name.split(file_name + "_")[1].replace(".jpg", "")
            ocr_text += "<" +  page.capitalize() + ">" + "\n"
            ocr_text += ocr_text_extraction + "\n"
            ocr_text += "</" +  page.capitalize() + ">" + "\n"

        results_df.loc[len(results_df)] = {
            "FILE_NAME": data["FILE_NAME"],
            "EXTRACTION_TIME": time_for_files,
            "OCR_TEXT": ocr_text
        }

        results_df.to_csv("../data/test_results/" + model_name + "_results.csv", index=False)


if __name__ == "__main__":
    make_a_test()