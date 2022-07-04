from http import HTTPStatus

from extensions.db import db
from flask import jsonify
from marshmallow import ValidationError
from models import Role, User
from schemas import role_schema
from sqlalchemy.exc import IntegrityError


class RoleService:

    RESPONSE_DESCRIPTIONS = {
        'ROLE_CREATED': '{0} role created.',
        'ROLE_DELETED': '{0} role deleted.',
        'ROLE_EXISTS': '{0} role already exists.',
        'ROLE_NOT_EXISTS': 'Role {0} does not exist.',
        'USER_NOT_EXISTS': 'User {0} does not exist.',
        'ROLE_ASSIGNED': 'Role {0} assigned to user {1}.',
        'ROLE_UNASSIGNED': 'Role {0} unassigned from user {1}.'
    }

    def get_roles(self):
        return jsonify(role_schema.dump(Role.query.all(), many=True))

    def create_role(self, role_data):
        role_data, err = self._validate_data(role_data, role_schema)
        if err:
            return err, HTTPStatus.BAD_REQUEST

        role = self._check_role_exists(role_data['name'])
        if role:
            message = self._get_response('ROLE_EXISTS', role.name)
            return message, HTTPStatus.BAD_REQUEST

        self._save_role(role_data)

        return self._get_response('ROLE_CREATED', role_data['name']), \
            HTTPStatus.CREATED

    def delete_role(self, role_data):
        role_data, err = self._validate_data(role_data, role_schema)
        if err:
            return err, HTTPStatus.BAD_REQUEST
        role = self._check_role_exists(role_data['name'])
        if not role:
            message = self._get_response('ROLE_NOT_EXISTS', role_data['name'])
            return message, HTTPStatus.NOT_FOUND
        
        self._delete_role(role)
        return self._get_response('ROLE_DELETED', role_data['name'])

    def assign_user_role(self, user_uuid, role_name):
        role, err = self._validate_role(role_name)
        if not role:
            return err, HTTPStatus.BAD_REQUEST

        user, err = self._validate_user(user_uuid)
        if not user:
            return err, HTTPStatus.BAD_REQUEST

        err = self._assign_user_role(user, role)
        if err:
            return err, HTTPStatus.BAD_REQUEST
        return self._get_response('ROLE_ASSIGNED', role.name, user.id)

    def unassign_user_role(self, user_uuid, role_name):
        role, err = self._validate_role(role_name)
        if not role:
            return err, HTTPStatus.BAD_REQUEST

        user, err = self._validate_user(user_uuid)
        if not user:
            return err, HTTPStatus.BAD_REQUEST

        err = self._unassign_user_role(user, role)
        if err:
            return err, HTTPStatus.BAD_REQUEST
        return self._get_response('ROLE_UNASSIGNED', role.name, user.id)

    def _assign_user_role(self, user: User, role: Role):
        try:
            user.roles.append(role)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'message': f'{user.id} already has role {role.name}'}

    def _unassign_user_role(self, user: User, role: Role):
        try:
            user.roles.remove(role)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {'message': f'{user.id} does not have role {role.name}'}

    def _validate_user(self, user_uuid):
        user = self._check_user_exists(user_uuid)
        if not user:
            message = self._get_response('USER_NOT_EXISTS', user_uuid)
            return None, message
        return user, {}

    def _validate_role(self, role_name):
        role = self._check_role_exists(role_name)
        if not role:
            message = self._get_response('ROLE_NOT_EXISTS', role_name)
            return None, message
        return role, {}

    def _check_user_exists(self, user_uuid):
        return User.query.filter(User.id == user_uuid).first()

    def _validate_data(self, data, schema):
        try:
            data = schema.load(data)
        except ValidationError as e:
            return {}, e.messages
        else:
            return data, {}

    def _check_role_exists(self, role):
        return Role.query.filter(Role.name == role).first()

    def _save_role(self, role_data):
        assert role_data.get('name', None) is not None
        role = Role(
            name=role_data.get('name'),
            description=role_data.get('description', None)
        )
        db.session.add(role)
        db.session.commit()

    def _delete_role(self, role):
        Role.query.filter(Role.name == role.name).delete()
        db.session.commit()

    def _get_response(self, label, *args):
        return {'message': self.RESPONSE_DESCRIPTIONS[label].format(*args)}


role_service = RoleService()
