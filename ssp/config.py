import os
from secrets import token_hex


class Config:

    # Common
    SSP_URL = 'https://whatever.ru/'
    MAILDOMAIN = 'whatever.ru'
    URL_FAQ = 'https://confluence.whatever.ru/pages/viewpage.action?pageId=34766975'
    URL_CDE = 'https://confluence.whatever.ru/display/whatever'
    URL_GITLAB = 'https://gitlab.whatever.ru'
    MAILTO = 'whatever@whatever.ru'
    SESSION_DAYS = 1
    APP_TOKEN = token_hex(20)
    DEV_ENV = os.environ.get("APPDATA")
    ADMINS = ['whatever@whatever.ru', 's.whatever@whatever.ru']  # LIST - admin section access
    cde_list = list(range(100, 121))

    # Active Directory
    # создание УЗ
    AD_SERVER =  'whatever.local' #'10.195.140.10'
    AD_USER = 'whatever\ssp-ad-write'    # Используя NTLM, вы используете шаблон DOMAIN \ user, и он найдет настоящего пользователя в Active Directory.
                                    # При использовании простой аутентификации LDAP вы должны указать dn пользователя.
    AD_PASSWORD = os.environ.get("AD_PASSWORD")
    AD_SEARCH_TREE = 'dc=whatever,dc=local'
    AD_DOMAIN_NAME = 'whatever.local'
    USER_OU = 'OU=Users,DC=whatever,DC=LOCAL'
    # авторизация
    AD_AUTH_SERVER = AD_SERVER  # 'whatever.whatever.org'
    AD_AUTH_SEARCH_TREE = AD_SEARCH_TREE  # 'dc=whatever,dc=org'
    AD_AUTH_DOMAIN_NAME = AD_DOMAIN_NAME  # 'whatever.org'

    # SMTP
    MAIL_DEFAULT_RCPT = ['whatever@whatever.ru', 's.whatever@whatever.ru']  #  LIST 'whatever@whatever.ru'
    BCC = ['b.whatever@whatever.ru']  # LIST BCC for mails to users and managers
    MAIL_SERVER = '10.195.105.29'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_DEFAULT_SENDER = 'whatever@whatever.ru'


