import re
from secrets import token_hex
from flask import render_template, request, redirect, session, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from ssp import app, User
from ssp.forms import UserForm, LoginForm
from ssp.generator import Generator
from ssp.notificator import Emailer
from ssp.constructor import Constructor
from ssp.ldap import LdapConnector
from ssp.logger import logger
from ssp.config import Config

SSP_URL = Config.SSP_URL
MAILDOMAIN = Config.MAILDOMAIN
URL_FAQ = Config.URL_FAQ
URL_CDE = Config.URL_CDE
URL_GITLAB = Config.URL_GITLAB
MAILTO = Config.MAILTO

constants = {}
for variable in ["URL_FAQ", "URL_CDE", "MAILTO", "URL_GITLAB"]:
    constants[variable] = eval(variable)

# database to store session independent data
db = {}


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        user = User(login=str(request.form.get('login')), password=str(request.form.get('password')))
        input_user = LdapConnector(attr='sAMAccountName', value=user.login)
        input_user.trylogin = user.login
        input_user.trypassword = user.password

        if input_user.try_connection():
            login_user(user, remember=form.remember.data)
            logger.info(msg=f'User logged in: {current_user.login}, auth: {current_user.is_authenticated} ')
            new_url = request.args.get('next')
            return redirect(new_url or url_for('home'))
        else:
            flash('Ошибка входа')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logger.info(msg=f'User logged out: {current_user.login}, auth: {current_user.is_authenticated} ')
    logout_user()
    session.clear()
    flash('Выполнен выход', 'success')
    return redirect(url_for('login'))

@app.route('/db')
#@login_required
def show_database():
    if session.get('email') in Config.ADMINS:
        return render_template('database.html', db=db, link=SSP_URL)

    logger.info(msg=f'User logged into DB: {current_user.login}, auth: {current_user.is_authenticated} ')
    logger.info(msg=f"Unauthorized access detected! DB {request.environ.get('HTTP_X_REAL_IP', request.remote_addr)}, {request.environ['REMOTE_ADDR']} ")
    if not Config.DEV_ENV:
        # sendmail
        html_page = f'</br></br> Unauthorized access detected. Page - DB' \
                    f'</br> Their IP are:</br>IP address: {request.environ["REMOTE_ADDR"]}' \
                    f'</br>IP address after Nginx: {request.environ["HTTP_X_REAL_IP"]} ' \
                    f'</br> Login: {current_user.login}'
        mail = Emailer(subject='WARNING - Unauthorized access detected!', html_file=html_page)
        mail.send_mail(app=app)
    return render_template('chucknorris.html')

@app.route('/start')
@app.route('/', methods=['GET', 'POST'])
#@login_required
def home():
    logger.info(msg=f'session before pop: {session}')
    # при перехорде на главную страницу список аккаунтов для сессии очищается
    if 'accounts' in session:
        session.pop('accounts')
    if 'current_id' in session:
        session.pop('current_id')
    logger.info(msg=f'session after pop: {session}')

    return redirect(url_for('processing'))

@app.route('/request', methods=['post', 'get'])
#@login_required
def processing():

    form = UserForm()
    logger.info(msg=f"Method is {request.method}")

    # форма отправлена (post) и прошла валидацию
    if form.validate_on_submit():
        logger.info(msg=f"Validate on submit")
        # запрос к данным формы
        second_name = str(request.form.get('second_name'))
        first_name = str(request.form.get('first_name'))
        middle_name = request.form.get('middle_name')
        login = request.form.get('login')
        email = request.form.get('email')
        phone = str(request.form.get('phone'))
        company = str(request.form.get('company'))
        cde = str(request.form.get('cde'))
        sd_number = str(request.form.get('sd_number'))
        external = str(request.form.get('external'))
        logger.info(msg=f"Введен login {login}, email {email}")
        logger.info(msg=f'Middle data and type: {middle_name} {type(middle_name)} {len(middle_name)}')

        # Проверка и преобразование логина
        if re.search('@', login):
            login = login.split('@')[0]
        re_dev = re.search('_dev', login)
        re_ext = re.search('_ext', login)
        if re_dev or re_ext:
            logger.info(msg=f"Пользователь ввел логи с постфиксом(dev, ext) {login}. Хвала!!! ")
        else:
            maildomain = email.split('@')[1]
            login = f'{login}_dev' if maildomain == MAILDOMAIN else f'{login}_ext'
            logger.info(msg=f"Преобразованный login {login}")

        # Проверка на добавление повтоного аккаунта
        if 'accounts' in session:
            logger.info(msg=f"Добавление 2 и выше аккаунтов")
            cn = f"{second_name} {first_name} {middle_name}".strip()
            logger.info(msg=cn)
            for account in session.get('accounts'):
                cn_in_session = f"{account.get('second_name')} {account.get('first_name')} {account.get('middle_name')}".strip()
                logger.info(msg=f"CN in session: {cn_in_session}")
                if cn == cn_in_session or login == account.get('login'):
                    logger.info(msg=f"Введены повторные данные")
                    flash('Вы уже добавили аккаунт с таким ФИО или Login')
                    return render_template('request.html', form=form, dubbleinput = 1, accounts=session['accounts'],  constants=constants, admins=Config.ADMINS)

        # Проверяем наличие аккаунтов в переменной сессии key accounts
        # Если добавляется второй и выше аккаунт, увеличиваем индекс
        if 'accounts' in session:
            session['current_id'] = len(session['accounts']) + 1
            session.modified = True
        else:
            session['current_id'] = 1
            session.modified = True

        user = {
            'id': session['current_id'], #current_id
            'second_name': second_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'login': login,
            'email': email,
            'company': company,
            'phone': phone,
            'cde': cde,
            'sd_number': sd_number
        }

        # добавление второго и последующий аккаунтов
        if 'accounts' in session:
            try:
                accounts = session.get('accounts')
                accounts.append(user)
                session['accounts'] = accounts
                session.modified = True
            except:
                logger.info(msg=f"Неизвестная ошибка")
        else:
            session['accounts'] = [user]
            session.modified = True

        logger.info(msg=f"Данные формы добавлены {session['accounts']}")
        ###flash(f'Добавлен аккаунт для {form.second_name.data} {form.first_name.data}!', 'success')
        return redirect(url_for('processing'))

    # Проверяем наличие аккаунтов в переменной сессии key accounts, если есть - выводим их
    if 'accounts' in session:
        return render_template('request.html', form=form, accounts=session['accounts'], constants=constants, admins=Config.ADMINS)
    else:
        return render_template('request.html', form=form, constants=constants, admins=Config.ADMINS)

@app.route('/remove_item')
#@login_required
def remove():
    account_id_raw = request.args.get('id')
    # проверить что переход на страницу был не через строку браузера
    if not account_id_raw:
        return redirect(url_for('home'))
    else:
        account_id = int(request.args.get('id'))
        logger.info(msg=f'ACCOUNT_IDs: {account_id, len(str(account_id)), type(account_id)})')

    for i in range(len(session['accounts'])):
        logger.info(msg=i)
        logger.info(msg=session['accounts'])
        if (session['accounts'][i]).get('id') == account_id:  ###if session['accounts'][i]['id'] == account_id:
            accounts = session.get('accounts')
            del accounts[i]
            session['accounts'] = accounts
            session.modified = True
            break

    return redirect(url_for('processing'))

@app.route('/finish')
#@login_required
def finish():
    # проверить что переход на страницу был не через строку браузера
    if 'accounts' not in session:
        logger.info(msg='finish: accounts not in session')
        return redirect(url_for('home'))
    # get uniq record to store the session created accounts in global var
    accounts_id = token_hex(20)
    accounts_to_create = list(session['accounts']) # copy list of session dict
    # add accounts to create to global (non session depended) var
    db[accounts_id] = accounts_to_create
    # add manager email
    db[f'{accounts_id}_mail'] = session.get('email')
    logger.info(msg=f'Обновлена БД {db}')
    # send mail to admins for moderation
    # add csv - like data
    construct = Constructor()
    csv = construct.csv_file_gen(accounts_to_create)
    html_page = construct.html_page_gen_admin(accounts_to_create, SSP_URL, accounts_id) + f"</br>{csv}"
    try:
        if not Config.DEV_ENV:
            mail_admins = Emailer(subject='Заявка на создание аккаунтов', html_file=html_page)
            mail_admins.send_mail(app=app)
        else:
            logger.info(msg=f"Программа запущена на ПК разработчика, почта не отправляется")
    except:
        return f"<h1>Ошибка</h1></br><h2> Произошла ошибка отправки сообщения модерации. Сообщите по адресу {MAILTO}</h2></br>{csv}"

    # clear user session
    if 'accounts' in session:
        session.pop('accounts')
    if 'current_id' in session:
        session.pop('current_id')

    temp_link = ''
    if Config.DEV_ENV:
        temp_link = f'http://127.0.0.1:5000/arbitration?id={accounts_id}&accept=1'  # run on home pc
    else:
        temp_link = 'test'
    return render_template('finish.html', accounts=accounts_to_create, mailto=MAILTO, temp_link=temp_link, csv=csv, admins=Config.ADMINS)

@app.route('/arbitration')
#@login_required
def arbitration():
    # only admin access
    if session.get('email') not in Config.ADMINS:
        logger.info(msg=f'User logged into Arbitration: {current_user.login}, auth: {current_user.is_authenticated} ')
        logger.info(
            msg=f"Unauthorized access detected! Arbitration {request.environ.get('HTTP_X_REAL_IP', request.remote_addr)}, {request.environ['REMOTE_ADDR']} ")
        if not Config.DEV_ENV:
            # sendmail
            html_page = f'</br></br> Unauthorized access detected. Page - Arbitration' \
                        f'</br> Their IP are:</br>IP address: {request.environ["REMOTE_ADDR"]}' \
                        f'</br>IP address after Nginx: {request.environ["HTTP_X_REAL_IP"]} ' \
                        f'</br> Login: {current_user.login}'
            mail = Emailer(subject='WARNING - Unauthorized access detected!', html_file=html_page)
            mail.send_mail(app=app)
        return render_template('chucknorris.html')

    logger.info(msg=f"DB empty, {len(db)}, {db}")
    logger.info(msg=f'User logged in to Arbitration: {current_user.login}, auth: {current_user.is_authenticated} ')
    # проверить что переход на страницу был не через строку браузера или все заявку уже обработаны
    if len(db) == 0:
        return f"</br></br><h1>В базе данных отсутствуют ожидающие одобрения заявки</h1>"
    uniq_str = request.args.get('id')
    accept = request.args.get('accept')
    logger.info(msg=f"Id requested, {uniq_str}")

    # проверить заявка с указанным id имеется в базе
    if uniq_str not in db:
        logger.info(msg=f"Incorrect Id, {uniq_str}")
        return f"</br></br><h1>Указанной заявки нет в базе. Вероятно она уже обработана. Проверьте почту</h1></br><h3>uniq_str, accept, db are:{uniq_str}, {accept}, {db} </h3>"
    if accept == '1':
        logger.info(msg=f"Got accept, about to create {db.get(uniq_str)}")
        #  creator email
        creator_email = [db.get(f'{uniq_str}_mail')]
        # create accounts
        # prepare the list of accounts
        # add password
        accounts_with_sec = list(db[uniq_str])
        for account in accounts_with_sec:
            password = Generator()
            account['password'] = password.get_password()
        #logger.info(msg=f"DB with secrets, {accounts_with_sec}")
        # create ad accounts
        create_user = LdapConnector(users=accounts_with_sec)
        ad_result = create_user.create_ad_user()
        logger.info(msg=f"LDAP results {ad_result}")
        construct = Constructor()
        if ad_result.get('result') != 0:  ###if ad_result['result'] != 0:
            logger.error(msg=f"Ошибка LDAP при создании аккаунтов {ad_result}")
            if not Config.DEV_ENV:
                # send source data to admins
                # replace source data with csv
                html_page = str(ad_result) + '\n' + construct.csv_file_gen(accounts_with_sec)
                ldap_error_mail = Emailer(subject='Ошибка LDAP при создании аккаунтов', html_file=html_page)
                ldap_error_mail.send_mail(app=app)
                # Удаление созданных аккаунтов из глобавльной переменной
            db.pop(uniq_str)
            db.pop(f'{uniq_str}_mail')
            return f"</br></br><h1>LDAP ERROR!</h1></br>{html_page}</br><h3>uniq_str, accept, db are:{uniq_str}, {accept}, {db} </h3>"
        else:
            # send email to users
            account_creation_results = []
            for account in accounts_with_sec:
                html_page = construct.html_page_gen_user(account, constants)
                account_creation_result = {
                    'Name': f"{account['second_name']} {account['first_name']} {account['middle_name']}",
                    'Login': account['login'],
                    'Password': account['password'],
                    'Email': account['email'],
                    'Send': ''}
                if not Config.DEV_ENV:

                    try:
                        # DEBUG
                        recipient = [account['email']]
                        mail_user = Emailer(subject='Создана учетная запись DevOpsCloud', html_file=html_page, rcpt_mail=recipient)
                        mail_user.send_mail(app=app)  # , bcc=Config.BCC)
                        mail_user_adm = Emailer(subject='Создана учетная запись DevOpsCloud', html_file=html_page)
                        mail_user_adm.send_mail(app=app)
                        account_creation_result['Send'] = True
                    except:
                        logger.error(msg=f"Не удалось отправить письмо на адрес {account['email']}")
                        html_page = f'не удалось отправить письмо на адрес {account["email"]}'
                        mail_user_adm = Emailer(subject='Не удалось отправить сообщение. DevOpsCloud', html_file=html_page)
                        mail_user_adm.send_mail(app=app)
                        account_creation_result['Send'] = False

                account_creation_results.append(account_creation_result)

        if not Config.DEV_ENV:
            #mail to manager
            construct = Constructor()
            html_page = construct.html_page_gen_manager(account_creation_results)
            logger.info(msg=f"Managers html {html_page}")
            mail_manager = Emailer(subject='Учетные записи были успешно созданы!', html_file=html_page, rcpt_mail=creator_email)
            logger.info(msg=f"Creator email {creator_email}, type {type(creator_email)}")
            mail_manager.send_mail(app=app, bcc=Config.BCC)

        logger.info(msg=f"Аккаунты созданы, db {db}")
        # Удаление созданных аккаунтов из глобавльной переменной
        db.pop(uniq_str)
        db.pop(f'{uniq_str}_mail')
        logger.info(msg=f"Содержимое db после очистки, accept {db}")
        return f"</br></br><h1>Учетные записи были успешно созданы!</h1></br>uniq_str, accept, db are:{uniq_str}, {accept}, {db}"

    #Удаление созданных аккаунтов из глобавльной переменной
    construct = Constructor()
    csv = construct.csv_file_gen(list(db[uniq_str]))
    creator_email = db.get(f'{uniq_str}_mail')
    db.pop(uniq_str)
    db.pop(f'{uniq_str}_mail')
    logger.info(msg=f"Содержимое db после очистки, decline {db}")
    # send mail to manager
    html_page = f'</br></br><h1>По каким-то причином не удалось с Вами связаться. Сообщите на {MAILTO}</h1>'
    mail_manager = Emailer(subject='Заявка на создание учетных записей отклонена!', html_file=html_page, rcpt_mail=creator_email)
    #  mail_manager.send_mail(app=app, bcc=Config.BCC)
    return f"</br></br><h1>Заявка на создание учетных записей отклонена!</h1></br>{csv}</br><h3>uniq_str, accept, db are:{uniq_str}, {accept}, {db} </h3>"
