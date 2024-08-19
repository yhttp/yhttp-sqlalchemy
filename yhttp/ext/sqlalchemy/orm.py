import functools

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from yhttp.core import HTTPStatus


class Manager:
    def __init__(self, app, basemodel):
        self.app = app
        self.engine = None
        self.sessionfactory = sessionmaker()
        self.basemodel = basemodel

    def initialize(self):
        if self.engine is not None:
            raise ValueError('ORM already initialized')

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

    def deinitialize(self):
        # TODO: dispose sessionfactory
        self.engine.dispose()

    def create_objects(self):
        return self.basemodel.metadata.create_all(self.engine)

    def begin(self):
        return self.sessionfactory.begin()

    def session(self, handler):
        @functools.wraps(handler)
        def outter(req, *a, **kw):
            with self.begin() as session:
                req.dbsession = session
                try:
                    return handler(req, *a, **kw)
                except HTTPStatus as ex:
                    if ex.keepheaders:
                        return ex

                    raise

        return outter
