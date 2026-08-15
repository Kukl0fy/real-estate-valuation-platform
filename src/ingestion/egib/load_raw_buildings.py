import xml.etree.ElementTree as ET
from pathlib import Path
from src.parsing.egib_parser import to_dict
from src.ingestion.rcn.load_raw_locales import insert_raw_records
RAW_DIR = Path('data/raw/egib')

def load_gml_file(path):
    root = ET.parse(path).getroot()
    records = to_dict(root)
    return records



def main():
    rec = []
    for path in sorted(RAW_DIR.glob('buildings_*.gml')):
        records = load_gml_file(path)
        rec.extend(records)
    insert_raw_records(rec,'raw.egib_buildings')
 

if __name__ == '__main__':
    main()