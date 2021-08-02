"""
Module for generate HTML/ CSV text from List of Dict
"""
from flask import session


class Constructor():

    @staticmethod
    def html_table_gen(accounts):
        table = ''
        start_table = f"""
            <table cellpadding="7" border="2">
              <tr style="font-size: 15px; font-weight: bold">
                <td>Фамилия</td>
                <td>Имя</td>
                <td>Отчество</td>
                <td>Login</td>
                <td>Email</td>
                <td>Компания</td>
                <td>Телефон</td>
                <td>CDE</td>
                <td>Номер заявки SD</td>
              </tr>
            """
        table += start_table
        for account in accounts:
            tr = f"""
              <tr>
                <td>{account['second_name']}</td>
                <td>{account['first_name']}</td>
                <td>{account['middle_name']}</td>
                <td>{account['login']}</td>
                <td>{account['email']}</td>
                <td>{account['company']}</td>
                <td>{account['phone']}</td>       
                <td>{account['cde']}</td>
                <td>{account['sd_number']}</td>
              </tr>
            """

            table += tr

        end_table = f"""
        </table>
        """
        table += end_table

        return table

    @staticmethod
    def html_table_gen_pwd(accounts):
        table = ''
        start_table = f"""
            <table cellpadding="7" border="2">
              <tr style="font-size: 15px; font-weight: bold">
                <td>Имя</td>
                <td>Login</td>
                <td>Password</td>
                <td>Email</td>
                <td>Отправка сообщения</td>
              </tr>
            """
        table += start_table
        for account in accounts:
            if account.get('Send'):
                send_result = '<td>Отправлено</td>'
            else:
                send_result = '<td style="color: red">Ошибка</td>'
            tr = f"""
              <tr>
                <td>{account['Name']}</td>
                <td>{account['Login']}</td>
                <td>{account['Password']}</td>
                <td>{account['Email']}</td>
                {send_result}
              </tr>
            """

            table += tr

        end_table = f"""
        </table>
        """
        table += end_table

        return table

    @staticmethod
    def html_page_gen_admin(accounts, link, uniq_str):
        link_accept = f'{link}/arbitration?id={uniq_str}&accept=1'
        link_decline = f'{link}/arbitration?id={uniq_str}&accept=0'
        table = Constructor.html_table_gen(accounts)
        style = '''   
        .divgreen {border: 1px outset black;
        background-color: green;
        text-align: center;
        }
        .divred {border: 1px outset black;
        background-color: red;
        text-align: center;
        }
        '''
        html_page = f'''
        <html>
        <head>
        <style>
        {style}
        </style>
        </head>
        <body>
        <h2>Заявка на создание аккаунтов в DevOpsCloud</h2>
        </br>
        <div  style="font-size: 15px; font-weight: bold">От: {session.get('cn')} ({ session.get('email') })</div>
        </br>
        <div>
        {table}
        </div>
        </br></br>
        <div >
            <a href={link_accept}><font color=green>Accept</font></a>
        </div>
        </br>
        <div >
            <a href={link_decline}><font color=red>Decline</font></a>
        </div>
        </br>
        </body>
        </html>
        '''
        return html_page

    @staticmethod
    def html_page_gen_manager(accounts):
        table = Constructor.html_table_gen_pwd(accounts)
        style = '''   
        .divgreen {border: 1px outset black;
        background-color: green;
        text-align: center;
        }
        .divred {border: 1px outset black;
        background-color: red;
        text-align: center;
        }
        '''
        html_page = f'''
        <html>
        <head>
        <style>
        {style}
        </style>
        </head>
        <body>
        <h2>Учетные записи домена DevOpsCloud созданы, пароли отправлены на указанные адреса email</h2>
        </br></br>
        <div>
        {table}
        </div>
        </br>
        <div>Если был указан несуществующий адрес Email письмо доставлено не будет</div>
        </br></br>
        </body>
        </html>
        '''
        return html_page

    @staticmethod
    def html_page_gen_user(account, links):
        # Gitlab FAQ links
        # USername Password

        html_page = f'''
        <html>
        <head>
        </head>
        <body>
        <h2>Учетная запись в DevOpsCloud</h2>
        </br></br>
        <div>Здравствуйте {account['first_name']}. Для вас создана учетная запись в домене DOC:</div>
        </br></br>
        <table cellpadding="7" border="2">
        <tr>
            <td style="font-weight: bold">Login</td>
            <td>{account['login']}</td>
        </tr>
        <tr>
            <td style="font-weight: bold">Password</td>
            <td>{account['password']}</td>
        </tr>
        </table>
        </br>
        </br>
        <div >
            <a href={links['URL_GITLAB']}><font color=blue>Gitlab</font></a>
        </div>
    
        <div >
            <a href={links['URL_FAQ']}><font color=blue>FAQ</font></a>
        </div>
        </br>
        </body>
        </html>
        '''
        return html_page

    @staticmethod
    def csv_file_gen(accounts):
        string = ''
        for account in accounts:
                newstring = f"{account['second_name']};{account['first_name']};"
                if 'middle_name' in account:
                    newstring = newstring + f"{account['middle_name']};"
                else:
                    newstring = newstring + ";"
                newstring = newstring + f"{account['login']};{account['email']};;;{account['company']};"
                if 'phone' in account:
                    newstring = newstring + f"{account['phone']};"
                else:
                    newstring = newstring + ";"
                newstring = newstring + f"{account['cde']}"
                string = string + '\n' + newstring
        return string
