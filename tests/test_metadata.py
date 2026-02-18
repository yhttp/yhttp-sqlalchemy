import sqlalchemy as sa
from sqlalchemy.orm import MappedColumn
from sqlalchemy.orm import DeclarativeBase, mapped_column
from bddrest import status, response, when, given

from yhttp.core import json
from yhttp.ext import sqlalchemy as saext, dbmanager
from yhttp.ext.sqlalchemy import metadata as m


def test_metadata(Given, freshdb, app):
    field_title = m.String('title', length=(1, 3))
    field_alias = m.String('alias', optional=True, default='OOF')
    field_featured = m.Boolean('featured', default=False)

    class Base(DeclarativeBase):
        pass

    class Foo(Base):
        __tablename__ = 'foo'

        id = mapped_column(sa.Integer, primary_key=True)
        title = field_title.column(nullable=False)
        alias = field_alias.column()
        featured = field_featured.column()

    dbmanager.install(app)
    saext.install(app, Base)
    app.ready()
    app.db.create_objects()

    @app.route()
    @app.bodyguard((field_title, field_alias, field_featured), strict=True)
    @json
    def post(req):
        session = app.db.session
        with session.begin():
            f = Foo(title=req.form['title'], alias=req.form['alias'],
                    featured=req.form['featured'])
            session.add(f)

        return dict(id=f.id, title=f.title, alias=f.alias, featured=f.featured)

    with Given(verb='post', form=dict(title='foo', alias='FOO',
                                      featured=True)):
        assert status == 200
        assert response.json == dict(id=1, title='foo', alias='FOO',
                                     featured=True)

        when(form=given - 'title')
        assert status == '400 title: Required'

        when(form=given - ['alias', 'featured'])
        assert status == 200
        assert response.json == dict(id=2, title='foo', alias='OOF',
                                     featured=False)


def test_metadata_example():
    field = m.String('foo', length=(0, 20), example='123')
    assert field.example == '123'


def test_metadata_column():
    col = m.String('foo', length=(0, 20), example='123').column()
    assert isinstance(col, MappedColumn)
    assert isinstance(col.column.type, sa.String)
    assert col.column.type.length == 20

    col = m.String('foo').column()
    assert isinstance(col, MappedColumn)
    assert isinstance(col.column.type, sa.String)
    assert col.column.type.length is None

    col = m.Integer('foo').column()
    assert isinstance(col, MappedColumn)
    assert isinstance(col.column.type, sa.Integer)

    col = m.Boolean('foo').column()
    assert isinstance(col, MappedColumn)
    assert isinstance(col.column.type, sa.Boolean)


def test_metadata_override():
    foo = m.String('foo', length=(0, 20), example='123')
    bar = foo(name='bar')
    assert bar.name == 'bar'
    assert bar.length == (0, 20)
    assert bar.example == '123'

    bar = foo(name='bar', length=(1, 10))
    assert bar.name == 'bar'
    assert bar.length == (1, 10)
    assert bar.example == '123'

    bar = bar(example='321')
    assert bar.name == 'bar'
    assert bar.length == (1, 10)
    assert bar.example == '321'
