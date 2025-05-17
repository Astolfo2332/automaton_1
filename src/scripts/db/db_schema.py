from sqlalchemy import  MetaData, Table, Column, Integer, String, Float, Date
from sqlalchemy.dialects.postgresql import VARCHAR

from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.metadata = MetaData()

        self.bills_table = Table(
            'bills',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('FILE_NAME', String(255)),
            Column('VALOR_ANTES_DE_IVA', Float),
            Column('IVA', Float),
            Column('TOTAL', Float),
            Column('PROVEEDOR', String(255)),
            Column('FACTURA', String(255)),
            Column('EXTRACTION', String(255)),
            Column('FILE', VARCHAR(255)),
            Column('CHECK', String(255)),
            Column('FECHA', Date),
            Column('NIT', String(255)),
        )

        self.already_analice_table = Table(
            'already_analice',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('FILE_NAMES', String(500))
        )



