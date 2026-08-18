import psycopg
from psycopg import sql
from dotenv import load_dotenv
import os
import xml.etree.ElementTree as ET
from src.parsing.rcn_parser import to_dict
from pathlib import Path
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
RAW_DIR = Path('data/raw/rcn')

def insert_raw_records(records, table_name):
    if not records:
        return

    columns = list(records[0].keys())

    query = sql.SQL("""
    INSERT INTO {table} ({columns})
    VALUES ({values})
    ON CONFLICT DO NOTHING
    """).format(
    table=sql.Identifier(*table_name.split(".")),
    columns=sql.SQL(", ").join(
        map(sql.Identifier, columns)
    ),
    values=sql.SQL(", ").join(
        map(sql.Placeholder, columns)
    )
    )

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.executemany(query, records)
def load_gml_file(path):
    root = ET.parse(path).getroot()
    records = to_dict(root)
    return records

def main():
    for path in sorted(RAW_DIR.glob("*/locales_*.gml")):
        records = load_gml_file(path)

        insert_raw_records(
            records=records,
            table_name="raw.locales"
        )

        print(f"Loaded {path.name}: {len(records)} records")

if __name__ == "__main__":
    main()