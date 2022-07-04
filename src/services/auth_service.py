import datetime
from http import HTTPStatus

from extensions.bcrypt import bcrypt
from extensions.cache import redis_db
from extensions.db import db
from extensions.ma import ma
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError
from models import LoginHistory, User
from schemas import (login_history_schema, user_change_password_schema,
                     user_schema_register)


class AuthService:
    
    RESPONSE_DESCRIPTIONS = {
        'ALREADY_EXISTS': 'User {0} already exists.',
        'SUCCESS': 'User successfully created.',
        'NOT_EXIST': 'User {0} does not exist.',
        'WRONG_PASSWORD': 'Wrong password.',
        'TOKEN_REVOKED': '{0} token successfully revoked.',
        'PASSWORD_CHANGED': 'Password successfully changed.'
    }

    ACCESS_EXPIRATION = {
        'refresh': datetime.timedelta(days=30),
        'access': datetime.timedelta(minutes=15)
    }

    def create_user(self, user_data: dict):
        user_data, err = self._validate_user_data(user_data, user_schema_register)
        if err:
            return err, HTTPStatus.BAD_REQUEST

        exists = self._check_user_exists(user_data['email'])
        if exists:
            message = self._get_response('ALREADY_EXISTS', user_data['email'])
            return message, HTTPStatus.BAD_REQUEST
        
        user_data['password'] = self._generate_password_hash(user_data['password'])
        self._save_user(user_data)

        message = self._get_response('SUCCESS')
        return message, HTTPStatus.CREATED

    def login_user(self, user_data: dict):
        user = self._check_user_exists(user_data['email'])
        if not user:
            message = self._get_response('NOT_EXIST', user_data['email'])
            return message, HTTPStatus.UNAUTHORIZED
        
        if not self._check_user_password(user, user_data):
            message = self._get_response('WRONG_PASSWORD')
            return message, HTTPStatus.UNAUTHORIZED
        
        self._create_login_history_record(user, user_data['user_agent'])
        return self._create_tokens(user.email), HTTPStatus.OK
    
    def refresh_token(self, identity: str):
        return self._create_tokens(identity), HTTPStatus.OK

    def revoke_token(self, jti: str, token_type: str):
        redis_db.set(jti, '', self.ACCESS_EXPIRATION[token_type])
        message = self._get_response('TOKEN_REVOKED', token_type)
        return message

    def get_login_history(
        self,
        identity: str,
        page: int = None,
        per_page: int = None
    ):
        user = self._check_user_exists(identity)
        query = LoginHistory.query.filter(LoginHistory.user_id == user.id) \
            .order_by(LoginHistory.auth_datetime.desc()) \
            .paginate(page, per_page, error_out=False).items
        return jsonify(login_history_schema.dump(query, many=True))

    def change_password(self, user_data: dict):
        user_data, err = self._validate_user_data(user_data, user_change_password_schema)
        if err:
            return err, HTTPStatus.BAD_REQUEST            

        user = self._check_user_exists(user_data['email'])
        if not user:
            message = self._get_response('NOT_EXISTS')
            return message, HTTPStatus.BAD_REQUEST

        if not self._check_user_password(user, user_data):
            message = self._get_response('WRONG_PASSWORD')
            return message, HTTPStatus.UNAUTHORIZED

        self._set_user_new_password(user, user_data['new_password'])
        return self._get_response('PASSWORD_CHANGED'), HTTPStatus.OK

    def _set_user_new_password(self, user: User, new_password: str):
        new_password_hash = self._generate_password_hash(new_password)
        self._update_user(user, password=new_password_hash)

    def _check_user_exists(self, email: str):
        return User.query.filter(User.email == email).first()

    def _validate_user_data(self, user_data: dict, schema: ma.Schema):
        try:
            data = schema.load(user_data)
        except ValidationError as e:
            return {}, e.messages
        else:
            return data, {}

    def _save_user(self, user_data: dict):
        email = user_data['email']
        password = user_data['password']

        user = User(email=email, password=password)

        db.session.add(user)
        db.session.commit()

    def _update_user(self, user: User, **kwargs):
        user.query.update(kwargs)
        db.session.commit()

    def _create_login_history_record(self, user: User, user_agent: str):
        record = LoginHistory(
            user_id=user.id,
            user_agent=user_agent
        )
        db.session.add(record)
        db.session.commit()

    def _check_user_password(self, user: User, user_data: dict):
        return bcrypt.check_password_hash(user.password, user_data['password'])
    
    def _generate_password_hash(self, password: str):
        password = bcrypt.generate_password_hash(password)
        return password.decode('utf-8')

    def _create_tokens(self, identity: str):
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return jsonify(access_token=access_token, refresh_token=refresh_token)

    def _get_response(self, message_key: str, *args):
        return {
            'message': self.RESPONSE_DESCRIPTIONS[message_key].format(*args)
        }


auth_service = AuthService()
