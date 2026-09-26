import pytest

from yhttp.ext.sqlalchemy.orm import ORM


def _engine_url(monkeypatch, url):
    seen = {}

    def fake_create_engine(target, **kwargs):
        seen['url'] = target
        seen['kwargs'] = kwargs

        class Engine:
            def dispose(self):
                return None

        return Engine()

    monkeypatch.setattr(
        'yhttp.ext.sqlalchemy.orm.create_engine',
        fake_create_engine,
    )
    orm = ORM(object())
    orm.connect(url)
    try:
        return seen
    finally:
        orm.disconnect()


@pytest.mark.parametrize('url', (
    'postgresql://user:pass@localhost:5432/dbname?sslmode=require',
    'postgres://user:pass@localhost:5432/dbname?sslmode=require',
))
def test_driverless_postgresql_uses_psycopg2(monkeypatch, url):
    seen = _engine_url(monkeypatch, url)
    parsed = seen['url']

    assert parsed.drivername == 'postgresql+psycopg2'


@pytest.mark.parametrize('url', (
    'postgresql+psycopg2://user:pass@localhost/dbname',
    'postgresql+psycopg://user:pass@localhost/dbname',
    'postgresql+asyncpg://user:pass@localhost/dbname',
))
def test_explicit_postgresql_driver_unchanged(monkeypatch, url):
    seen = _engine_url(monkeypatch, url)

    assert seen['url'].drivername == url.split(':', 1)[0]
    assert seen['url'].username == 'user'
    assert seen['url'].database == 'dbname'
