from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms_components import DateTimeLocalField

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Имя уже занято.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email уже зарегистрирован.')

class EventForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Optional()])
    date = DateField('Дата', validators=[DataRequired()], format='%Y-%m-%d')
    time = TimeField('Время', validators=[Optional()], format='%H:%M')
    reminder = DateTimeLocalField('Напоминание', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    color = SelectField('Цвет', choices=[('default', 'По умолчанию'), ('red', 'Красный'), ('green', 'Зелёный'), ('blue', 'Синий')])
    submit = SubmitField('Сохранить')