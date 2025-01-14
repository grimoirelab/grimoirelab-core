from grimoirelab.core.config.settings import *  # noqa: F403,F401
from grimoirelab.core.config.settings import INSTALLED_APPS, _RQ_DATABASE, RQ

import warnings

import rq
import django_rq.queues

from fakeredis import FakeRedis, FakeStrictRedis

INSTALLED_APPS.append('tests')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'loggers': {
        "grimoirelab.core": {
            "level": "CRITICAL"
        },
    }
}

SQL_MODE = [
    'NO_ZERO_IN_DATE',
    'NO_ZERO_DATE',
    'ERROR_FOR_DIVISION_BY_ZERO',
    'NO_AUTO_CREATE_USER',
    'NO_ENGINE_SUBSTITUTION',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'root',
        'NAME': 'grimoirelab_db',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': ','.join(SQL_MODE)
        },
        'TEST': {
            'NAME': 'testgrimoire',
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_520_ci',
        },
        'HOST': '127.0.0.1',
        'PORT': 3306
    }
}

TEST_DATABASE_IMAGE = "mariadb:11.4"

TEST_RUNNER = 'tests.runners.TestContainersRunner'


# Configuration to pretend there is a Redis service
# available. We need to set up the connection before
# RQ Django reads the settings. Also, the connection
# must be the same because in fakeredis connections
# do not share the state. Therefore, we define a
# singleton object to reuse it.
class FakeRedisConn:
    """Singleton FakeRedis connection."""

    def __init__(self):
        self.conn = None

    def __call__(self, _, strict):
        if not self.conn:
            self.conn = FakeStrictRedis() if strict else FakeRedis()
        return self.conn


RQ_QUEUES['testing'] = _RQ_DATABASE  # noqa: F405
RQ['WORKER_CLASS'] = rq.worker.SimpleWorker

django_rq.queues.get_redis_connection = FakeRedisConn()

# Ignore warnings raised by the tests

# This warning is raised when the model is registered twice.
# This is only happening because we are running the tests with
# custom test models that need to be registered several times.
warnings.filterwarnings('ignore', message=r"Model .+ was already registered")

# This is raised because fakeredis does not support the CLIENT SETNAME
# command. This is not important for the tests.
warnings.filterwarnings('ignore', message=r"CLIENT SETNAME command not supported")
