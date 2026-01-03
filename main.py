import os
import pandas as pd
from tqdm import tqdm

from src.scripts.utils.pdf_loader import make_pdf_bytes
from src.scripts.utils.make_queries import fill_dataframe_with_model_response, fill_pdf_only_bills, fill_dataframe_with_model_response_xml
from src.scripts.extraction_and_df import extract_and_create_df
from src.scripts.db.controller.search import search_file
from src.scripts.utils.process_images import image_process
from src.scripts.db.controller.create import sync_all_tables


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
    empty_rows["bytes"] = empty_rows.progress_apply(make_pdf_bytes, axis=1)
    xml_only_files = empty_rows[empty_rows["bytes"].isnull()]
    empty_rows = empty_rows.dropna(subset=["bytes"])

    if not empty_rows.empty:
        print("Starting to fill dataframe with model response")
        bills_df = fill_dataframe_with_model_response(empty_rows, bills_df)
    else:
        print("No empty rows to process")

    if not xml_only_files.empty:
        print("Starting to fill dataframe with model response from xml")
        bills_df = fill_dataframe_with_model_response_xml(xml_only_files, bills_df)
    else:
        print("No xml only files to process")

    #Para los pdf faltantes

    print("Starting to fill pdf only bills")
    all_pdfs = os.listdir(os.path.join(os.getcwd(), "data", "extracted"))
    all_pdfs = [os.path.join(os.getcwd(), "data", "extracted", file) for file in all_pdfs if file.lower().endswith(".pdf")]
    all_pdfs = [file for file in all_pdfs if not search_file(os.path.basename(file))]
    all_pdfs = [file for file in all_pdfs if not search_file(os.path.basename(file).replace(".pdf", ".xml"))]
    if not all_pdfs:
        print("No missing pdfs to process")

    bills_df = fill_pdf_only_bills(all_pdfs, bills_df)

    bills_df = image_process(main_path, bills_df)



if __name__ == "__main__":
    main()