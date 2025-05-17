import pandas as pd
from src.scripts.db.migration import create_db_connection
from src.scripts.db.db_schema import DatabaseConfig

db = DatabaseConfig()

def add_a_bill(bill:pd.Series) -> bool:
    bill["FECHA"] = pd.to_datetime(bill["FECHA"], format="mixed", dayfirst=True).date()
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