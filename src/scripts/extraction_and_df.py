import pandas as pd
import os
from src.scripts.utils.zip_extractor import extract_zip
from src.scripts.utils.bill_parser import create_and_save_dataframe

def extract_and_create_df(main: str) -> pd.DataFrame:
    """
    Extracts zip files from the data/zips directory and creates a dataframe from the extracted files.
    """
    zip_files = os.listdir(os.path.join(main, "data", "zips"))

    os.makedirs(os.path.join(main, "data", "extracted"), exist_ok=True)
    [extract_zip(os.path.join(main, "data", "zips", file), os.path.join(main, "data", "extracted")) for file in zip_files]

    xml_files = os.listdir(os.path.join(main, "data", "extracted"))
    xml_files = [os.path.join(main, "data", "extracted", file) for file in xml_files if file.endswith(".xml")]
    output_path = os.path.join(main, "data", "bills.csv")

    return create_and_save_dataframe(xml_files, output_path)

if __name__ == "__main__":
    import json
    main = os.getcwd().split("src")[0]
    bills = os.listdir(os.path.join(main, "data", "extracted"))
    bills = {"data_extracted": bills}
    with open(os.path.join(main, "data", "bills.json"), "w") as f:
        json.dump(bills, f, indent=4)