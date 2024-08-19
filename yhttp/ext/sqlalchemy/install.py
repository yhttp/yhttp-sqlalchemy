from yhttp.ext.dbmanager import DatabaseCommand

from . import orm, cli


def install(app, basemodel, db=None, cliarguments=None):
    DatabaseCommand.__arguments__.append(cli.DatabaseObjectsCommand)
    if cliarguments:
        cli.DatabaseObjectsCommand.__arguments__.extend(cliarguments)

    if db is None:
        db = orm.DatabaseManager(app, basemodel)

    if db.engine is None:
        @app.when
        def ready(app):
            app.db.__enter__()

        @app.when
        def shutdown(app):
            app.db.__exit__(None, None, None)

    app.db = db
