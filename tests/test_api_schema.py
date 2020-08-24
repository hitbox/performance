import uuid
import unittest

from flask import request, url_for
import flask_login
import sqlalchemy as sa

from performance.app import create_app
from performance.extensions import db
from performance.user.model import User

def connect_current_user_database():
    engine = sa.create_engine(
        sa.engine.url.URL(drivername = 'postgresql', database = ''))
    conn = engine.connect()
    conn.execute('rollback')
    return conn

class BaseTestCase(unittest.TestCase):

    database = f'_testing_performance_{str(uuid.uuid4()).replace("-", "_")}'

    @classmethod
    def setUpClass(cls):
        """
        Create app and temporary database; and add a user.
        """
        conn = connect_current_user_database()
        conn.execute(f'CREATE DATABASE {cls.database}')
        conn.close()
        cls.app = create_app(
            TESTING = True,
            SQLALCHEMY_DATABASE_URI = sa.engine.url.URL(
                drivername = 'postgresql',
                database = cls.database,
            )
        )
        with cls.app.test_request_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        conn = connect_current_user_database()
        conn.execute(f'DROP DATABASE {cls.database}')
        conn.close()


@unittest.skip('very painful making this run and it does not do anything')
class TestAPI(BaseTestCase):

    def test_schema_dump(self):
        with self.app.test_request_context():
            print(url_for('report.edit', year=2019, month=9, day=19))
            print(url_for('api.reports'))
            print(url_for('api.flights'))


if __name__ == '__main__':
    unittest.main()
