from datetime import timedelta
from flask import Flask, request, redirect, url_for, session, flash
from flask_login import UserMixin, LoginManager
from secrets import token_hex
from ssp.config import Config
from ssp.logger import logger
from ssp.notificator import Emailer

# Flask app
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=Config.SESSION_DAYS)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=Config.SESSION_DAYS)
# secret key для шифрования данных сессий и форм
app.secret_key = token_hex(20)
# настройки SMTP
app.config['MAIL_SERVER'] = Config.MAIL_SERVER
app.config['MAIL_PORT'] = Config.MAIL_PORT
app.config['MAIL_USE_TLS'] = Config.MAIL_USE_TLS
app.config['MAIL_DEFAULT_SENDER'] = Config.MAIL_DEFAULT_SENDER

# Login system
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Для доступа к странице нужно авторизоваться'


class User(UserMixin):
    def __init__(self, login, password=0):
        self.login = login
        self.password = password

    @property
    def id(self):
        return self.login


@login_manager.user_loader
def load_user(user_id):
    u = User(user_id)
    return u


"""@login_manager.unauthorized_handler
def unauthorized_callback():
    if not 'auth' in session:
        logger.info(msg=f"Unauthorized access detected! {request.environ.get('HTTP_X_REAL_IP', request.remote_addr)}, {request.environ['REMOTE_ADDR']} ")
        if not Config.DEV_ENV:
            # sendmail
            html_page = f'</br></br> Someone tried to break the authentication</br> Their IP are:</br>IP address: {request.environ["REMOTE_ADDR"]}' \
                        f'</br>IP address after Nginx: {request.environ["HTTP_X_REAL_IP"]} '
            mail = Emailer(subject='WARNING - Unauthorized access detected!', html_file=html_page)
            mail.send_mail(app=app)
    flash('Для доступа к старнице нужно авторизоваться')
    return redirect(url_for('login'))"""

from ssp import routes