import pymysql
from pymysql.connections import Connection
from db.utils import *
from typing import Dict
import datetime

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
            response_code:
                0 for success
                1 for not found
                2 for wrong password
                3 for wrong data
            ident:
                identity(authority)

    """
    log_message = dict()

    if not check(['username', 'password'], data, 'login'):
        log_message['response_code'] = 3
        return log_message

    cursor = conn.cursor()
    sql = 'select username from users;'
    cursor.execute(sql)
    rows = cursor.fetchall()
    rows = [row[0] for row in rows]

    if data['username'] not in rows:
        cursor.close()
        logging.debug(F'user {data["username"]} not found')
        log_message['response_code'] = 1
        return log_message

    sql = F"select password from users where username = '{data['username']}';"
    cursor.execute(sql)
    real_pwd = cursor.fetchall()[0][0]

    if real_pwd != data['password']:
        cursor.close()
        logging.debug(F'login for account {data["username"]} wrong password')
        log_message['response_code'] = 2
        return log_message

    else:
        logging.debug(F'login for account {data["username"]} succeeded')
        log_message['response_code'] = 0
        sql = F"select authority from users where username = '{data['username']}';"
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
                response_code:
                    0 for success
                    1 for username duplicated
                    2 for nickname duplicated
                    3 for wrong data

    """

    reg_message = dict()

    if not check(['username', 'password', 'nickname', 'gender', 'phone', 'ident', 'age'], data, 'register'):
        reg_message['response_code'] = 3
        return reg_message

    cursor = conn.cursor()

    sql = 'select username from users'
    cursor.execute(sql)
    rows = cursor.fetchall()
    usernames = [row[0] for row in rows]

    sql = 'select nickname from users'
    cursor.execute(sql)
    rows = cursor.fetchall()
    nicknames = [row[0] for row in rows]

    for row in usernames:
        if data['username'] == row:
            cursor.close()
            logging.debug(F'username {data["username"]} already exists')
            reg_message['response_code'] = 1
            return reg_message

    for row in nicknames:
        if data['nickname'] == row:
            cursor.close()
            logging.debug(F'nickname {data["nickname"]} already exists')
            reg_message['response_code'] = 2
            return reg_message

    if data['ident'] == 0:
        sql = F"insert into users (username, password, nickname, gender, phone, authority, age)" \
              F" VALUE ('{data['username']}', '{data['password']}', '{data['nickname']}', '{data['gender']}', "\
              F"'{data['phone']}', '{data['ident']}', '{data['age']}');"
        cursor.execute(sql)

        conn.commit()
        cursor.close()

    elif data['ident'] == 1:
        sql = F"insert into requests (username, password, nickname, gender, phone, age)" \
              F" VALUE ('{data['username']}', '{data['password']}', '{data['nickname']}', '{data['gender']}', " \
              F"'{data['phone']}', '{data['age']}');"
        cursor.execute(sql)

        conn.commit()
        cursor.close()

    logging.debug(F'register for account {data["username"]} succeeded')
    reg_message['response_code'] = 0
    return reg_message


def find_goods(data: dict, conn: Connection):
    """
            :param data:
                python dictionary, containing keys as follows:
                    keyword: string
                    type: string
            :param conn:
                pymysql connection
            :return:
                good_message:
                    response_code:
                        0 for success
                        1 for not found
                        2 for wrong data
                    good_list:
                        a list of goods including seller's nickname, price, good's name and id
    """

    good_message = dict()

    if not check(['keyword', 'type'], data, "find_good"):
        good_message['response_code'] = 2
        return good_message

    cursor = conn.cursor()
    sql = F"select G.goodname, U.nickname, G.price, G.goodsid from goods as G, users as U "\
          F"where sold=0 and type = '{data['type']}' and U.username=G.seller "\
          F"ORDER BY G.uptime ASC;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    good_message['response_code'] = 0
    good_list = []
    for row in rows:
        if is_keyword(data['keyword'], row[0]):
            good_list.append([row[0], row[1], row[2], row[3]])

    if len(good_list) == 0:
        good_message['response_code'] = 1
        return good_message

    good_message['good_list'] = good_list
    return good_message


def find_info(data: dict, conn: Connection):
    """
        :param data:
            python dictionary, containing keys as follows:
                goodsid: string
        :param conn:
            pymysql connection
        :return:
            info_message:
                response_code:
                    0 for success
                    1 for wrong data
                good_info:
                    goodname and description
    """

    info_message = dict()

    if not check(['goodsid'], data, "good_info"):
        info_message['response_code'] = 1
        return info_message

    info_message['response_code'] = 0
    cursor = conn.cursor()
    sql = F"select goodname, description from goods "\
          F"where goodsid = {data['goodsid']};"

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    info_message['good_info'] = [rows[0][0], rows[0][1]]
    return info_message


def add_cart(data: dict, conn: Connection):
    """
        :param data:
            python dictionary, containing keys as follows:
                username: string
                goodsid: string
        :param conn:
            pymysql connection
        :return:
            add_message:
                response_code:
                    0 for success
                    1 for wrong data
                good_list
    """

    add_message = dict()

    if not check(['goodsid', 'username'], data, "add_cart"):
        add_message['response_code'] = 2
        return add_message

    cursor = conn.cursor()
    sql = F"select goodsid from cart "\
          F"where username = '{data['username']}';"
    cursor.execute(sql)
    rows = cursor.fetchall()
    goodsids = [row[0] for row in rows]

    for id in goodsids:
        if int(data['goodsid']) == id:
            cursor.close()
            add_message['response_code'] = 1
            return add_message

    sql = F"insert into cart(goodsid, username) "\
          F"VALUE({data['goodsid']}, '{data['username']}');"

    cursor.execute(sql)
    conn.commit()
    cursor.close()

    add_message['response_code'] = 0
    return add_message


def find_cart(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               username: string
       :param conn:
           pymysql connection
       :return:
           add_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    cart_message = dict()

    if not check(['username'], data, "find_cart"):
        cart_message['response_code'] = 1
        return cart_message

    cursor = conn.cursor()
    sql = F"select G.goodname, U.nickname, G.price, G.goodsid from goods as G, cart as C, users as U "\
          F"where C.username='{data['username']}' and G.goodsid=C.goodsid and U.username=G.seller "\
          F"ORDER BY G.uptime ASC;"

    cursor.execute(sql)
    rows = cursor.fetchall()
    good_list = []
    for row in rows:
        good_list.append([row[0], row[1], row[2], row[3]])

    cart_message['good_list'] = good_list

    cursor.close()

    cart_message['response_code'] = 0

    return cart_message


def buy_good(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               username: string
               goodsid: string
       :param conn:
           pymysql connection
       :return:
           add_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    buy_message = dict()
    if not check(['username', 'goodsid'], data, "find_cart"):
        buy_message['response_code'] = 1
        return buy_message

    ntime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()
    sql = F"insert into orders(goodsid, buyer, time) "\
          F"VALUE({data['goodsid']}, '{data['username']}', '{ntime}');"

    cursor.execute(sql)
    conn.commit()

    sql = F"update goods set sold = 1 "\
          F"where goodsid = {data['goodsid']};"

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    buy_message['response_code'] = 0
    return buy_message


def remove_cart(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               username: string
               goodsid: string
       :param conn:
           pymysql connection
       :return:
           add_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    remove_message = dict()
    if not check(['username', 'goodsid'], data, 'remove cart'):
        remove_message['response_code'] = 1
        return remove_message

    cursor = conn.cursor()
    sql = F"delete from cart "\
          F"where goodsid = {data['goodsid']} and username = '{data['username']}';"

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    remove_message['response_code'] = 0
    return remove_message


def find_bought(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               username: string
       :param conn:
           pymysql connection
       :return:
           add_message:
               response_code:
                   0 for success
                   1 for wrong data
                good_list
    """

    bought_message = dict()
    if not check(['username'], data, 'find bought'):
        bought_message['response_code'] = 1
        return bought_message

    cursor = conn.cursor()
    sql = F"select G.goodname, U.nickname, O.time, G.goodsid from goods as G, orders as O, users as U "\
          F"where O.buyer='{data['username']}' and G.goodsid = O.goodsid and U.username=G.seller "\
          F"ORDER BY O.time ASC;"
    cursor.execute(sql)
    rows = cursor.fetchall()

    good_list = []
    for row in rows:
        good_list.append([row[0], row[1], row[2], row[3]])

    cursor.close()

    bought_message['good_list'] = good_list
    bought_message['response_code'] = 0

    return bought_message


def good_return(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               goodsid: string
       :param conn:
           pymysql connection
       :return:
           return_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    return_message = dict()
    if not check(['goodsid'], data, 'buyer return'):
        return_message['response_code'] = 1
        return return_message

    cursor = conn.cursor()
    sql = F"update goods set sold = 0 "\
          F"where goodsid = {data['goodsid']};"
    cursor.execute(sql)
    conn.commit()

    sql = F"delete from orders "\
          F"where goodsid = {data['goodsid']}"
    cursor.execute(sql)
    conn.commit()

    cursor.close()

    return_message['response_code'] = 0

    return return_message


def good_comment(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               comment: string
               goodsid: int
       :param conn:
           pymysql connection
       :return:
           comment_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    comment_message = dict()
    if not check(['comment'], data, 'buyer comment'):
        comment_message['response_code'] = 1

    cursor = conn.cursor()
    sql = F"update goods set comment = '{data['comment']}' "\
          F"where goodsid = {data['goodsid']};"

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    comment_message['response_code'] = 0
    return comment_message
