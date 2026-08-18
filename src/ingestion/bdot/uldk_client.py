import requests
ULDK_URL = "https://uldk.gugik.gov.pl/"

def find_center_of_counties(counties):
    results = {}
    errors = []

    for county in counties:
        try:
            params = {
                "request": "GetCountyById",
                "id": county,
                "result": "id,geom_extent,county",
                "srid": 2180,
            }

            response = (
                requests.get(url=ULDK_URL, params=params)
                .text
                .strip()
                .splitlines()
            )

            if response[0] != "0":
                raise ValueError("ULDK returned an error")

            data = response[1]

            code, extent, _ = data.split("|")

            minx, miny, maxx, maxy = map(float, extent.split(","))

            center_x = (minx + maxx) / 2
            center_y = (miny + maxy) / 2

            results[code] = (center_x, center_y)

        except Exception:
            errors.append(county)

    if errors:
        print(f"Failed to get county centers for: {errors}")

    print(f"Successfully retrieved county centers for: {list(results.keys())}")

    return results, errors