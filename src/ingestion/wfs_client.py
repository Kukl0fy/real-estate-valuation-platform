import requests
import xml.etree.ElementTree as ET


BASE_URL = "https://mapy.geoportal.gov.pl/wss/service/rcn"


def get_features_raw(type_name, count=500, start_index=0, filter_xml=None):
    params = {
        "Service": "WFS",
        "Request": "GetFeature",
        "Version": "2.0.0",
        "TypeNames": type_name,
        "Count": count,
        "StartIndex": start_index
    }

    if filter_xml is not None:
        params["Filter"] = filter_xml

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    if not response.ok:
        print("STATUS:", response.status_code)
        print(response.text)

    response.raise_for_status()

    return response


def get_features(type_name, count=500, start_index=0, filter_xml=None):
    response = get_features_raw(
        type_name=type_name,
        count=count,
        start_index=start_index,
        filter_xml=filter_xml
    )

    return ET.fromstring(response.content)