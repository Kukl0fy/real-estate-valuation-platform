def strip_namespace(tag):
    return tag.split("}")[-1]


def to_dict(root):
    records = []

    for child in root:
        key = strip_namespace(child.tag)

        if key == "member":
            locale = list(child)[0]
            record = {}

            for field in locale:
                loc_key = strip_namespace(field.tag)

                if loc_key == "boundedBy":
                    continue

                if loc_key == "msGeometry":
                    for geom_element in field.iter():
                        if strip_namespace(geom_element.tag) == "pos":
                            x, y = geom_element.text.split()
                            record["x"] = x
                            record["y"] = y

                    continue

                record[loc_key] = field.text

            records.append(record)

    return records