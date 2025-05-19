import os
import pandas as pd
import time
from tqdm import tqdm
import numpy as np

from src.scripts.utils.pdf_loader import make_pdf_bytes
from src.scripts.utils.make_queries import fill_dataframe_with_model_response, fill_pdf_only_bills
from src.scripts.extraction_and_df import extract_and_create_df
from src.scripts.db.controller.search import search_file
from src.scripts.utils.process_images import image_process
from src.scripts.db.controller.create import sync_all_tables

def read_xml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def main():
    sync_all_tables()
    tqdm.pandas()
    main_path = os.getcwd().replace("\\", "/")

    if os.path.exists(os.path.join(os.getcwd(), "data", "bills.csv")):
        bills_df = pd.read_csv(os.path.join(os.getcwd(), "data", "bills.csv"))
    else:
        bills_df = extract_and_create_df(os.getcwd())

    empty_rows = bills_df[bills_df[["VALOR ANTES DE IVA", "IVA", "TOTAL"]].isnull().all(axis=1)]

    print("Starting to convert pdf to bytes")
    empty_rows["bytes"] = empty_rows.progress_apply(lambda row: make_pdf_bytes(row), axis=1)
    empty_rows = empty_rows.dropna(subset=["bytes"])

    if not empty_rows.empty:
        print("Starting to fill dataframe with model response")
        bills_df = fill_dataframe_with_model_response(empty_rows, bills_df)


    #Para los pdf faltantes

    print("Starting to fill pdf only bills")
    all_pdfs = os.listdir(os.path.join(os.getcwd(), "data", "extracted"))
    all_pdfs = [os.path.join(os.getcwd(), "data", "extracted", file) for file in all_pdfs if file.lower().endswith(".pdf")]
    all_pdfs = [file for file in all_pdfs if not search_file(os.path.basename(file))]

    bills_df = fill_pdf_only_bills(all_pdfs, bills_df)

    bills_df = image_process(main_path, bills_df)



if __name__ == "__main__":
    main()