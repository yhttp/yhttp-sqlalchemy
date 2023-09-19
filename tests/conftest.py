import functools

import bddrest
import pytest

from yhttp import Application
from yhttp.ext.sqlalchemy.fixtures import freshdb


@pytest.fixture
def app():
    app = Application()
    yield app
    app.shutdown()


@pytest.fixture
def Given(app):
    return functools.partial(bddrest.Given, app)
