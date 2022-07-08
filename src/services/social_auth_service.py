import abc
import json

from extensions.bcrypt import bcrypt
from extensions.db import db
from flask import jsonify, redirect, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from models import SocialAccount, User
from rauth import OAuth2Service
from sqlalchemy import and_

from services.utils import generate_random_email, generate_random_string


class BaseOAuth(abc.ABC):
    def auth(self):
        return redirect(
            self.service.get_authorize_url(
                response_type='code',
                redirect_uri=self.get_redirect_url(self.name)
            )
        )

    def _create_user(self, email):
        password = generate_random_string()
        password_hash = bcrypt.generate_password_hash(password)
        user = User(email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()
        return user

    def _create_social_account(self, social_id, user_id):
        social = SocialAccount(
            social_id=social_id,
            social_name=self.name,
            user_id=user_id
        )
        db.session.add(social)
        db.session.commit()

    def _create_social_account_if_not_exists(self, social_id, email):
        social = SocialAccount.query.filter(
            and_(
                SocialAccount.social_id == social_id,
                SocialAccount.social_name == self.name
            )
        ).first()

        if not social:
            user = self._create_user(email)
            self._create_social_account(social_id, user.id)
    
    def _create_tokens(self, identity: str):
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return jsonify(access_token=access_token, refresh_token=refresh_token)

    @abc.abstractmethod
    def authorize_user(self):
        pass

    def get_redirect_url(self, provider):
        return url_for('social_auth.oauth_callback', provider=provider, _external=True)


class YandexOAuth(BaseOAuth):
    name = 'yandex'

    def __init__(self, credentials: dict):
        self.service = OAuth2Service(**credentials.dict(exclude={'provider'}))

    def callback(self, request):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        code = request.args.get('code')
        if not code:
            return None

        data = {
            'code': code,
            'grant_type': 'authorization_code'
        }
        session = self.service.get_auth_session(data=data, decoder=decode_json)
        response = session.get('info').json()
        return response

    def authorize_user(self, response):
        social_id = response['id']
        email = response['default_email']
        self._create_social_account_if_not_exists(social_id, email)
        return self._create_tokens(email)


class VKOAuth(BaseOAuth):
    name = 'vk'

    def __init__(self, credentials: dict):
        self.service = OAuth2Service(**credentials.dict(exclude={'provider'}))

    def callback(self, request):
        code = request.args.get('code')
        if not code:
            return None

        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.get_redirect_url(self.name)
        }
        response = self.service.get_raw_access_token(data=data)
        return response.json()

    def authorize_user(self, response):
        social_id = response['user_id']
        email = generate_random_email()
        self._create_social_account_if_not_exists(social_id, email)
        return self._create_tokens(email)
