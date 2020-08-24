import unittest

import sqlalchemy as sa

from performance.app import create_app
from performance.extensions import db

class BaseTest(unittest.TestCase):

    def setUp(self):
        uri = sa.engine.url.URL(drivername='postgresql', database='_testing_performance')
        track_modifications = False
        # LOGIN_DISABLED is evaluated at `flask_login.login_required`
        # decorating time. It won't be noticed later.
        self.app = create_app({
            'LOGIN_DISABLED': True,
            'SECRET_KEY': 'testing_secret_key',
            'SQLALCHEMY_DATABASE_URI': uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': track_modifications,
            'TESTING': True,
        })
        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
