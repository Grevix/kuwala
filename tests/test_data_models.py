import kuwala
from kuwala.data.conventions import year_fraction
from kuwala.data.store import DataStore


def test_conventions_and_year_fraction():
    d1 = "2026-01-01"
    d2 = "2026-07-02"
    yf = year_fraction(d1, d2, "ACT/365")
    assert 0.49 < yf < 0.51


def test_data_store_and_parquet_roundtrip(tmp_path):
    store = DataStore(db_path=tmp_path / "test.duckdb")
    chain = kuwala.data.fetch("SPY", source="yahoo")

    df = chain.to_dataframe()
    assert not df.empty
    rows = store.write_chain(df)
    assert rows > 0

    queried = store.query("SELECT COUNT(*) as cnt FROM options_chains")
    assert queried["cnt"].iloc[0] == rows
    store.close()
