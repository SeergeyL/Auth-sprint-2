from http import HTTPStatus

from tests.utils import open_file
from models import LoginHistory, User


def test_user_register_with_wrong_data(client):
    """Тестирование регистрации пользователя с неправильно переданными данными."""
    data = open_file('testdata/wrong_register_data.json')
    for user_data in data:
        response = client.post('/v1/register', json=user_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST


def test_user_register_with_correct_data(client, clear_table):
    """Тестирование регистрации пользователя с правильными данными."""
    data = open_file('testdata/correct_register_data.json')
    for user_data in data:
        response = client.post('/v1/register', json=user_data)
        assert response.status_code == HTTPStatus.CREATED

    clear_table(User)


def test_existing_user_register(client, clear_table):
    """Тестирование регистрации уже существующего пользователя."""
    user_data = open_file('testdata/correct_register_data.json')[0]
    response = client.post('/v1/register', json=user_data)
    assert response.status_code == HTTPStatus.CREATED

    response = client.post('/v1/register', json=user_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    clear_table(User)


def test_not_existing_user_login(client):
    """Тестирование авторизации несуществующего пользователя."""
    user_data = open_file('testdata/correct_register_data.json')[0]
    response = client.post('/v1/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_wrong_password_user_login(client, clear_table):
    """Тестирование авторизации с неправильно переданными данными."""
    user_data = open_file('testdata/correct_register_data.json')[0]
    response = client.post('/v1/register', json=user_data)
    
    response = client.post('/v1/login', json={
        'email': user_data['email'],
        'password': ''
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    
    clear_table(User)


def test_user_login(client, clear_table):
    """Тестирование авторизации пользователя с правильно переданными данными."""
    user_data = open_file('testdata/correct_register_data.json')[0]
    client.post('/v1/register', json=user_data)
    response = client.post('/v1/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json

    clear_table([LoginHistory, User])


def test_user_login_history(client, clear_table):
    """Тестирование доступа пользователя к своей истории входов."""
    user_data = open_file('testdata/correct_register_data.json')[0]
    client.post('/v1/register', json=user_data)
    response = client.post('/v1/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })

    access_token = response.json["access_token"]
    access_token_header = f'Bearer {access_token}'
    response = client.get('v1/login-history', headers={'Authorization': access_token_header})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1

    clear_table([LoginHistory, User])


def test_refresh_token(client, clear_table):
    """Тестирование обновления токена."""
    user_data = open_file('testdata/correct_register_data.json')[0]
    client.post('/v1/register', json=user_data)
    response = client.post('/v1/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })

    refresh_token = response.json['refresh_token']
    refresh_token_header = f'Bearer {refresh_token}'
    response = client.post('/v1/refresh', headers={'Authorization': refresh_token_header})
    
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json

    clear_table([LoginHistory, User])


def test_revoke_token(client, clear_table):
    """Тестирование выхода из аккаунта пользователем."""
    user_data = open_file('testdata/correct_register_data.json')[0]
    client.post('/v1/register', json=user_data)
    response = client.post('/v1/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })

    access_token = response.json['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    client.post('/v1/logout', headers=headers)
    response = client.get('v1/login-history', headers=headers)
    
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    clear_table([LoginHistory, User])


def test_wrong_change_password(client):
    """Тестирование смены пароля пользователем с неправпильно переданными данными."""
    data = open_file('testdata/wrong_change_user_password.json')
    for user_data in data:
        response = client.post('/v1/change-password', json=user_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST


def test_correct_change_password(client):
    """Тестирование смены пароля пользователем с правильно переданными данными."""
    user_data = open_file('testdata/correct_change_user_password.json')[0]
    client.post('/v1/register', json={
        'email': user_data['email'],
        'password': user_data['password'],
        'confirm_password': user_data['password']
    })

    response = client.post('/v1/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    assert response.status_code == HTTPStatus.OK

    response = client.post('/v1/change-password', json=user_data)
    assert response.status_code == HTTPStatus.OK

    response = client.post('/v1/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    
    assert response.status_code == HTTPStatus.UNAUTHORIZED
