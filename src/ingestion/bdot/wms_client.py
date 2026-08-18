import requests
from uldk_client import find_center_of_counties

WMS_URL = (
    "https://mapy.geoportal.gov.pl/"
    "wss/service/PZGIK/BDOT/WMS/PobieranieBDOT10k"
)

def get_bdot_gpkg_urls(counties):
    counties_urls = {}
    errors = []

    centers, center_errors = find_center_of_counties(counties)
    errors.extend(center_errors)

    for code, (x, y) in centers.items():
        try:
            bbox = (
                y - 1000,
                x - 1000,
                y + 1000,
                x + 1000
            )

            bbox_str = ",".join(map(str, bbox))

            params = {
                "SERVICE": "WMS",
                "VERSION": "1.3.0",
                "REQUEST": "GetFeatureInfo",
                "LAYERS": "Powiaty",
                "QUERY_LAYERS": "Powiaty",
                "CRS": "EPSG:2180",
                "BBOX": bbox_str,
                "WIDTH": 101,
                "HEIGHT": 101,
                "I": 50,
                "J": 50,
                "INFO_FORMAT": "text/plain",
            }

            response = requests.get(
                WMS_URL,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            data = response.text.strip().splitlines()

            url = None

            for line in data:
                if "URL_GPKG" in line:
                    _, value = line.split("=", 1)
                    url = value.strip().strip("'")
                    break

            if url is None:
                raise ValueError("URL_GPKG not found in WMS response")

            counties_urls[code] = url

        except (requests.RequestException, ValueError) as e:
            errors.append(code)
            print(f"Failed to get BDOT GPKG URL for county {code}: {e}")

    print(
        f"Successfully retrieved BDOT GPKG URLs for: "
        f"{list(counties_urls.keys())}"
    )

    if errors:
        print(f"Failed counties: {errors}")

    return counties_urls, errors