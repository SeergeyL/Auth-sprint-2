import os
from pydantic import BaseSettings, Field, BaseModel


class OAuthProvider(BaseModel):
    provider: str
    client_id: str
    client_secret: str
    authorize_url: str
    access_token_url: str
    base_url: str


class BaseConfig(BaseSettings):
    SECRET_KEY: str = Field('top_secret', env='SECRET_KEY')
    
    POSTGRES_HOST: str = Field('127.0.0.1', env='POSTGRES_HOST')
    POSTGRES_PORT: int = Field(5432, env='POSTGRES_PORT')
    POSTGRES_USER: str = Field('postgres', env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field('123456', env='POSTGRES_PASSWORD')
    POSTGRES_DATABASE: str = Field('auth_database', env='POSTGRES_DATABASE')

    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')

    OAUTH_CREDENTIALS = {
        'yandex': OAuthProvider(
            provider='yandex',
            client_id=os.environ.get('YANDEX_OAUTH_ID'),
            client_secret=os.environ.get('YANDEX_OAUTH_SECRET'),
            authorize_url='https://oauth.yandex.ru/authorize',
            access_token_url='https://oauth.yandex.ru/token',
            base_url='https://login.yandex.ru/'
        )
    }
