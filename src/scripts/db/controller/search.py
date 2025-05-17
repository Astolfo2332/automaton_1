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
    results = search_in_table(db.already_analice_table.c.FILE_NAMES == file_name)
    return results

def search_bill(bill: str) -> bool:
    results = search_in_table(func.lower(db.bills_table.c.FACTURA) == bill)
    return results

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