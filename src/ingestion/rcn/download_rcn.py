import time
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

from src.ingestion.rcn.wfs_client import get_features_raw
from src.config import COUNTY_CODES


REQUEST_DELAY = 2
RAW_DIR = Path("data/raw/rcn")

BATCH_SIZE = 500
MAX_RETRIES = 3


def build_locales_filter(county_code):
    return f"""
    <fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0">
        <fes:And>

            <fes:PropertyIsEqualTo>
                <fes:ValueReference>lok_funkcja</fes:ValueReference>
                <fes:Literal>mieszkalna</fes:Literal>
            </fes:PropertyIsEqualTo>

            <fes:PropertyIsGreaterThanOrEqualTo>
                <fes:ValueReference>dok_data</fes:ValueReference>
                <fes:Literal>2020-01-01</fes:Literal>
            </fes:PropertyIsGreaterThanOrEqualTo>

            <fes:PropertyIsLike
                wildCard="*"
                singleChar="?"
                escapeChar="!"
            >
                <fes:ValueReference>lok_id_lokalu</fes:ValueReference>
                <fes:Literal>{county_code}*</fes:Literal>
            </fes:PropertyIsLike>

        </fes:And>
    </fes:Filter>
    """


def get_number_returned(response):
    root = ET.fromstring(response.content)

    number_returned = root.attrib.get("numberReturned")

    if number_returned is not None:
        return int(number_returned)

    return sum(
        1
        for element in root.iter()
        if element.tag.endswith("member")
    )


def download_county(county_code, batch_size=BATCH_SIZE):
    filter_xml = build_locales_filter(county_code)

    county_dir = RAW_DIR / county_code
    county_dir.mkdir(parents=True, exist_ok=True)

    start_index = 0
    downloaded_records = 0

    while True:
        response = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = get_features_raw(
                    type_name="ms:lokale",
                    count=batch_size,
                    filter_xml=filter_xml,
                    start_index=start_index,
                )

                break

            except requests.RequestException as error:
                print(
                    f"[{county_code}] "
                    f"Attempt {attempt}/{MAX_RETRIES} failed "
                    f"for batch starting at {start_index}: {error}"
                )

                if attempt < MAX_RETRIES:
                    time.sleep(5)

        if response is None:
            print(
                f"[{county_code}] Download stopped. "
                f"Could not retrieve batch starting at {start_index}."
            )
            return False

        number_returned = get_number_returned(response)

        if number_returned == 0:
            break

        file_path = county_dir / f"locales_{start_index:06d}.gml"

        with open(file_path, "wb") as file:
            file.write(response.content)

        downloaded_records += number_returned

        print(
            f"[{county_code}] Downloaded batch "
            f"{start_index}: {number_returned} records"
        )

        if number_returned < batch_size:
            break

        start_index += batch_size
        time.sleep(REQUEST_DELAY)

    print(
        f"[{county_code}] Finished. "
        f"Downloaded {downloaded_records} records."
    )

    return True


def main():
    failed_counties = []

    for county_code in COUNTY_CODES:
        print(f"\nStarting county {county_code}...")

        success = download_county(county_code)

        if not success:
            failed_counties.append(county_code)

    print("\nDownload completed.")

    if failed_counties:
        print(f"Failed counties: {failed_counties}")
    else:
        print("All counties downloaded successfully.")


if __name__ == "__main__":
    main()