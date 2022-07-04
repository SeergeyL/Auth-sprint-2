import re

from marshmallow import ValidationError, validates, validates_schema

from extensions.ma import ma


class UserSchema(ma.Schema):
    email = ma.Email()
    password = ma.String()

    @validates("password")
    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError('Password length should be at least 6 sybmols.', ['password'])
        if re.search('[A-Za-z]', value) is None:
            raise ValidationError('Password should contain letters.', ['password'])
        if re.search('[0-9]', value) is None:
            raise ValidationError('Password should contain numbers.', ['password'])


class UserRegisterSchema(UserSchema):
    confirm_password = ma.String()

    @validates_schema
    def validate_object(self, data, **kwargs):
        if data['password'] != data['confirm_password']:
            raise ValidationError('Passwords should be the same.')


class UserChangePasswordSchema(UserSchema):
    new_password = ma.String()

    @validates_schema
    def validate_object(self, data, **kwargs):
        if data['password'] == data['new_password']:
            raise ValidationError('The new password must be different from the old password.')

    @validates('new_password')
    def validate_new_password(self, value):
        self.validate_password(value)


class LoginHistorySchema(ma.Schema):
    user_id = ma.UUID()
    user_agent = ma.String()
    auth_datetime = ma.DateTime()


class RoleSchema(ma.Schema):
    name = ma.String(required=True)
    description = ma.String()


user_schema_register = UserRegisterSchema()
login_history_schema = LoginHistorySchema()
user_change_password_schema = UserChangePasswordSchema()
role_schema = RoleSchema()
