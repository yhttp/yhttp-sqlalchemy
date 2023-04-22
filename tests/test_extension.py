import pytest
from bddrest import status, response, when
from yhttp import json, statuses



def test_extension(app, Given, freshdb):

    class Foo(app.db.Base):
        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str] = mapped_column(String(30))

    app.ready()

    @dbsession
    def mockup():
        Foo(title='foo 1')
        Foo(title='foo 2')

    mockup()

    @app.route()
    @json
    @dbsession
    def get(req):
        return {f.id: f.title for f in Foo.select()}

    @app.route()
    @json
    @dbsession
    def got(req):
        Foo(title='foo')
        raise statuses.created()

    @app.route()
    @json
    @dbsession
    def err(req):
        Foo(title='qux')
        raise statuses.badrequest()

    @dbsession
    def getfoo(title):
        return Foo.get(title=title)

    with Given():
        assert status == 200
        assert response.json == {'1': 'foo 1', '2': 'foo 2'}

        when(verb='err')
        assert status == 400
        qux = getfoo('qux')
        assert qux is None

        when(verb='got')
        assert status == 201

        foo = getfoo('foo')
        assert foo is not None

    app.shutdown()


# def test_exceptions(app):
#     dbsession = install(app)  # noqa: F841
#
#     if 'db' in app.settings:
#         del app.settings['db']
#
#     with pytest.raises(ValueError):
#         app.ready()
