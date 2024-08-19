from sqlalchemy import text
from easycli import SubCommand


class CreateObjectsCommand(SubCommand):
    __command__ = 'create'
    __aliases__ = ['c']

    def __call__(self, args):
        db = args.application.db
        with db:
            db.create_objects()
            self.report_objects(args)

    def report_objects(self, args):
        app = args.application
        with app.db.engine.connect() as conn:
            result = conn.execute(text('''
                SELECT relname, relkind
                FROM pg_class
                WHERE relname !~ '^(pg|sql)_' AND relkind != 'v';
            '''))

            print('Following objects has been created successfully:')
            for name, kind in result.fetchall():
                print(kind, name)


class DatabaseObjectsCommand(SubCommand):
    __command__ = 'objects'
    __aliases__ = ['obj', 'o']
    __arguments__ = [
        CreateObjectsCommand,
    ]
