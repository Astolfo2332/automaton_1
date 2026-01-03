import pandas as pd
from src.scripts.db.migration import create_db_connection
from src.scripts.db.db_schema import DatabaseConfig
from sqlalchemy import select, exists, func

db = DatabaseConfig()

def search_in_table(donde) -> bool:
    engine = create_db_connection()
    conn = engine.connect()

    if conn:
        query = select(exists().where(donde))
        result = conn.execute(query).scalar()
        conn.close()
        if result:
            return True

        return False
    else:
        print("Failed to connect to the database.")
        return False

def search_file(file_name: str) -> bool:
    results = search_in_table(db.bills_table.c.FILE_NAME == file_name)
    return results

def search_bill(bill: str) -> bool:
    results = search_in_table(func.lower(db.bills_table.c.FACTURA) == bill)
    return results

def search_ocr(file_name: str) -> str or None:
    engine = create_db_connection()
    conn = engine.connect()
    if conn:
        query = select(db.ocr_data_table.c.OCR_TEXT).where(db.ocr_data_table.c.FILE_NAME == file_name)
        result = conn.execute(query).fetchall()
        conn.close()
        if result:
            return result[0][0]
        return None
    else:
        print("Failed to connect to the database.")
        return None

if __name__ == "__main__":
    # Example usage
    file_name = """F:\\Documentos\\git\\automaton_1\\data\\extracted\\fv0800153993015251094939452.pdf"""
    bill = 'F-001'.lower()

    if search_file(file_name):
        print(f"File '{file_name}' exists in the database.")
    else:
        print(f"File '{file_name}' does not exist in the database.")

    if search_bill(bill):
        print(f"Bill '{bill}' exists in the database.")
    else:
        print(f"Bill '{bill}' does not exist in the database.")


    file_ocr = "IMG_20250518_003043.jpg"

    if search_ocr(file_ocr):
        print(f"OCR for file '{file_ocr}' exists in the database.")
        print(search_ocr(file_ocr))
    else:
        print(f"OCR for file '{file_ocr}' does not exist in the database.")
