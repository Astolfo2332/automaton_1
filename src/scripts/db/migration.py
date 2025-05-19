import os
import json
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from src.scripts.db.db_schema import DatabaseConfig

database = DatabaseConfig()

def create_db_connection():
    db_url = (f"postgresql://{os.getenv('POSTGRES_USER')}:"
              f"{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}"
              f"/{os.getenv('POSTGRES_DB')}")
    try:
        engine = create_engine(db_url)
        return engine
    except SQLAlchemyError as e:
        print(f"Error connecting to the database: {e}")
        return None

def migrate_db():
    engine = create_db_connection()

    conn = engine.connect()

    if conn:
        # Create the bills table
        database.metadata.drop_all(conn)
        database.metadata.create_all(conn)
        # Close the connection
        conn.commit()
        conn.close()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in the database: {tables}")
        print("Database migrated successfully.")
    else:
        print("Failed to connect to the database.")


def migrate_info():
    engine = create_db_connection()

    conn = engine.connect()

    if conn:
        # Read the CSV file
        main = os.getcwd().replace("\\", "/").split("src")[0]
        bills_df = pd.read_csv(os.path.join(main, "data", "bills.csv"))
        bills_df["FECHA"] = pd.to_datetime(bills_df["FECHA"], format="mixed", dayfirst=True).dt.date

        bills_df["VALOR_ANTES_DE_IVA"] = bills_df["VALOR ANTES DE IVA"]
        del bills_df["VALOR ANTES DE IVA"]

        # Insert data into the bills table
        try:
            bills_df.to_sql('bills', conn, if_exists='append', index=False)

            #Fix de errores de secuencia
            conn.execute(text("""
                              SELECT setval('bills_id_seq', COALESCE((SELECT MAX(id) FROM ocr_data), 1));
                              """))
            conn.commit()
            print("Data migrated successfully.")
        except SQLAlchemyError as e:
            print(f"Error migrating data: {e}")

        with open(os.path.join(main, "data", "bills.json"), "r", encoding="utf-8") as f:

            bills = json.load(f)

        bills = bills["data_extracted"]
        bills = [{"FILE_NAMES": bill} for bill in bills]

        try:
            conn.execute(database.already_analice_table.insert(), bills)
            conn.commit()
            print("Data migrated successfully.")
        except SQLAlchemyError as e:
            print(f"Error migrating data: {e}")

        ocr_data = pd.read_excel(os.path.join(main, "data", "ocr_data.xlsx"))

        try:
            ocr_data.to_sql('ocr_data', conn, if_exists='append', index=False)
            conn.execute(text("""
            SELECT setval('ocr_data_id_seq', COALESCE((SELECT MAX(id) FROM ocr_data), 1));
            """))
            print("Data migrated successfully.")
        except SQLAlchemyError as e:
            print(f"Error migrating data: {e}")

        # Close the connection
        conn.close()
    else:
        print("Failed to connect to the database.")

if __name__ == "__main__":
    migrate_db()
    migrate_info()