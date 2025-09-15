import os
import pandas as pd
import numpy as np

from src.scripts.utils.pdf_loader import make_pdf_bytes
from src.scripts.utils.ask_a_model import query_model_ocr_transformers, llm_nanonets

def main():

    # main_path = os.getcwd().split("src")[0]
    # os.chdir(main_path)

    pdf_file  = "0ab3ad91a7274a6057a9d5c60b62eba2a51b541ce3c08af35517012a3f44eb8bc58d204f819c456fb0e60cb116767d8d"
    row_dummy = pd.Series({
        "FILE_NAME": pdf_file
    })
    image = make_pdf_bytes(row_dummy)
    if image is np.nan:
        print("Error cargando el PDF")
        return
    response = query_model_ocr_transformers(image)


if __name__ == "__main__":
    main()