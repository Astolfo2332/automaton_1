import pandas as pd

from src.scripts.db.db_schema import DatabaseConfig
from src.scripts.db.migration import create_db_connection

db = DatabaseConfig()

def update_bill(bill:pd.Series):

    bill = bill.to_dict()
    bill["FECHA"] = pd.to_datetime(bill["FECHA"], format="mixed", dayfirst=True).date()
    bill["VALOR_ANTES_DE_IVA"] = bill["VALOR ANTES DE IVA"]
    del bill["VALOR ANTES DE IVA"]

    engine = create_db_connection()
    conn = engine.connect()

    if conn:
        # Update data in the bills table
        try:
            query = db.bills_table.update().where(db.bills_table.c.FILE_NAME == bill["FILE_NAME"]).values(bill)
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(f"Error updating bill: {e}")
        finally:
            conn.close()