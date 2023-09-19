from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self, engine):
        self.engine = engine
        self.sessionfactory = sessionmaker(engine)

    def dispose(self):
        # TODO: dispose sessionfactory
        self.engine.dispose()


def initialize(url, basemodel, create_objects=False):
    engine = create_engine(
        url,
        isolation_level='REPEATABLE READ'
    )

    if create_objects:
        basemodel.metadata.create_all(engine)

    return Database(engine)


def deinitialize(db):
    db.dispose()
