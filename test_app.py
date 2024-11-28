import pytest
from app import app, db, University

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

@pytest.fixture
def init_db(client):
    with app.app_context():
        university = University(name="Kyiv University", type="University", location="Kyiv", website="http://www.ukr.edu")
        db.session.add(university)
        db.session.commit()
        yield db
        db.drop_all()

def test_search(client, init_db):
    response = client.get('/?query=Kyiv')
    assert b'Kyiv University' in response.data

def test_filter_by_type(client, init_db):
    response = client.get('/?type=University')
    assert b'Kyiv University' in response.data

def test_filter_by_location(client, init_db):
    response = client.get('/?location=Kyiv')
    assert b'Kyiv University' in response.data

def test_university_details(client, init_db):
    response = client.get('/university/1')
    assert b'Kyiv University' in response.data
    assert b'University' in response.data
    assert b'Kyiv' in response.data
    assert b'http://www.ukr.edu' in response.data