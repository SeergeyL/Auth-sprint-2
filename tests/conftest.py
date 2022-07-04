import pytest
from app import create_app
from extensions.db import db
from models import Base

from dotenv import load_dotenv
load_dotenv()

@pytest.fixture(scope='session')
def app():
    app = create_app()
    Base.metadata.create_all(db.engine)
    yield app
    db.session.remove()
    Base.metadata.drop_all(db.engine)


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture()
def clear_table():
    def _clear_table(table):
        if isinstance(table, (list, tuple)):
            for table in table:
                table.query.delete()
        else:
            table.query.delete()
            db.session.commit()
    return _clear_table
