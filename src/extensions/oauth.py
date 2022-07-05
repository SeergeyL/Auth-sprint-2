from flask import Flask
from services.social_auth_service import BaseOAuth


_providers = {}

def init_oauth(app: Flask):
    for provider_cls in BaseOAuth.__subclasses__():
        provider = provider_cls.name
        creds = app.config['OAUTH_CREDENTIALS'][provider]
        _providers[provider] = provider_cls(creds)


def get_provider(provider: str) -> BaseOAuth:
    return _providers.get(provider, None)
