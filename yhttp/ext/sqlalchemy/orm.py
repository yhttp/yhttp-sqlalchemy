from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, close_all_sessions, Session, \
    scoped_session


class ORM:
    def __init__(self, basemodel, url=None, saplugins=None):
        self.url = url
        self.engine = None
        self.basemodel = basemodel
        self.session = scoped_session(sessionmaker())
        self.saplugins = saplugins

    def copy(self, url=None):
        return ORM(self.basemodel, url=url or self.app.settings.db.url)

    def create_objects(self):
        return self.basemodel.metadata.create_all(self.engine)

    def connect(self, url=None):
        u = url or self.url
        assert self.engine is None
        assert u is not None

        parsed = make_url(u)
        if parsed.drivername in ('postgresql', 'postgres'):
            # SQLAlchemy 2.1 loads psycopg 3 for a driverless URL.
            # https://docs.sqlalchemy.org/en/21/changelog/migration_21.html#default-postgresql-driver-changed-to-psycopg-psycopg-3  # noqa: E501
            parsed = parsed.set(drivername='postgresql+psycopg2')

        self.engine = create_engine(
            parsed,
            isolation_level='REPEATABLE READ',
            plugins=self.saplugins or [],
        )
        self.session.configure(bind=self.engine)

    def disconnect(self):
        close_all_sessions()
        self.session.expunge_all()
        self.session.remove()
        self.engine.dispose()
        self.engine = None

    def __enter__(self) -> Session:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()


class ApplicationORM(ORM):
    def __init__(self, basemodel, app, **kw):
        self.app = app
        super().__init__(basemodel, **kw)

    def connect(self, url=None):
        if 'db' not in self.app.settings or 'url' not in self.app.settings.db:
            raise ValueError(
                'Please provide db.url configuration entry, for example: '
                'postgresql://:@/dbname'
            )

        return super().connect(url=url or self.app.settings.db.url)
