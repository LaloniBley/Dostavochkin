from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, TelField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp, Optional, NumberRange
from datetime import datetime


class RegistrationForm(FlaskForm):
    lastname = StringField('Фамилия', validators=[
        DataRequired(message='Фамилия обязательна для заполнения'),
        Length(min=2, max=50, message='Фамилия должна быть от 2 до 50 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z]+$', message='Фамилия должна содержать только буквы')
    ])
    firstname = StringField('Имя', validators=[
        DataRequired(message='Имя обязательно для заполнения'),
        Length(min=2, max=50, message='Имя должно быть от 2 до 50 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z]+$', message='Имя должно содержать только буквы')
    ])
    middlename = StringField('Отчество', validators=[
        Optional(),
        Length(max=50, message='Отчество не может быть длиннее 50 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z]*$', message='Отчество должно содержать только буквы')
    ])
    phone = TelField('Телефон', validators=[
        DataRequired(message='Телефон обязателен для заполнения'),
        Regexp(r'^(\+7|8)[0-9]{10}$',
               message='Введите корректный номер телефона (например: +78005553535 или 88005553535)')
    ])
    login = StringField('Логин', validators=[
        DataRequired(message='Логин обязателен для заполнения'),
        Length(min=4, max=16, message='Логин должен быть от 4 до 16 символов'),
        Regexp(r'^[a-zA-Z0-9]+$', message='Логин должен содержать только латинские буквы и цифры')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен для заполнения'),
        Length(min=8, max=32, message='Пароль должен быть от 8 до 32 символов'),
        Regexp(r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).+$',
               message='Пароль должен содержать цифры, латинские буквы (строчные и заглавные) и спецсимволы')
    ])
    password_confirm = PasswordField('Повторите пароль', validators=[
        DataRequired(message='Повторите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])

    def validate_login(self, field):
        from app.models import storage
        if storage.get_user_by_login(field.data):
            raise ValidationError('Пользователь с таким логином уже существует')


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[
        DataRequired(message='Введите логин')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль')
    ])

class OrderForm(FlaskForm):
    pickup_address = StringField('Откуда забрать', validators=[
        DataRequired(message='Укажите адрес отправления'),
        Length(min=5, max=255, message='Адрес должен быть не менее 5 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z0-9\s\.,\-]+$', message='Адрес содержит недопустимые символы')
    ])
    delivery_address = StringField('Куда доставить', validators=[
        DataRequired(message='Укажите адрес доставки'),
        Length(min=5, max=255, message='Адрес должен быть не менее 5 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z0-9\s\.,\-]+$', message='Адрес содержит недопустимые символы')
    ])
    courier_date = DateField('Дата подачи курьера', validators=[
        DataRequired(message='Укажите дату подачи курьера')
    ])
    recipient_phone = TelField('Телефон получателя', validators=[
        DataRequired(message='Укажите телефон получателя'),
        Regexp(r'^(\+7|8)[0-9]{10}$',
               message='Введите корректный номер телефона (например: +78005553535 или 88005553535)')
    ])
    distance = FloatField('Расстояние', validators=[
        DataRequired(message='Укажите расстояние'),
        NumberRange(min=0.001, max=70, message='Расстояние должно быть от 0.001 до 70 км')
    ])
    tariff = SelectField('Тариф', choices=[
        ('dohodyaga', 'Доходяга'),
        ('busik', 'Бусик'),
        ('skorohod', 'Скороход')
    ], validators=[DataRequired(message='Выберите тариф')])
    promo_code = StringField('Промокод', validators=[
        Optional(),
        Length(max=20, message='Промокод не может быть длиннее 20 символов')
    ])

    def validate_courier_date(self, field):
        if field.data and field.data < datetime.now().date():
            raise ValidationError('Дата подачи курьера не может быть в прошлом')


class ChangeDataForm(FlaskForm):
    lastname = StringField('Фамилия', validators=[
        Optional(),
        Length(min=2, max=50, message='Фамилия должна быть от 2 до 50 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z]+$', message='Фамилия должна содержать только буквы')
    ])
    firstname = StringField('Имя', validators=[
        Optional(),
        Length(min=2, max=50, message='Имя должно быть от 2 до 50 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z]+$', message='Имя должно содержать только буквы')
    ])
    middlename = StringField('Отчество', validators=[
        Optional(),
        Length(max=50, message='Отчество не может быть длиннее 50 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z]*$', message='Отчество должно содержать только буквы')
    ])
    phone = TelField('Телефон', validators=[
        Optional(),
        Regexp(r'^(\+7|8)[0-9]{10}$',
               message='Введите корректный номер телефона (например: +78005553535 или 88005553535)')
    ])
    login = StringField('Логин', validators=[
        Optional(),
        Length(min=4, max=16, message='Логин должен быть от 4 до 16 символов'),
        Regexp(r'^[a-zA-Z0-9]+$', message='Логин должен содержать только латинские буквы и цифры')
    ])
    password = PasswordField('Новый пароль', validators=[
        Optional(),
        Length(min=8, max=32, message='Пароль должен быть от 8 до 32 символов'),
        Regexp(r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).+$',
               message='Пароль должен содержать цифры, латинские буквы (строчные и заглавные) и спецсимволы')
    ])
    password_confirm = PasswordField('Повторите пароль', validators=[
        EqualTo('password', message='Пароли не совпадают')
    ])


class OrderEditForm(FlaskForm):
    pickup_address = StringField('Откуда забрать', validators=[
        DataRequired(message='Укажите адрес отправления'),
        Length(min=5, max=255, message='Адрес должен быть не менее 5 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z0-9\s\.,\-]+$', message='Адрес содержит недопустимые символы')
    ])
    delivery_address = StringField('Куда доставить', validators=[
        DataRequired(message='Укажите адрес доставки'),
        Length(min=5, max=255, message='Адрес должен быть не менее 5 символов'),
        Regexp(r'^[а-яА-Яa-zA-Z0-9\s\.,\-]+$', message='Адрес содержит недопустимые символы')
    ])
    courier_date = DateField('Дата подачи курьера', validators=[
        DataRequired(message='Укажите дату подачи курьера')
    ])
    recipient_phone = TelField('Телефон получателя', validators=[
        DataRequired(message='Укажите телефон получателя'),
        Regexp(r'^(\+7|8)[0-9]{10}$',
               message='Введите корректный номер телефона (например: +78005553535 или 88005553535)')
    ])
    distance = FloatField('Расстояние', validators=[
        DataRequired(message='Укажите расстояние'),
        NumberRange(min=0.001, max=70, message='Расстояние должно быть от 0.001 до 70 км')
    ])
    tariff = SelectField('Тариф', choices=[
        ('dohodyaga', 'Доходяга'),
        ('busik', 'Бусик'),
        ('skorohod', 'Скороход')
    ], validators=[DataRequired(message='Выберите тариф')])

    def validate_courier_date(self, field):
        if field.data and field.data < datetime.now().date():
            raise ValidationError('Машину времени, к сожалению, пока не изобрели=((((((((((((((')