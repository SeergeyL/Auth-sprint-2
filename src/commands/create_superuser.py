import click
from extensions.db import db
from extensions.bcrypt import bcrypt
from flask import Blueprint
from models import Role, User

superuser = Blueprint('superuser', __name__)


@superuser.cli.command('create')
@click.option('--email', help='Admin email.')
@click.option('--password', help='Admin password.')
def create(email, password):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password=password_hash)
    role = Role.query.filter(Role.name == 'admin').first()
    if not role:
        role = Role(name='admin')
    
    user.roles.append(role)
    db.session.add(user)
    db.sessionn.commit()
    click.echo('Superuser successfully created.')
