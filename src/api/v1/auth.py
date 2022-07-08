from http import HTTPStatus

from extensions.cache import redis_db
from extensions.jwt import jwt
from extensions.limiter import limiter
from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from schemas import user_roles
from services.auth_service import auth_service

auth = Blueprint('auth', __name__)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = redis_db.get(jti)
    return token_in_redis is not None


@auth.route('/register', methods=['POST'])
def register():
    """Register user endpoint
    ---
    parameters:
      - name: body
        in: body
        type: string
        required: true
        description: Data to create user in db
        schema:
          $ref: "#/definitions/UserRegister"
    definitions:
      UserRegister:
        type: object
        properties:
          email:
            type: string
          password:
            type: string
          confirm_password:
            type: string
    responses:
      200:
        description: User successfully created.
      400:
        description: Either wrong data provided or user already exists.
    """
    user_data = request.get_json()
    result, status = auth_service.create_user(user_data)
    return result, status


@auth.route('/login', methods=['POST'])
@limiter.limit('1 per second')
def login():
    """Login user endpoint
    ---
    parameters:
      - name: body
        in: body
        type: string
        required: true
        description: Data to authorize user in service
        schema:
          $ref: "#/definitions/UserLogin"
    definitions:
      UserLogin:
        type: object
        properties:
          email:
            type: string
          password:
            type: string
    responses:
      200:
        description: User successfully created.
      401:
        description: Either wrong data provided or user does not exist.
    """
    user_data = request.get_json()
    user_data['user_agent'] = request.user_agent.string
    return auth_service.login_user(user_data)


@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@limiter.limit('1 per second')
def refresh():
    """Refresh user tokens endpoint
    ---
    parameters:
      - name: refresh_token
        in: header
        type: string
        required: true
        description: User refresh_token
    responses:
      200:
        description: Return fresh tokens
    """
    identity = get_jwt_identity()
    return auth_service.refresh_token(identity)


@auth.route('/logout', methods=['POST'])
@jwt_required(verify_type=False)
@limiter.limit('1 per second')
def logout():
    """Revoke user tokens endpoint. Tokens are added to blocklist untill expiration
    ---
    parameters:
      - name: token
        in: header
        type: string
        required: true
        description: access or refresh token
    responses:
      200:
        description: Return tokens
    """
    token = get_jwt()
    jti = token['jti']
    ttype = token['type']
    return auth_service.revoke_token(jti, ttype)
 

@auth.route('/login-history')
@jwt_required()
@limiter.limit('1 per second')
def login_history():
    """User login history endpoint
    ---
    parameters:
      - name: access_token
        in: header
        type: string
        required: true
    responses:
      200:
        description: Return login history
      401:
        description: Invalid access token
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per-page', default=10, type=int)
    identity = get_jwt_identity()
    return auth_service.get_login_history(identity, page, per_page)


@auth.route('/change-password', methods=['POST'])
@limiter.limit('1 per second')
def change_password():
    """User change password endpoint
    ---
    parameters:
      - name: body
        in: body
        type: string
        required: true
        schema:
          $ref: "#/definitions/UserChangePassword"
    definitions:
      UserChangePassword:
        type: object
        properties:
          email:
            type: string
          password:
            type: string
          new_password:
            type: string
    responses:
      200:
        description: Password changed
      400:
        description: Wrong data provided
    """
    user_data = request.get_json()
    return auth_service.change_password(user_data)


@auth.route('/check-auth', methods=['GET'])
@jwt_required()
@limiter.limit('60 per second')
def check_auth():
    identity = get_jwt_identity()
    user = auth_service._check_user_exists(identity)
    if not user:
        return {'message': 'User does not exist.'}, \
            HTTPStatus.UNAUTHORIZED
    return user_roles.dumps(user)
