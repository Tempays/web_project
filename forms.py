import flask_wtf
from flask_wtf import FlaskForm
from wtforms.fields.simple import EmailField, PasswordField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    username = StringField(label='username', validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Пароль', validators=[DataRequired()])
    password_again = PasswordField(label='Повторите Пароль', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


class LoginForm(FlaskForm):
    username = EmailField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

