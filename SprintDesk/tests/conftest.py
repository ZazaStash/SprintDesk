import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import User
from app.security import hash_password


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_db():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        test_client.session_factory = factory
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def member(client):
    data = client.post('/api/auth/register', json={'name':'Ирина','email':'irina@example.com','password':'securePassword123'}).json()
    return {'headers':{'Authorization':f"Bearer {data['access_token']}"}, 'user':data['user']}


@pytest.fixture
def other_member(client):
    data = client.post('/api/auth/register', json={'name':'Дмитрий','email':'dmitry@example.com','password':'securePassword456'}).json()
    return {'headers':{'Authorization':f"Bearer {data['access_token']}"}, 'user':data['user']}


@pytest.fixture
def admin(client):
    with client.session_factory() as db:
        user = User(name='Главный администратор', email='admin@example.com', role='admin', password_hash=hash_password('securePassword789'))
        db.add(user)
        db.commit()
    login = client.post('/api/auth/login',json={'email':'admin@example.com','password':'securePassword789'}).json()
    return {'headers':{'Authorization':f"Bearer {login['access_token']}"},'user':login['user']}
