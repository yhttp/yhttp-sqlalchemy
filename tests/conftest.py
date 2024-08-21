import functools

import bddrest
import pytest

from yhttp.core import Application
from yhttp.dev.fixtures import freshdb, cicd


@pytest.fixture
def app(freshdb):
    app = Application()
    app.settings.merge(f'''
      db:
        url: {freshdb}
    ''')
    yield app
    app.shutdown()


@pytest.fixture
def Given(app):
    return functools.partial(bddrest.Given, app)
