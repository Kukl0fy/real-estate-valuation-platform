import psycopg
from psycopg import sql
from dotenv import load_dotenv
import os
from src.ingestion.egib.wfs_client import get_features, get_features_raw
import xml.etree.ElementTree as ET
import requests
from pathlib import Path
import time

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
RAW_DIR = Path("data/raw/egib")
def get_building_ids():
    query = """
    Select distinct
    split_part(lok_id_lokalu,'_BUD',1) || '_BUD' as building_id from raw.locales
    where lok_id_lokalu is not null;
    """
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    return [row[0] for row in rows]

def build_building_filter(building_ids):
    conditions = []

    for building_id in building_ids:
        condition = f"""
        <fes:PropertyIsEqualTo>
            <fes:ValueReference>ID_BUDYNKU</fes:ValueReference>
            <fes:Literal>{building_id}</fes:Literal>
        </fes:PropertyIsEqualTo>
        """
        conditions.append(condition)

    if len(conditions) == 1:
        body = conditions[0]
    else:
        body = f"""
        <fes:Or>
            {''.join(conditions)}
        </fes:Or>
        """

    return f"""
    <fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0">
        {body}
    </fes:Filter>
    """

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    building_ids = get_building_ids()
    failed_batches = []
    max_retries = 3
    BATCH_SIZE = 10

    for i in range(0, len(building_ids), BATCH_SIZE):
        for attempt in range(1,max_retries + 1):
            try:
                batch = building_ids[i:i + BATCH_SIZE]
                filter_xml = build_building_filter(batch)
                response = get_features_raw(type_name='ms:budynki',count=len(batch),filter_xml=filter_xml)

                file_path = RAW_DIR / f"buildings_{i:06d}.gml"

                with open(file_path,'wb') as file:
                    file.write(response.content)
                    print(f"Downloaded batch starting at {i}")
                    break

            except requests.RequestException as error:
                print(
                    f"Attempt {attempt}/{max_retries} failed "
                    f"for batch {i}: {error}"
                )

                if attempt == max_retries:
                    failed_batches.append(i)
                else:
                    time.sleep(5)

        time.sleep(2)
    print("Failed batches:", failed_batches)

if __name__ == "__main__":
    main()