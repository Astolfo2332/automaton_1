import os
import pandas as pd
from src.scripts.utils.make_queries import fill_pdf_only_bills

def only_vision():
    main = os.getcwd()
    print("Starting to fill pdf only bills only vision")

    bills_df = pd.read_csv(os.path.join(os.getcwd(), "data", "bills.csv"))

    missing_files = os.path.join(main, "data")

    pdf_files = []
    with open(os.path.join(missing_files, "only_vision.txt"), "r") as f:
        lines = f.readlines()
        for line in lines:
            file_name = line.strip()
            file_path = os.path.join(missing_files, "extracted", file_name + ".pdf")
            if not os.path.isfile(file_path):
                print(f"Missing file: {file_name}")
                continue
            pdf_files.append(file_path)


    bills_df = fill_pdf_only_bills(pdf_files, bills_df)

if __name__ == "__main__":
    only_vision()
