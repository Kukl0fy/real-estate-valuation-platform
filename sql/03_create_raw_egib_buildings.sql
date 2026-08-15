CREATE TABLE raw.egib_buildings (
    raw_id BIGSERIAL PRIMARY KEY,

    id_budynku TEXT,
    rodzaj TEXT,
    kondygnacje_nadziemne TEXT,
    kondygnacje_podziemne TEXT,

    polygon_coords TEXT
);