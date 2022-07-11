import pytest

from performance.app import create_app
from performance.extensions import assets
from performance.extensions import db

@pytest.fixture
def app(request):
    app = create_app(silent_config=True)

    app.config.update(dict(
        ASSETS_DEBUG = True,
        SQLALCHEMY_DATABASE_URI = 'postgresql:///test_performance',
    ))

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()

    # How to clear the bundles
    # https://stackoverflow.com/a/20948072/2680592
    assets._named_bundles = {}

@pytest.fixture
def client(app):
    yield app.test_client()
