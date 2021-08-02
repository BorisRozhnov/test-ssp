from ldap3 import Server, Connection, SUBTREE, ALL, MODIFY_REPLACE, NTLM
from flask import session
from ssp.config import Config
from ssp.logger import logger


class LdapConnector:
    AD_SERVER = Config.AD_SERVER

    AD_USER = Config.AD_USER
    AD_PASSWORD = Config.AD_PASSWORD
    AD_SEARCH_TREE = Config.AD_SEARCH_TREE
    AD_DOMAIN_NAME = Config.AD_DOMAIN_NAME
    USER_OU = Config.USER_OU
    AD_AUTH_SERVER = Config.AD_AUTH_SERVER
    AD_AUTH_SEARCH_TREE = Config.AD_AUTH_SEARCH_TREE
    AD_AUTH_DOMAIN_NAME = Config.AD_AUTH_DOMAIN_NAME

    def __init__(self, attr=0, value=0, users=0):
        self.attr = attr
        self.value = value
        self.users = users

    @staticmethod
    def connect_ldap(adserver, aduser, adpassword):
        server = Server(adserver, get_info=ALL, use_ssl=True)
        global conn
        conn = Connection(server, user=aduser, password=adpassword, authentication=NTLM, auto_bind=True)

    def check_ad_user(self):
        if 'conn' not in globals():
            logger.info(msg=f"conn not in globals")
            self.connect_ldap(self.AD_SERVER, self.AD_USER, self.AD_PASSWORD)
        logger.info(msg=f"conn status {conn}")
        try:
            conn.bind()
        except:
            logger.error(msg=f"bind failed, reconnecting")
            self.connect_ldap(self.AD_SERVER, self.AD_USER, self.AD_PASSWORD)
        filter_str = f"(&(objectCategory=Person)({self.attr}={self.value}))"
        conn.search(self.AD_SEARCH_TREE, filter_str, SUBTREE,
                    attributes=['cn', 'name', 'displayName', 'sAMAccountName', 'mail', 'distinguishedName']
                    )
        logger.info(msg=f'LDAP search result: {conn.result}')
        logger.info(msg=f'LDAP search data: {conn.entries}')

        if conn.entries:
            return conn.entries
        else:
            return None

    def create_ad_user(self):
        for user in self.users:
            if 'conn' not in globals():
                logger.info(msg=f"conn not in globals")
                self.connect_ldap(self.AD_SERVER, self.AD_USER, self.AD_PASSWORD)
            try:
                conn.bind()
            except:
                logger.error(msg=f"bind failed, reconnecting")
                self.connect_ldap(self.AD_SERVER, self.AD_USER, self.AD_PASSWORD)
            display_name = f"{user['second_name']} {user['first_name']} {user['middle_name']}".strip()
            dn = f'CN={display_name},{self.USER_OU}'.strip()
            logger.info(msg=f"DN is {dn}")
            # Если телефон не введен ставим пробел
            if (len(user.get('phone')) == 0):
                 user['phone'] = ' '
            attr={'sAMAccountName':user['login'],
                  'userPrincipalName': f'{user["login"]}@{self.AD_DOMAIN_NAME}'.strip(),
                  'name': display_name,
                  'sn': user['second_name'],
                  'givenName': user['first_name'],
                  'mail': user['email'],
                  'displayName': display_name,
                  'company': user['company'],
                  'description': user['cde'],
                  'telephoneNumber': user['phone']
                  }

            logger.info(msg=f"Attr is {attr}")

            # create user
            conn.add(dn, ['user','organizationalPerson','person','top'], attr)
            logger.info(msg=f"Account creation result: {conn.result}")

            try:
                if conn.result.get('result') == 0:  ###if conn.result['result'] == 0:
                    # get random password
                    password = (user['password']).strip() #get_password()
                    logger.debug(msg=f"Password {password}")
                    # set the password --ttl/ssl is required(or ntlm ssp)--
                    conn.extend.microsoft.modify_password(dn, password,
                                                           old_password=None)  
                    logger.info(msg=f"Password set results {conn.result}")
                    # set password never expires and account unlocked
                    conn.modify(dn, changes={"userAccountControl": (MODIFY_REPLACE, [66048])})
                    logger.info(msg=f"Pwd never expires set results {conn.result}")

            except:
                logger.error(msg=f"Failed to create LDAP account {conn.result}")
                return conn.result

        # close the connection
        #conn.unbind()
        return conn.result

    def unbind(self, conn):
        conn.unbind()

    def try_connection(self):
        # Используя NTLM, вы используете шаблон DOMAIN \ user, и он найдет настоящего пользователя в Active Directory.
        # При использовании простой аутентификации LDAP вы должны указать dn пользователя.
        if '\\' in self.trylogin:
            logon_name = self.trylogin
        else:
            logon_name = self.AD_AUTH_DOMAIN_NAME.split('.')[0].upper() + "\\" + self.trylogin
        logger.info(msg=f"Попытка подключения к LDAP с login {logon_name}")
        server = Server(self.AD_AUTH_SERVER, get_info=ALL)  # use_ssl=False
        tryconn = Connection(server, user=logon_name, password=self.trypassword, authentication=NTLM)
        tryconn.bind()
        if (tryconn.result).get('result') != 0:  ###if tryconn.result['result'] != 0:
            logger.error(msg=f"Ошибка подключения к LDAP с login {logon_name}")
            logger.error(msg=f"LDAP error: {tryconn.result}")
            tryconn.unbind()
            return False
        filter_str = f"(&(objectCategory=Person)({self.attr}={self.value}))"
        tryconn.search(self.AD_AUTH_SEARCH_TREE, filter_str, SUBTREE,
                    attributes=['cn', 'name', 'displayName', 'sAMAccountName', 'mail', 'distinguishedName']
                    )
        trydata = tryconn.entries

        if len(trydata[0]['mail']) > 0: # empty email returns [], len 0
            session['email'] = str(trydata[0]['mail'])
            session['cn'] = str(trydata[0]['cn'])
            session['auth'] = Config.APP_TOKEN
            session.modified = True
            logger.info(msg=f"Подключение к LDAP с login {self.trylogin} успешно")
            tryconn.unbind()
            return True
        else:
            logger.error(msg=f"Не удалось определить mail: {self.trylogin} LDAP data: {trydata}")
            tryconn.unbind()
            return False
