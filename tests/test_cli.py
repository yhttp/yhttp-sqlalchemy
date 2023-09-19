from bddcli import Given, Application as CLIApplication, status, stderr, \
    when, stdout
import easycli
from yhttp import Application
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from yhttp.ext.sqlalchemy import install


class Bar(easycli.SubCommand):
    __command__ = 'bar'

    def __call__(self, args):
        print('bar')


app = Application()
app.settings.merge('''
db:
  url: postgresql://:@/foo
''')


class Base(DeclarativeBase):
    pass


class Foo(Base):
    __tablename__ = 'foo'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))


install(app, Base, cliarguments=[Bar], create_objects=True)
app.ready()


def test_applicationcli():
    cliapp = CLIApplication('example', 'tests.test_cli:app.climain')
    with Given(cliapp, 'db'):
        assert stderr == ''
        assert status == 0

        when('db drop')
        when('db create')
        assert stderr == ''
        assert status == 0

        when('db drop')
        assert status == 0
        assert stderr == ''

        # Custom Command line interface
        when('db bar')
        assert status == 0
        assert stderr == ''
        assert stdout == 'bar\n'

        when('db c')
        assert status == 0
        assert stderr == ''
        assert stdout == '''Following objects has been created successfully:
S foo_id_seq
r foo
i foo_pkey
'''
