import time
from pathlib import Path

import requests

from src.ingestion.rcn.wfs_client import get_features_raw


REQUEST_DELAY = 2
RAW_DIR = Path("data/raw/rcn")

COUNTIES = {
    "tarnow": "1263",
    "tarnowski": "1216",
    "dabrowski": "1204",
    "brzeski": "1202",
    "debicki": "1803",
}


FILTER_XML = """
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

        <fes:Or>

            <fes:PropertyIsLike wildCard="*" singleChar="?" escapeChar="!">
                <fes:ValueReference>lok_id_lokalu</fes:ValueReference>
                <fes:Literal>1263*</fes:Literal>
            </fes:PropertyIsLike>

            <fes:PropertyIsLike wildCard="*" singleChar="?" escapeChar="!">
                <fes:ValueReference>lok_id_lokalu</fes:ValueReference>
                <fes:Literal>1216*</fes:Literal>
            </fes:PropertyIsLike>

            <fes:PropertyIsLike wildCard="*" singleChar="?" escapeChar="!">
                <fes:ValueReference>lok_id_lokalu</fes:ValueReference>
                <fes:Literal>1204*</fes:Literal>
            </fes:PropertyIsLike>

            <fes:PropertyIsLike wildCard="*" singleChar="?" escapeChar="!">
                <fes:ValueReference>lok_id_lokalu</fes:ValueReference>
                <fes:Literal>1202*</fes:Literal>
            </fes:PropertyIsLike>

            <fes:PropertyIsLike wildCard="*" singleChar="?" escapeChar="!">
                <fes:ValueReference>lok_id_lokalu</fes:ValueReference>
                <fes:Literal>1803*</fes:Literal>
            </fes:PropertyIsLike>

        </fes:Or>

    </fes:And>
</fes:Filter>
"""


def download(filter_xml, batch_size, n):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    failed_batches = []
    max_retries = 3

    for i in range(0, n, batch_size):

        for attempt in range(1, max_retries + 1):
            try:
                response = get_features_raw(
                    type_name="ms:lokale",
                    count=batch_size,
                    filter_xml=filter_xml,
                    start_index=i
                )

                file_path = f"data/raw/rcn/locales_{i:06d}.gml"

                with open(file_path, "wb") as file:
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

        time.sleep(REQUEST_DELAY)

    print("Failed batches:", failed_batches)


def main():
    # 6855 matching elements in ms:lokale
    download(
        filter_xml=FILTER_XML,
        batch_size=500,
        n=6855
    )


if __name__ == "__main__":
    main()