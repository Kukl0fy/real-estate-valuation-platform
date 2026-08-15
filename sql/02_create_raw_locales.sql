CREATE TABLE IF NOT EXISTS raw.locales (
    raw_id BIGSERIAL PRIMARY KEY,

    x TEXT,
    y TEXT,

    serwis_rcn TEXT,
    teryt TEXT,

    tran_przestrzen_nazw TEXT,
    tran_lokalny_id_iip TEXT,
    tran_wersja_id TEXT,
    tran_rodzaj_trans TEXT,
    tran_rodzaj_rynku TEXT,
    tran_sprzedajacy TEXT,
    tran_kupujacy TEXT,
    tran_cena_brutto TEXT,
    tran_vat TEXT,

    dok_data TEXT,

    nier_rodzaj TEXT,
    nier_prawo TEXT,
    nier_udzial TEXT,
    nier_pow_gruntu TEXT,
    nier_cena_brutto TEXT,
    nier_vat TEXT,

    lok_id_lokalu TEXT,
    lok_nr_lokalu TEXT,
    lok_funkcja TEXT,
    lok_liczba_izb TEXT,
    lok_nr_kond TEXT,
    lok_pow_uzyt TEXT,
    lok_pow_przyn TEXT,
    lok_cena_brutto TEXT,
    lok_vat TEXT,
    lok_adres TEXT
);