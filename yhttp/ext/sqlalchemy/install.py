from .cli import DatabaseCLI
from . import orm
from .decorator import dbsession


def install(app, basemodel, db=None, cliarguments=None, create_objects=False):
    app.cliarguments.append(DatabaseCLI)
    if cliarguments:
        DatabaseCLI.__arguments__.extend(cliarguments)

    if db is not None:
        app.db = db

    @app.when
    def ready(app):
        if hasattr(app, 'db') and (app.db is not None):
            return

        if 'db' not in app.settings:
            raise ValueError(
                'Please provide db.url configuration entry, for example: '
                'postgresql://:@/dbname'
            )

        app.db = orm.initialize(
            app.settings.db.url,
            basemodel,
            create_objects=create_objects
        )

    @app.when
    def shutdown(app):
        orm.deinitialize(app.db)

    return dbsession
