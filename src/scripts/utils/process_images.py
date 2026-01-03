import os
import pandas as pd
import cv2
from cv2 import Mat
from tqdm import tqdm
from PIL import Image

from src.scripts.utils.make_queries import all_queries_ocr
from src.scripts.utils.ask_a_model import query_model_ocr, query_model_structured, query_model_one_shot_batch
from src.scripts.db.controller.create import add_a_bill, add_a_file, add_a_ocr
from src.scripts.db.controller.search import search_bill, search_file, search_ocr
from src.scripts.utils.pdf_loader import convert_img_to_bytes
from src.scripts.utils.bill_parser import get_alpha_numeric_string

SERVER = os.getenv("SERVER")

def image_process(main:str, bills_df:pd.DataFrame) -> pd.DataFrame:

    data_path = os.path.join(main, "data", "extracted")
    files = os.listdir(data_path)
    img_files = [file for file in files if file.lower().endswith((".jpg", ".jpeg", ".png"))]
    # img_files = [img_files[0]]

    bytes_images = []

    for file in tqdm(img_files, desc="Processing images", unit="file"):
        exists = search_file(os.path.basename(file))

        if exists:
            print(f"File {file} already exists in the database. Skipping.")
            continue

        row = pd.Series()
        file_path = os.path.join(data_path, file)
        img = cv2.imread(file_path)
        tresh = treshold_image(img)
        img = Image.fromarray(tresh)
        img = convert_img_to_bytes([img])

        file_name = os.path.basename(file).split(".")[0]
        server_path = SERVER + os.path.basename(file_path)
        row["bytes"] = img
        row["FILE"] = f'=HYPERLINK("{server_path}", "link")'
        row["FILE_NAME"] = file_name
        bytes_images.append(row)

    all_bytes = [row["bytes"] for row in bytes_images]
    if not all_bytes:
        print("No new images to process")
        return bills_df

    responses, _ = query_model_one_shot_batch(all_bytes)

    for i, row in tqdm(enumerate(bytes_images), desc="Filling image bills", unit="file"):
        row = all_queries_ocr(row, responses[i])
        row["FACTURA"] = get_alpha_numeric_string(row["FACTURA"])
        bills_df.loc[len(bills_df)] = row
        add_a_bill(row)
        bills_df.to_csv(os.path.join(main, "data", "bills.csv"), index=False)
        bills_df.to_excel(os.path.join(main, "data", "bills.xlsx"), index=False)

    return bills_df


def treshold_image(img:Mat) -> Mat:
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced)
    thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    thresh = cv2.bitwise_not(thresh)

    return thresh