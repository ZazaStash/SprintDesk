def test_register_and_me(client):
    response = client.post('/api/auth/register', json={'name':'Екатерина','email':'Katya@Example.com','password':'correctHorse123'})
    assert response.status_code == 201
    data = response.json()
    assert data['user']['role'] == 'member'
    assert data['user']['email'] == 'katya@example.com'
    assert client.get('/api/auth/me', headers={'Authorization':f"Bearer {data['access_token']}"}).json()['name'] == 'Екатерина'


def test_duplicate_email_rejected(client, member):
    response = client.post('/api/auth/register', json={'name':'Дубликат','email':'irina@example.com','password':'correctHorse123'})
    assert response.status_code == 409


def test_login_and_wrong_password(client, member):
    assert client.post('/api/auth/login',json={'email':'irina@example.com','password':'badPassword'}).status_code == 401
    response = client.post('/api/auth/login',json={'email':'irina@example.com','password':'securePassword123'})
    assert response.status_code == 200
    assert response.json()['token_type'] == 'bearer'


def test_password_and_email_validation(client):
    response = client.post('/api/auth/register',json={'name':'x','email':'invalid','password':'short'})
    assert response.status_code == 422


def test_invalid_token(client):
    assert client.get('/api/auth/me').status_code == 401
    assert client.get('/api/auth/me',headers={'Authorization':'Bearer corrupted'}).status_code == 401
