def test_member_creates_updates_and_deletes_task(client,member):
    headers = member['headers']
    created = client.post('/api/tasks',headers=headers,json={'title':'Подготовить презентацию','description':'Слайды для команды','priority':3})
    assert created.status_code == 201
    task = created.json()
    assert task['owner_id'] == member['user']['id']
    assert task['status'] == 'todo'
    assert len(client.get('/api/tasks',headers=headers).json()) == 1
    updated = client.patch(f"/api/tasks/{task['id']}",headers=headers,json={'status':'done','title':'Готовая презентация'})
    assert updated.status_code == 200
    assert updated.json()['status'] == 'done'
    assert client.delete(f"/api/tasks/{task['id']}",headers=headers).status_code == 204
    assert client.get('/api/tasks',headers=headers).json() == []


def test_member_cannot_access_foreign_task(client,member,other_member):
    task = client.post('/api/tasks',headers=member['headers'],json={'title':'Личная задача'}).json()
    task_id = task['id']
    assert client.get('/api/tasks',headers=other_member['headers']).json() == []
    assert client.get(f'/api/tasks/{task_id}',headers=other_member['headers']).status_code == 404
    assert client.patch(f'/api/tasks/{task_id}',headers=other_member['headers'],json={'status':'done'}).status_code == 404
    assert client.delete(f'/api/tasks/{task_id}',headers=other_member['headers']).status_code == 404


def test_only_admin_can_assign_tasks(client,member,other_member,admin):
    payload={'title':'Задача для Дмитрия','owner_id':other_member['user']['id']}
    assert client.post('/api/tasks',headers=member['headers'],json=payload).status_code == 403
    created=client.post('/api/tasks',headers=admin['headers'],json=payload)
    assert created.status_code == 201
    assert created.json()['owner_id'] == other_member['user']['id']
    assert len(client.get('/api/tasks',headers=admin['headers']).json()) == 1
    assert len(client.get('/api/tasks',headers=other_member['headers']).json()) == 1
    assert client.get('/api/users',headers=member['headers']).status_code == 403
    assert len(client.get('/api/users',headers=admin['headers']).json()) == 3


def test_task_validation(client,member):
    headers=member['headers']
    assert client.post('/api/tasks',headers=headers,json={'title':'X','priority':8}).status_code == 422
    assert client.post('/api/tasks',headers=headers,json={'title':'Нормальная задача','status':'invalid'}).status_code == 422
    task=client.post('/api/tasks',headers=headers,json={'title':'Нормальная задача'}).json()
    assert client.patch(f"/api/tasks/{task['id']}",headers=headers,json={'priority':None}).status_code == 422
    assert client.patch(f"/api/tasks/{task['id']}",headers=headers,json={'priority':0}).status_code == 422


def test_missing_owner_and_task(client,admin):
    assert client.post('/api/tasks',headers=admin['headers'],json={'title':'Новая задача','owner_id':98765}).status_code == 422
    assert client.get('/api/tasks/98765',headers=admin['headers']).status_code == 404


def test_anonymous_is_rejected(client):
    assert client.get('/api/tasks').status_code == 401
    assert client.post('/api/tasks',json={'title':'Новая задача'}).status_code == 401


def test_frontend_and_health(client):
    assert client.get('/').status_code == 200
    assert 'SprintDesk' in client.get('/').text
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/api/health').json() == {'status':'ok'}
