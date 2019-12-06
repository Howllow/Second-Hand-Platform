import pymysql
from pymysql.connections import Connection
from db.utils import *
from typing import Dict

def login_user(data: Dict[str, str], conn: Connection):
    """
    :param data:
        python dictionary, containing keys as follows:
            username: string (len < 20)
            password: string (len < 20)
    :param conn:
        pymysql connection
    :return:
        log_message:
            state:
                0 for success
                1 for not found
                2 for wrong password
                3 for wrong data

    """
    log_message = dict()

    if not check(['username', 'password'], data, 'login'):
        log_message['state'] = 3
        return log_message

    cursor = conn.cursor()
    sql = 'select username from users;'
    cursor.execute(sql)
    rows = cursor.fetchall()
    rows = [row[0] for row in rows]

    if data['username'] not in rows:
        cursor.close()
        logging.debug(F'user {data["username"]} not found')
        log_message['state'] = 1
        return log_message

    sql = "select password from users where username = '{data['username']'};"
    cursor.execute(sql)
    real_pwd = cursor.fetchall()[0][0]


    if real_pwd != data['password']:
        cursor.close()
        logging.debug(F'login for account {data["account"]} wrong password')
        log_message['state'] = 2
        return log_message

    else:
        logging.debug(F'login for account {data["account"]} succeeded')
        log_message['state'] = 0
        sql = "select authority from users where username = '{data['username']';"
        cursor.execute(sql)
        log_message['ident'] = cursor.fetchall()[0][0]
        cursor.close()
        return log_message



def register_user(data: dict, conn: Connection):
    """
        :param data:
            python dictionary, containing keys as follows:
                username: string (len < 20)
                password: string (len < 20)
                nickname: string
                gender: int
                phone: string
                indent: int
        :param conn:
            pymysql connection
        :return:
            reg_message:
                state:
                    0 for success
                    1 for username duplicated
                    2 for nickname duplicated
                    3 for wrong data

    """

    reg_message = dict()

    if not check(['username', 'password', 'nickname', 'gender', 'phone', 'indent'], data, 'register'):
        reg_message['state'] = 3
        return reg_message

    cursor = conn.cursor()

    sql = 'select username from user'
    cursor.execute(sql)
    rows = cursor.fetchall()
    usernames = [row[0] for row in rows]

    sql = 'select nickname from user'
    cursor.execute(sql)
    rows = cursor.fetchall()
    nicknames = [row[0] for row in rows]

    for row in usernames:
        if data['username'] == row:
            cursor.close()
            logging.debug(F'username {data["username"]} already exists')
            reg_message['state'] = 1
            return reg_message

    for row in nicknames:
        if data['nickname'] == row:
            cursor.close()
            logging.debug(F'nickname {data["nickname"]} already exists')
            reg_message['state'] = 2
            return reg_message

    if data['indent'] == 0:
        sql = F"insert into users (username, password, nickname, gender, phone, authority)" \
              F" VALUE ('{data['username']}', '{data['password']}', '{data['nickname']}', '{data['gender']}', "\
              F"'{data['phone']}', '{data['indent']}');"
        cursor.execute(sql)

        conn.commit()
        cursor.close()

    elif data['indent'] == 1:
        sql = F"insert into requests (username, password, nickname, gender, phone, authority)" \
              F" VALUE ('{data['username']}', '{data['password']}', '{data['nickname']}', '{data['gender']}', " \
              F"'{data['phone']}', '{data['indent']}');"
        cursor.execute(sql)

        conn.commit()
        cursor.close()

    logging.debug(F'register for account {data["account"]} succeeded')
    reg_message['state'] = 0
    return reg_message











