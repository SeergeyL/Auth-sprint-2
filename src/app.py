from flasgger import Swagger
from flask import Flask

from api.v1.auth import auth
from api.v1.role import role
from commands.create_superuser import superuser
from extensions.bcrypt import init_bcrypt
from extensions.cache import init_cache
from extensions.db import init_db
from extensions.jwt import init_jwt
from extensions.ma import init_schemas


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.BaseConfig')
    swagger = Swagger(app)

    # Routes
    app.register_blueprint(auth, url_prefix='/v1')
    app.register_blueprint(role, url_prefix='/v1')

    # Commandss
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
    return app
    

app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
