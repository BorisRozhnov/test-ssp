from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, FieldList
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
from ssp.config import Config


class UserForm(FlaskForm):
    second_name = StringField("Фамилия: ", validators=[DataRequired(), Length(min=2, max=30, message='Введите от 2 до 30 символов'),
                                                       Regexp('^[a-zA-ZА-Яа-я-]{2,30}$', message='Фамилия не может содержать цифры и спецсимволы')])
    first_name = StringField("Имя: ", validators=[DataRequired(), Length(min=2, max=30, message='Введите от 2 до 30 символов'),
                                                  Regexp('^[a-zA-ZА-Яа-я]{2,30}$', message='Имя не может содержать цифры и спецсимволы')])
    middle_name = StringField("Отчество: ")
    login = StringField("Login: ", validators=[DataRequired(), Length(min=3, max=16, message='Введите от 3 до 16 символов'),
                                               Regexp('^[^0-9][A-Za-z0-9_.-]{2,15}$', message='Логин должен начинаться с буквы и содержать от 3 до 16 символов. '
                                                                                              'Разрешены латинские буквы, цифры, символы_ - . Нельзя использовать @')],
                        render_kw={"placeholder": "bob"} )
    email = StringField("Email: ", validators=[DataRequired(message='Введите корректный email. На него будет выслан пароль'),
                                               Email(message='Введите корректный email. На него будет выслан пароль')],
                        render_kw={"placeholder": "bob@whatever.ru"})
    company = StringField("Компания: ", validators=[DataRequired(), Length(min=2, max=30, message='Введите от 2 до 20 символов')])
    phone = StringField("Номер телефона: ")
    #cde = StringField("CDE: ", validators=[DataRequired(), Length(min=3, max=3, message='Введите корректный CDE'),
    #                                       Regexp('^[1-1][0-1][0-9]$', message='Введите корректный CDE')])
    cde = SelectField('Номер CDE',choices=Config.cde_list)
    sd_number = StringField("Номер заявки в SD: ", render_kw={"placeholder": "не заполнять"})#, validators=[DataRequired(), Length(min=7, max=7, message='Номер заяки SD состоит из 7 цифр'),
                                                  #             Regexp('^[0-9]{7,7}$', message='Номер заяки SD не может содержать буквы и спецсимволы')])
    external = BooleanField("Внешний пользователь")
    submit = SubmitField("Добавить аккаунт")

    def validate_login(self, login):
        if login.data == 'AAA':
            raise ValidationError('Test custom validator. Login is AAA.')

    def validate_email(self, email):
        if 'ops.local' in email.data:
            raise ValidationError('ops.local не является Email адресом')


class LoginForm(FlaskForm):
    login = StringField("Login: ", validators=[DataRequired(), Length(min=2, max=30, message='Введите от 3 до 30 символов')],
                                               #Regexp('^[^0-9][A-Za-z0-9_.-\\]{2,29}$', message='Введите корректный логин домена без знака @')],
                        render_kw={"placeholder": "bob_dev"})
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=8, max=20, message='Введите от 8 до 20 символов.'),
                                               Regexp('^[^А-Яа-я]{8,20}$', message='В пароле не может быть кириллицы')])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Войти")
    