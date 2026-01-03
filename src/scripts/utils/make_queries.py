import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv

from scripts.utils.ask_a_model import query_model_one_shot_batch
from src.scripts.utils.ask_a_model import (query_model, query_model_ocr,
query_model_structured, query_model_ocr_ollama,
query_model_structure_xml, query_model_ocr_transformers)
# from src.scripts.utils.ask_a_model import llm_nanonets
from src.scripts.utils.prompts.prompts import *
from src.scripts.utils.pdf_loader import make_pdf_bytes
from src.scripts.utils.bill_parser import get_alpha_numeric_string
from src.scripts.db.controller.update import update_bill
from src.scripts.db.controller.create import add_a_file, add_a_bill
from src.scripts.db.controller.search import search_bill
load_dotenv()


SERVER = os.getenv("SERVER")

def fill_dataframe_with_model_response(df:pd.DataFrame, bills_df:pd.DataFrame) -> pd.DataFrame:

    tqdm.pandas()

    print("Ocr pdfs\n")
    print("-"*50)
    # df["ocr"] = df.progress_apply(lambda x: query_model_ocr(x["bytes"]), axis=1)

    all_bytes = df["bytes"].tolist()

    ocr_responses, _ = query_model_one_shot_batch(all_bytes)

    df["model_ocr"] = ocr_responses

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Filling dataframe with model response", unit="row"):
        # bills_df.loc[idx] = queries_for_model(row)
        bills_df.loc[idx] = queries_for_model_from_ocr(row)
        update_bill(bills_df.loc[idx])
        bills_df.to_csv(os.path.join(os.getcwd(), "data", "bills.csv"), index=False)
        bills_df.to_excel(os.path.join(os.getcwd(), "data", "bills.xlsx"), index=False)

    #Fix de links
    bills_df["FILE"] = bills_df["FILE"].apply(lambda x: f'=HYPERLINK("{x}", "link")' if not x.startswith("=") else x)
    return bills_df

def fill_dataframe_with_model_response_xml(df:pd.DataFrame, bills_df:pd.DataFrame) -> pd.DataFrame:
    tqdm.pandas()

    print("XML\n")
    print("-"*50)

    df["xml_content"] = df.progress_apply(lambda x: read_xml_file(x["FILE_NAME"]), axis=1)

    xml_contents = df["xml_content"].tolist()

    xml_responses, _ = query_model_structure_xml(xml_contents)

    df["model_ocr"] = xml_responses

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Filling dataframe with model response from xml", unit="row"):

        bills_df.loc[idx] = queries_for_model_from_ocr(row)
        update_bill(bills_df.loc[idx])
        bills_df.to_csv(os.path.join(os.getcwd(), "data", "bills.csv"), index=False)
        bills_df.to_excel(os.path.join(os.getcwd(), "data", "bills.xlsx"), index=False)

    return bills_df

def read_xml_file(file_path):
    main = os.getcwd().split("src")[0]
    path = os.path.join(main, "data", "extracted", file_path)

    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def queries_for_model(row:pd.Series) -> pd.Series:
    row["VALOR ANTES DE IVA"] = query_model(row["bytes"], subtotal_prompt)
    row["IVA"] = query_model(row["bytes"], iva_prompt)
    row["TOTAL"] = query_model(row["bytes"], monto_prompt)
    row["PROVEEDOR"] = query_model(row["bytes"], proveedor_prompt)
    row["FACTURA"] = get_alpha_numeric_string(query_model(row["bytes"], numero_factura_prompt))
    row["EXTRACTION"] = "IA+parser"
    del row["bytes"]
    return row

def queries_for_model_from_ocr(row:pd.Series) -> pd.Series:
    # invoice = query_model_structured(row["ocr"])
    invoice = row["model_ocr"]
    row["VALOR ANTES DE IVA"] = invoice.antes_iva
    row["IVA"] = invoice.iva
    row["TOTAL"] = invoice.valor_total
    row["PROVEEDOR"] = invoice.proveedor
    row["FACTURA"] = invoice.numero_factura
    row["EXTRACTION"] = "IA+parser"

    # if "bytes" in row:
    #     del row["bytes"]
    # if "ocr" in row:
    #     del row["ocr"]
    return row

def fill_pdf_only_bills(all_pdfs:list, df:pd.DataFrame) -> pd.DataFrame:
    ocr_pdf = []
    main = os.getcwd().replace("\\", "/")
    for pdf in tqdm(all_pdfs, desc="Passing pdf to bytes", unit="pdf"):
        file = os.path.basename(pdf).split(".")[0]
        row = pd.Series({"FILE_NAME": file})
        if not os.path.exists(pdf):
            continue
        row["bytes"] = make_pdf_bytes(row)
        if row["bytes"] is np.nan:
            continue
        ocr_pdf.append(row)

    all_bytes = [row["bytes"] for row in ocr_pdf]
    if not all_bytes:
        print("No new pdfs to process")
        return df

    print("Getting responses from model")
    responses, _ = query_model_one_shot_batch(all_bytes)

    for i, row in tqdm(enumerate(ocr_pdf), desc="Filling PDF only bills", unit="pdf"):
        row = all_queries_ocr(row, responses[i])

        row["FACTURA"] = get_alpha_numeric_string(row["FACTURA"])
        df.loc[len(df)] = row

        add_a_bill(row)

        df.to_csv(os.path.join(os.getcwd(), "data", "bills.csv"), index=False)
        df.to_excel(os.path.join(os.getcwd(), "data", "bills.xlsx"), index=False)

    return df

def all_queries(row:pd.Series, pdf:str) -> pd.Series:
    row["VALOR ANTES DE IVA"] = query_model(row["bytes"], subtotal_prompt)
    row["IVA"] = query_model(row["bytes"], iva_prompt)
    row["TOTAL"] = query_model(row["bytes"], monto_prompt)
    row["PROVEEDOR"] = query_model(row["bytes"], proveedor_prompt)
    row["FACTURA"] = query_model(row["bytes"], numero_factura_prompt)
    row["FECHA"] = query_model(row["bytes"], fecha_prompt)
    row["NIT"] = query_model(row["bytes"], nit_prompt)
    row["CHECK"] = "NO"
    row["EXTRACTION"] = "IA"
    server_file = SERVER + os.path.basename(pdf)
    row["FILE"] = f'=HYPERLINK("{server_file}", "link")'
    # del row["bytes"]
    del row["ocr"]
    return row

def all_queries_ocr(row:pd.Series, invoice) -> pd.Series:
    row["VALOR ANTES DE IVA"] = invoice.antes_iva
    row["IVA"] = invoice.iva
    row["TOTAL"] = invoice.valor_total
    row["PROVEEDOR"] = invoice.proveedor
    row["FACTURA"] = invoice.numero_factura
    row["FECHA"] = invoice.fecha
    row["NIT"] = invoice.nit
    row["CHECK"] = "NO"
    row["EXTRACTION"] = "IA"
    row["FILE_NAME"] = row["FILE_NAME"] + ".pdf" if not row["FILE_NAME"].endswith(".pdf") else row["FILE_NAME"]
    row["FILE"] = f'=HYPERLINK("{SERVER + row["FILE_NAME"]}", "link")'

    if "ocr" in row.index:
        del row["ocr"]
    if "bytes" in row.index:
        del row["bytes"]
    return row

if __name__ == "__main__":
    #Fix de links
    bills_df = pd.read_csv(os.path.join(os.getcwd().split("src")[0], "data", "bills.csv"))
    bills_df["FILE"] = bills_df.apply(lambda x: f'=HYPERLINK("{SERVER + x["FILE_NAME"]}", "link")' if x["FILE"] is np.nan else x["FILE"], axis=1)
    bills_df["FILE"] = bills_df.apply(lambda x: f'=HYPERLINK("{SERVER + x["FILE_NAME"]}", "link")' if SERVER not in x["FILE"] else x["FILE"], axis=1)
    bills_df["FILE"] = bills_df["FILE"].apply(lambda x: f'=HYPERLINK("{x}", "link")' if not x.startswith("=") else x)
    bills_df["FACTURA"] = bills_df["FACTURA"].apply(lambda x: get_alpha_numeric_string(str(x)))
    bills_df.to_csv(os.path.join(os.getcwd().split("src")[0], "data", "bills.csv"), index=False)
    bills_df.to_excel(os.path.join(os.getcwd().split("src")[0], "data", "bills.xlsx"), index=False)
