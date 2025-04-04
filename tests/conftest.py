import functools

import bddrest
import pytest

from yhttp.core import Application
from yhttp.dev.fixtures import freshdb, cicd


@pytest.fixture
def app(freshdb):
    app = Application('0.1.0', 'foo')
    app.settings.merge(f'''
      db:
        url: {freshdb}
    ''')
    yield app
    app.shutdown()


@pytest.fixture
def Given(app):
    return functools.partial(bddrest.Given, app)
