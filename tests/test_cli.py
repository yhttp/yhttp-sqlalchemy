import os

from bddcli import Given, Application as CLIApplication, status, stderr, \
    when, stdout
import easycli
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from yhttp.core import Application
from yhttp.dev.fixtures import CICD

from yhttp.ext import dbmanager, sqlalchemy as saext


class Bar(easycli.SubCommand):
    __command__ = 'bar'

    def __call__(self, args):
        print('bar')


class Baz(easycli.SubCommand):
    __command__ = 'baz'

    def __call__(self, args):
        print('baz')


class BaseModel(DeclarativeBase):
    pass


class Foo(BaseModel):
    __tablename__ = 'foo'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))


_host = os.environ.get('YHTTP_DB_DEFAULT_HOST', 'localhost' if CICD else '')
_user = os.environ.get('YHTTP_DB_DEFAULT_USER', 'postgres' if CICD else '')
_pass = os.environ.get('YHTTP_DB_DEFAULT_PASS', 'postgres' if CICD else '')


app = Application('0.1.0', 'foo')
app.settings.merge(f'''
db:
  url: postgresql://{_user}:{_pass}@{_host}/foo
''')
dbmanager.install(app, cliarguments=[Bar])
saext.install(app, BaseModel, cliarguments=[Baz])


def test_applicationcli(cicd):
    cliapp = CLIApplication('example', 'tests.test_cli:app.climain')
    env = os.environ.copy()
    if cicd:
        env.setdefault('YHTTP_DB_DEFAULT_HOST', 'localhost')
        env.setdefault('YHTTP_DB_DEFAULT_ADMINUSER', 'postgres')
        env.setdefault('YHTTP_DB_DEFAULT_ADMINPASS', 'postgres')

    with Given(cliapp, 'db', environ=env):
        assert str(stderr) == ''
        assert status == 0

        # Custom Command line interface
        when('db bar')
        assert status == 0
        assert stderr == ''
        assert stdout == 'bar\n'

        when('db objects baz')
        assert status == 0
        assert stderr == ''
        assert stdout == 'baz\n'

        when('db drop')
        when('db create')
        assert str(stderr) == ''
        assert status == 0

        when('db objects create')
        assert str(stderr) == ''
        assert status == 0
        assert stdout == '''Following objects has been created successfully:
S foo_id_seq
r foo
i foo_pkey
'''
