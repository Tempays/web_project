import flask_wtf
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.fields.simple import EmailField, PasswordField, StringField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    login = StringField(label='Имя пользователя', validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Пароль', validators=[DataRequired()])
    password_again = PasswordField(label='Повторите пароль', validators=[DataRequired()])
    submit = SubmitField(label='Войти')


class LoginForm(FlaskForm):
    username = EmailField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AccommodationAddForm(FlaskForm):
    name = StringField('Название объявления', validators=[DataRequired()])
    description = StringField('Описание жилья', validators=[DataRequired()])
    cost = StringField('Стоимость', validators=[DataRequired()])
    address = StringField('Адрес (Разделяйте значения запятой)', validators=[DataRequired()])
    photo = FileField('Фото', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    submit = SubmitField('Подтвердить')


class ProfileForm(FlaskForm):
    photo = FileField('Фото', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')], default='')
    submit = SubmitField('Подтвердить')


