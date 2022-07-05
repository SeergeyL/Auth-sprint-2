import os


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DATABASE = os.environ.get('POSTGRES_DATABASE')

    REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

    OAUTH_CREDENTIALS = {
        'yandex': {
            'client_id': os.environ.get('YANDEX_OAUTH_ID'),
            'client_secret': os.environ.get('YANDEX_OAUTH_SECRET'),
            'authorize_url': 'https://oauth.yandex.ru/authorize',
            'access_token_url': 'https://oauth.yandex.ru/token',
            'base_url': 'https://login.yandex.ru/'
        }
    }
