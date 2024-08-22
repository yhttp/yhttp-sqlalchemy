from yhttp.ext.dbmanager import DatabaseCommand

from . import orm, cli


def install(app, basemodel, db=None, cliarguments=None):
    DatabaseCommand.__arguments__.append(cli.DatabaseObjectsCommand)
    if cliarguments:
        cli.DatabaseObjectsCommand.__arguments__.extend(cliarguments)

    if db is None:
        db = orm.ApplicationORM(basemodel, app)

    if db.engine is None:
        @app.when
        def ready(app):
            app.db.connect()

        @app.when
        def shutdown(app):
            app.db.disconnect()

        @app.when
        def endresponse(response):
            app.db.session.reset()

    app.db = db
