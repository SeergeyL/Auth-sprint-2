from flask import Flask
from flask_jwt_extended import JWTManager

jwt = JWTManager()


def init_jwt(app: Flask):
    jwt.init_app(app)
