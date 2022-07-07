import datetime
import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from extensions.db import db

Base = declarative_base()
Base.query = db.session.query_property()


roles_users = db.Table(
    'roles_users',
    Base.metadata,
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id')),
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('role.id')),
    UniqueConstraint('user_id', 'role_id')
)


class User(Base):
    __tablename__ = 'user'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.Date, default=datetime.datetime.now)
    login_history = db.relationship('LoginHistory')
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    def __repr__(self):
        return f'<User {self.email}>'


class SocialAccount(Base):
    __tablename__ = 'social_account'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('social_account', uselist=False))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'), )

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'


class Role(Base):
    __tablename__ = 'role'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_pc" PARTITION OF "users_sign_in" FOR VALUES IN ('pc')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_tablet" PARTITION OF "users_sign_in" FOR VALUES IN ('tablet')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')"""
    )


class LoginHistory(Base):
    __tablename__ = 'login_history'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), index=True)
    user_agent = db.Column(db.String)
    auth_datetime = db.Column(db.DateTime(), default=datetime.datetime.now)
    user_device_type = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        return f'<Login {self.user_id}: {self.auth_datetime}>'
