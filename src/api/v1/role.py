from functools import wraps
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import Role, User
from services.role_service import role_service

role = Blueprint('role', __name__)


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            user = User.query.filter(User.email == identity).first()
            admin = Role.query.filter(Role.name == 'admin').first()
            if admin in user.roles:
                return fn(*args, **kwargs)
            else:
                return jsonify(error='Access forbidden!'), HTTPStatus.FORBIDDEN
        return decorator
    return wrapper


@role.route('/roles', methods=['GET', 'POST', 'DELETE'])
@admin_required()
def roles():
    """Roles endpoint
    ---
    get:
      parameters:
        - name: access_token
          in: body
          type: string
          required: true
          description: admin access token
      responses:
        200:
          description: Return list of roles
    post:
      parameters:
        - name: access_token
          in: header
          type: string
          required: true
          description: admin access token
        - name: body
          in: body
          type: object
          required: true
      responses:
        200:
          description: Create role
    delete:
      parameters:
        - name: access_token
          in: header
          type: string
          required: true
          description: admin access token
        - name: body
          in: body
          type: object
          required: true
      responses:
        200:
          description: Role deleted
    """
    if request.method == 'GET':
        return role_service.get_roles()
    
    role_data = request.get_json()
    if request.method == 'POST':
        return role_service.create_role(role_data)
    if request.method == 'DELETE':
        return role_service.delete_role(role_data)


@role.route('/user/<user_uuid>/<role>', methods=['POST', 'DELETE'])
@admin_required()
def user_role(user_uuid, role):
    if request.method == 'POST':
        return role_service.assign_user_role(user_uuid, role)
    if request.method == 'DELETE':
        return role_service.unassign_user_role(user_uuid, role)
