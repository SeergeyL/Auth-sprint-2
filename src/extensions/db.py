from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask):

    POSTGRES_HOST = app.config['POSTGRES_HOST']
    POSTGRES_PORT = app.config['POSTGRES_PORT']
    POSTGRES_USER = app.config['POSTGRES_USER']
    POSTGRES_PASSWORD = app.config['POSTGRES_PASSWORD']
    POSTGRES_DATABASE = app.config['POSTGRES_DATABASE']

    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'

    db.init_app(app)
