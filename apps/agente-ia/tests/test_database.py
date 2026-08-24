from app.database import _normalize_db_url


def test_normalize_db_url_adds_psycopg_dialect():
    url = "postgresql://user:pass@host:5432/db"
    assert _normalize_db_url(url) == "postgresql+psycopg://user:pass@host:5432/db"


def test_normalize_db_url_keeps_psycopg_dialect():
    url = "postgresql+psycopg://user:pass@host:5432/db"
    assert _normalize_db_url(url) == url


def test_normalize_db_url_keeps_sqlite():
    url = "sqlite:///:memory:"
    assert _normalize_db_url(url) == url
