import functools

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, close_all_sessions, Session
from yhttp.core import HTTPStatus


class DatabaseManager:
    def __init__(self, app, basemodel):
        self.app = app
        self.engine = None
        self.sessionfactory = sessionmaker()
        self.basemodel = basemodel

    def __enter__(self) -> sessionmaker:
        if self.engine is None:
            if 'db' not in self.app.settings:
                raise ValueError(
                    'Please provide db.url configuration entry, for example: '
                    'postgresql://:@/dbname'
                )

            self.engine = create_engine(
                self.app.settings.db.url,
                isolation_level='REPEATABLE READ'
            )

        self.sessionfactory.configure(bind=self.engine)
        return self.sessionfactory

    def __exit__(self, exc_type, exc_value, traceback):
        close_all_sessions()
        self.engine.dispose()

    def create_objects(self):
        return self.basemodel.metadata.create_all(self.engine)

    def session(self) -> Session:
        return self.sessionfactory.begin()

    def __call__(self, handler):
        @functools.wraps(handler)
        def outter(req, *a, **kw):
            with self.session() as session:
                req.dbsession = session
                try:
                    return handler(req, *a, **kw)
                except HTTPStatus as ex:
                    if ex.keepheaders:
                        return ex

                    raise
                finally:
                    del req.dbsession

        return outter
