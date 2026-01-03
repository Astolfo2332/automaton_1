import xml.etree.ElementTree as ET
import pandas as pd
import datetime
import numpy as np
from dotenv import load_dotenv
import os
import re

from scripts.db.controller.search import search_file
from src.scripts.db.controller.create import add_a_file, add_a_bill
from src.scripts.db.controller.search import search_bill
load_dotenv()

SERVER = os.getenv("SERVER")

def get_alpha_numeric_string(s: str) -> str:
    data = re.sub(r'[^a-zA-Z0-9]', '', s)
    return data

def parse_xml_to_dataframe(xml_path: str, bills_df:pd.DataFrame) -> None:

    file = SERVER + os.path.basename(xml_path)
    file = file.replace("\\", "/").replace(".xml", ".pdf")

    print(f"Processing file: {xml_path}")
    root = ET.parse(xml_path).getroot()
    namespaces = {
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsd': "http://www.w3.org/2001/XMLSchema",
        'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        'sts': "dian:gov:co:facturaelectronica:Structures-2-1",
        'xades': "http://uri.etsi.org/01903/v1.3.2#",
        'xades141': "http://uri.etsi.org/01903/v1.4.1#",
        'ext': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        'ds': "http://www.w3.org/2000/09/xmldsig#",
        'inv': "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    }

    # Find and extract the PayableAmount value
    payable_amount = get_value('.//cbc:PayableAmount', namespaces, root, to_type=float)

    iva = get_value('.//cbc:TaxAmount', namespaces, root, to_type=float)

    antes_iva = get_value('.//cbc:TaxExclusiveAmount', namespaces, root, to_type=float)

    fecha = get_value('.//xades:SigningTime', namespaces, root, to_type=str, time=True)

    proveedor = get_value('.//cbc:Name', namespaces, root, to_type=str)

    nit = get_value('.//cbc:CompanyID', namespaces, root, to_type=str)

    factura = get_value('.//cbc:ID', namespaces, root, to_type=str)
    factura = get_alpha_numeric_string(factura)

    #Check que la factura no sea un duplicado
    if not search_file(os.path.basename(xml_path)):
        bills_df.loc[len(bills_df)] = [fecha, proveedor, nit, factura, antes_iva,
                                       iva, payable_amount, file, "parser",
                                       os.path.basename(xml_path),"NO"]

def get_value(xpath, namespaces, root, to_type=str, default=np.nan, time=False):
    element = root.find(xpath, namespaces)
    if element is not None and element.text:
        try:
            if time:
                date = element.text.split("T")[0]
                date = datetime.datetime.fromisoformat(date)
                return date.strftime("%#d/%m/%Y")
            return to_type(element.text)
        except (ValueError, TypeError):
            return default
    return default

def create_and_save_dataframe(xml_files: list, output_path: str) -> pd.DataFrame:
    bills_df = pd.DataFrame(columns=["FECHA", "PROVEEDOR", "NIT", "FACTURA",
                                     "VALOR ANTES DE IVA", "IVA", "TOTAL", "FILE", "EXTRACTION", "FILE_NAME", "CHECK"])

    [parse_xml_to_dataframe(xml_file, bills_df) for xml_file in xml_files]

    # Save the DataFrame to a CSV file
    bills_df.to_csv(output_path, index=False)
    bills_df["FILE"] = bills_df["FILE"].apply(lambda x: f'=HYPERLINK("{x}", "link")')
    bills_df.to_excel(output_path.replace(".csv", ".xlsx"), index=False)
    bills_df.apply(lambda x: add_a_bill(x), axis=1)
    # bills_df.apply(lambda x: add_a_file(x["FILE_NAME"] + ".xml"), axis=1)
    print(f"DataFrame saved to {output_path}")

    return bills_df

if __name__ == "__main__":
    main = os.getcwd().split("src")[0]
    xml_files = os.listdir(os.path.join(main, "data", "extracted"))
    xml_files = [os.path.join(main, "data", "extracted", file) for file in xml_files if file.endswith(".xml")]

    output_path = os.path.join(main, "data", "bills.csv")
    create_and_save_dataframe(xml_files, output_path)