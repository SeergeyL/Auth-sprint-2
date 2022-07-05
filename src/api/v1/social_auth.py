from http import HTTPStatus

from extensions.oauth import get_provider
from flask import Blueprint, request

social_auth = Blueprint('social_auth', __name__)


@social_auth.route('/oauth/<provider>', methods=['POST'])
def oauth(provider):
    provider = get_provider(provider)
    if not provider:
        return {'message': 'Provider is not supported.'}, HTTPStatus.NOT_FOUND
    return provider.auth()


@social_auth.route('/oauth-callback/<provider>')
def oauth_callback(provider):
    provider = get_provider(provider)
    response = provider.callback(request)
    if not response:
        return {'message': 'Code is not provided or another error occured.'}
    return provider.authorize_user(response)
