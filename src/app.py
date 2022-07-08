from flasgger import Swagger
from flask import Flask, request

from api.v1.auth import auth
from api.v1.role import role
from api.v1.social_auth import social_auth
from commands.create_superuser import superuser
from config import BaseConfig
from extensions.bcrypt import init_bcrypt
from extensions.cache import init_cache
from extensions.db import init_db
from extensions.jaeger import init_jaeger
from extensions.jwt import init_jwt
from extensions.limiter import init_limiter
from extensions.ma import init_schemas
from extensions.oauth import init_oauth


def create_app():
    app = Flask(__name__)
    config = BaseConfig()
    app.config.from_object(config)

    swagger = Swagger(app)

    # Routes
    app.register_blueprint(auth, url_prefix='/v1')
    app.register_blueprint(role, url_prefix='/v1')
    app.register_blueprint(social_auth, url_prefix='/v1')

    # Commands
    app.register_blueprint(superuser)

    # Postgres
    init_db(app)

    # Redis
    init_cache(app)

    app.app_context().push()

    # Marshmallow
    init_schemas(app)

    # Bcrypt
    init_bcrypt(app)

    # JWT
    init_jwt(app)

    # OAuth
    init_oauth(app)

    init_jaeger(app)

    # Limiter
    init_limiter(app)

    return app
    

app = create_app()


@app.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is required') 


if __name__ == '__main__':
    app.run(debug=True)
