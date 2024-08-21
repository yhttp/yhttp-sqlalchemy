import pytest
from bddrest import status, response, when
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select, String

from yhttp.core import json, statuses

from yhttp.ext import sqlalchemy as saext, dbmanager


def test_extension(Given, freshdb, app):
    class Base(DeclarativeBase):
        pass

    class Foo(Base):
        __tablename__ = 'foo'

        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str] = mapped_column(String(30))

    dbmanager.install(app)
    saext.install(app, Base)
    app.ready()
    app.db.create_objects()

    with app.db.session() as session:
        foo = Foo(title='foo 1')
        session.add(foo)
        session.commit()
        session.reset()

    with app.db.copy(freshdb) as d, d.session() as session:
        bar = Foo(title='foo 2')
        session.add(bar)
        session.commit()
        session.reset()

    @app.route()
    @json
    @app.db
    def get(req):
        with app.db.session() as session:
            result = session.scalars(select(Foo)).all()
        return {f.id: f.title for f in result}

    @app.route()
    @json
    @app.db
    def got(req):
        Foo(title='foo')
        raise statuses.created()

    @app.route()
    @json
    @app.db
    def err(req):
        Foo(title='qux')
        raise statuses.badrequest()

    def getfoo(title):
        with app.db.session() as session:
            result = session.scalars(
                select(Foo).where(Foo.title == title)
            ).first()
            return result

    with Given():
        assert status == 200
        assert response.json == {'1': 'foo 1', '2': 'foo 2'}

        when(verb='err')
        assert status == 400
        qux = getfoo('qux')
        assert qux is None

        when(verb='got')
        assert status == 201

        foo = getfoo('foo 1')
        assert foo is not None


def test_exceptions(app, freshdb):
    class Base(DeclarativeBase):
        pass

    saext.install(app, Base)

    if 'db' in app.settings:
        del app.settings['db']

    with pytest.raises(ValueError):
        app.ready()

    app.settings.merge(f'''
      db:
        url: {freshdb}
    ''')

    app.ready()
