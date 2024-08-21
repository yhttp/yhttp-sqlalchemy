import functools

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, close_all_sessions, Session, \
    scoped_session
from yhttp.core import HTTPStatus


class ORM:
    def __init__(self, basemodel, url=None):
        self.url = url
        self.engine = None
        self.basemodel = basemodel
        self.session = scoped_session(sessionmaker())

    def copy(self, url=None):
        return ORM(self.basemodel, url=url or self.app.settings.db.url)

    def create_objects(self):
        return self.basemodel.metadata.create_all(self.engine)

    def connect(self, url=None):
        u = url or self.url
        assert self.engine is None
        assert u is not None

        self.engine = create_engine(u, isolation_level='REPEATABLE READ')
        self.session.configure(bind=self.engine)

    def disconnect(self):
        close_all_sessions()
        self.engine.dispose()
        self.engine = None

    def __enter__(self) -> Session:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()


class ApplicationORM(ORM):
    def __init__(self, basemodel, app):
        self.app = app
        super().__init__(basemodel)

    def connect(self, url=None):
        if 'db' not in self.app.settings or 'url' not in self.app.settings.db:
            raise ValueError(
                'Please provide db.url configuration entry, for example: '
                'postgresql://:@/dbname'
            )

        return super().connect(url=url or self.app.settings.db.url)

    def __call__(self, handler):
        @functools.wraps(handler)
        def outter(*a, **kw):
            try:
                return handler(*a, **kw)
            except HTTPStatus as ex:
                if ex.keepheaders:
                    return ex

                raise
            finally:
                self.session.reset()

        return outter
