def strip_namespace(tag):
    return tag.split("}")[-1]

def to_dict(root):
    records = []

    for child in root:
        key = strip_namespace(child.tag)
        record = {}
        if key == 'member':
            building = list(child)[0]
            for field in building:
                bld_key = strip_namespace(field.tag)

                if bld_key =='boundedBy':
                    continue

                if bld_key == 'geom':
                    for geom_element in field.iter():
                        if strip_namespace(geom_element.tag) == 'posList':
                            values = geom_element.text.split()
                            record["polygon_coords"] = values
                    continue

                record[bld_key.lower()] = field.text
            records.append(record)
    return records

