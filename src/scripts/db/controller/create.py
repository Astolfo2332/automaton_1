import pandas as pd
from sqlalchemy import text
from src.scripts.db.migration import create_db_connection
from src.scripts.db.db_schema import DatabaseConfig

db = DatabaseConfig()

def add_a_bill(bill:pd.Series) -> bool:
    try:
        bill["FECHA"] = pd.to_datetime(bill["FECHA"], format="mixed", dayfirst=True).date()
    except Exception as e:
        print(f"Error converting date: {e}")
        return False
    bill["VALOR_ANTES_DE_IVA"] = bill["VALOR ANTES DE IVA"]
    del bill["VALOR ANTES DE IVA"]
    bill = bill.to_dict()

    engine = create_db_connection()
    conn = engine.connect()

    if conn:
        # Insert data into the bills table
        try:
            query = db.bills_table.insert().values(bill)
            conn.execute(query)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding bill: {e}")
            return False
        finally:
            conn.close()
    return False

def add_a_file(file:str) -> None:
    engine = create_db_connection()
    conn = engine.connect()

    if conn:
        # Insert data into the bills table
        try:
            query = db.already_analice_table.insert().values({"FILE_NAMES": file})
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(f"Error adding file: {e}")
        finally:
            conn.close()

def add_a_ocr(file:str, ocr:str) -> None:
    engine = create_db_connection()
    conn = engine.connect()

    if conn:
        # Insert data into the bills table
        try:
            query = db.ocr_data_table.insert().values({"FILE_NAME": file, "OCR_TEXT": ocr})
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(f"Error adding file: {e}")
        finally:
            conn.close()


def sync_all_tables() -> None:
    engine = create_db_connection()
    conn = engine.connect()
    tables = ["bills", "already_analice", "ocr_data"]
    if conn:
        for table in tables:
            conn.execute(text(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE((SELECT MAX(id) FROM {table}), 1),
                            true
                        );
                    """))
        conn.commit()
        print("All tables synchronized successfully.")
    else:
        print("Failed to connect to the database.")
