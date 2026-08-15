import xml.etree.ElementTree as ET

from src.ingestion.egib.wfs_client import get_features

FILTER_XML = """
<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0">
    <fes:PropertyIsEqualTo>
        <fes:ValueReference>ID_BUDYNKU</fes:ValueReference>
        <fes:Literal>120202_4.0001.1454_BUD</fes:Literal>
    </fes:PropertyIsEqualTo>
</fes:Filter>
"""

def main():
    root = get_features(
        type_name="ms:budynki",
        count=10,
        filter_xml=FILTER_XML
    )

    ET.dump(root)


if __name__ == "__main__":
    main()