import requests
import xml.etree.ElementTree as ET


BASE_URL = "https://mapy.geoportal.gov.pl/wss/service/rcn"

filter_xml = """
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

COUNTIES = {
    "tarnow": "1263",
    "tarnowski": "1216",
    "dabrowski": "1204",
    "brzeski": "1202",
    "debicki": "1803",
}

def get_capabilities():
    """
    Fetches metadata describing the RCN WFS service.
    """

    params = {
        "Service": "WFS",
        "Request": "GetCapabilities"
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    return ET.fromstring(response.text)


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

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    return ET.fromstring(response.text)


def get_features(type_name, count=5, filter_xml=None, result_type="results"):
    params = {
        "Service": "WFS",
        "Request": "GetFeature",
        "Version": "2.0.0",
        "TypeNames": type_name,
        "ResultType": result_type
    }

    if result_type == "results":
        params["Count"] = count

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

    return ET.fromstring(response.text)

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
    root = get_features(
    type_name="ms:lokale",
    filter_xml=filter_xml,
    result_type="hits"
    )

    print(root.attrib["numberMatched"])


if __name__ == "__main__":
    main()