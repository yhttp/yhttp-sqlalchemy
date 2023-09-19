import os
import functools
import getpass

from easycli import SubCommand, Argument

from . import dbmanager
from .decorator import dbsession


getdbpass = functools.partial(getpass.getpass, 'Enter db password: ')


DEFAULT_DBUSER = os.environ['USER']


class DatabaseAdministrativeCommand(SubCommand):
    __arguments__ = [
        Argument(
            '-H',
            '--host',
            default=os.environ.get('YHTTPSQLALCHEMY_DEFAULT_HOST', ''),
            help='DB hostname, default: empty.'
        ),
        Argument('-d', '--database', default='postgres', help='DB name'),
        Argument(
            '-u',
            '--user',
            default=os.environ.get(
                'YHTTPSQLALCHEMY_DEFAULT_ADMINDBUSER',
                DEFAULT_DBUSER
            ),
            help=f'DB username, default: ${DEFAULT_DBUSER}'
        ),
        Argument(
            '-p', '--password',
            nargs='?',
            default=os.environ.get(
                'YHTTPSQLALCHEMY_DEFAULT_ADMINPASS',
                'postgres'
            ),
            help='DB password'
        ),
    ]

    def getdbmanager(self, args):
        password = args.password or getdbpass()

        return dbmanager.PostgresqlManager(
            user=args.user,
            password=password,
            host=args.host,
            dbname=args.database
        )

    def getappdbinfo(self, args):
        dbsettings = args.application.settings.db
        url = dbsettings.url
        return url


class CreateDatabase(DatabaseAdministrativeCommand):
    __command__ = 'create'
    __aliases__ = ['c']

    def __call__(self, args):
        info = self.getappdbinfo(args)
        self.getdbmanager(args) \
            .create(info['database'], owner=info.get('user'))

        args.application.ready()
        self.report_objects(args)

    @dbsession
    def report_objects(self, args):
        app = args.application
        with app.db.engine.begin() as conn:
            result = conn.execute('''
                SELECT relname, relkind
                FROM pg_class
                WHERE relname !~ '^(pg|sql)_' AND relkind != 'v';
            ''')

            print('Following objects has been created successfully:')
            for name, kind in result.fetchall():
                print(kind, name)


class DropDatabase(DatabaseAdministrativeCommand):
    __command__ = 'drop'
    __aliases__ = ['d']

    def __call__(self, args):
        info = self.getappdbinfo(args)
        self.getdbmanager(args).drop(info['database'])


class DatabaseCLI(SubCommand):
    __command__ = 'database'
    __aliases__ = ['db']
    __arguments__ = [
        CreateDatabase,
        DropDatabase
    ]
