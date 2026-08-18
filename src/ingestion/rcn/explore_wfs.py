import requests
import xml.etree.ElementTree as ET

from src.ingestion.rcn.wfs_client import BASE_URL
from parsing.rcn_parser import to_dict

def get_capabilities():
    """
    Fetches metadata describing the RCN WFS service.
    """

    params = {
        "Service": "WFS",
        "Request": "GetCapabilities"
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return ET.fromstring(response.content)


def get_feature_types(root):
    """
    Extracts available WFS feature types from GetCapabilities response.

    Discovered RCN feature types:
    - ms:budynki
    - ms:lokale
    - ms:dzialki
    - ms:powiaty
    """

    feature_types = []

    for elem in root.iter():
        if elem.tag.endswith("FeatureType"):
            feature_types.append(elem)

    return feature_types


def print_feature_types(feature_types):
    """
    Prints metadata for discovered feature types.
    Used mainly during API exploration.
    """

    for feature_type in feature_types:
        for child in feature_type:
            print(child.tag, child.text)

        print()


def describe_feature_type(type_name):
    """
    Fetches the schema of a selected WFS feature type.

    For ms:lokale, the schema showed attributes relevant
    for apartment valuation, including:

    - dok_data
    - tran_rodzaj_rynku
    - tran_cena_brutto
    - lok_funkcja
    - lok_liczba_izb
    - lok_nr_kond
    - lok_pow_uzyt
    - lok_cena_brutto
    - lok_adres
    - teryt
    - msGeometry

    The WFS service exposes these attributes as strings.
    Proper data types will therefore be assigned later
    during data transformation.
    """

    params = {
        "Service": "WFS",
        "Request": "DescribeFeatureType",
        "Version": "2.0.0",
        "TypeNames": type_name
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return ET.fromstring(response.content)


def get_output_formats(root):
    """
    Extracts supported output formats from the WFS GetCapabilities response.

    The RCN service currently exposes GML/XML-based formats only.
    Discovered formats include:

    - application/gml+xml; version=3.2
    - text/xml; subtype=gml/3.2.1
    - text/xml; subtype=gml/3.1.1
    - text/xml; subtype=gml/2.1.2

    The same formats may appear multiple times because they are declared
    separately for different feature types.

    Returns:
        list[str]: Supported output format strings.
    """

    formats = []

    for elem in root.iter():
        if elem.tag.endswith("OutputFormats"):
            for child in elem:
                if child.text:
                    formats.append(child.text)

    return formats

def main():
    root = ET.parse("data/raw/rcn/1263/locales_000000.gml")
    records = to_dict(root)
    print(records[0])

if __name__ == '__main__':
    main()