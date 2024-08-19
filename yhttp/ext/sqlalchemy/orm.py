from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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

    def session(self, handler):
        @functools.wraps(handler)
        def outter(req, *a, **kw):
            app = req.application
            try:
                req.dbsession = app.db.sessionfactory()
            except AttributeError:
                print(
                    'Please install yhttp-sqlalchemy extention first.',
                    file=sys.stderr
                )
                raise

            with req.dbsession as session, session.begin():
                try:
                    return func(req, *a, **kw)
                except y.HTTPStatus as ex:
                    if ex.keepheaders:
                        return ex

                    raise

        return outter
