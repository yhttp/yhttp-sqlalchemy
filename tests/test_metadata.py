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

    class Base(DeclarativeBase):
        pass

    class Foo(Base):
        __tablename__ = 'foo'

        id = mapped_column(sa.Integer, primary_key=True)
        title = field_title.column(nullable=False)
        alias = field_alias.column()

    dbmanager.install(app)
    saext.install(app, Base)
    app.ready()
    app.db.create_objects()

    @app.route()
    @app.bodyguard((field_title, field_alias), strict=True)
    @json
    def post(req):
        session = app.db.session
        with session.begin():
            f = Foo(title=req.form['title'], alias=req.form['alias'])
            session.add(f)

        return dict(id=f.id, title=f.title, alias=f.alias)

    with Given(verb='post', form=dict(title='foo', alias='FOO')):
        assert status == 200
        assert response.json == dict(id=1, title='foo', alias='FOO')

        when(form=given - 'title')
        assert status == '400 title: Required'

        when(form=given - 'alias')
        assert status == 200
        assert response.json == dict(id=2, title='foo', alias='OOF')


def test_metadata_args():
    col = m.String('foo', length=(0, 20)).column()
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
