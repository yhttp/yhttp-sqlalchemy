import os
import datetime

import pytest
from .dbmanager import createdbmanager


@pytest.fixture
def freshdb():
    """ Creates a fresh database for each test.

    Default configuration is using peer authentication method on
    Postgresql's Unix Domain Socket.
    """

    host = os.environ.get('YHTTPDEV_DB_HOST', '')
    user = os.environ.get('YHTTPDEV_DB_USER', '')
    password = os.environ.get('YHTTPDEV_DB_PASS', '')

    dbname = f'freshdb_{datetime.datetime.now():%Y%m%d%H%M%S}'
    dbmanager = createdbmanager(host, 'postgres', user, password)
    dbmanager.create(dbname, dropifexists=True)
    freshurl = f'postgresql://:@/{dbname}'
    yield freshurl
    dbmanager.dropifexists(dbname)
