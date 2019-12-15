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
          F"ORDER BY G.uptime DESC;"
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
          F"ORDER BY G.uptime DESC;"

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
          F"ORDER BY O.time DESC;"
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
               goodsid: string
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


def change_setting(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               username: string
               type: string
               content: string
       :param conn:
           pymysql connection
       :return:
           setting_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    setting_message = dict()
    if not check(['username', 'type', 'content'], data, 'change setting'):
        setting_message['response_code'] = 1
        return setting_message

    cursor = conn.cursor()
    sql = F"update users set {data['type']} = '{data['content']}' "\
          F"where username = '{data['username']}';"

    cursor.execute(sql)
    conn.commit()
    cursor.close()

    setting_message['response_code'] = 0

    return setting_message


def sell_good(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               username: string
               type: string
               description: string
               price: string
               goodname: string
       :param conn:
           pymysql connection
       :return:
           sell_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    sell_message = dict()
    if not check(['username', 'type', 'description', 'price', 'goodname'], data, 'sell good'):
        sell_message['response_code'] = 1
        return sell_message

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    sql = F"insert into goods(sold, type, description, price, seller, uptime, goodname)"\
          F"VALUE(0, '{data['type']}', '{data['description']}', {data['price']}, '{data['username']}'," \
          F"'{dt}', '{data['goodname']}');"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    sell_message['response_code'] = 0
    return sell_message


def selling_good(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               username: string
       :param conn:
           pymysql connection
       :return:
           selling_message:
               response_code:
                   0 for success
                   1 for wrong data
               good_list
    """

    username = data['username']
    selling_message = dict()

    if not check(['username'], data, "selling good"):
        selling_message['response_code'] = 1
        return selling_message

    cursor = conn.cursor()
    sql = F"select goodname, price, type, goodsid from goods "\
          F"where seller = '{username}' and sold = 0 "\
          F"ORDER BY type ASC, uptime DESC;"

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    good_list = []
    for row in rows:
        good_list.append([row[0], row[1], row[2], row[3]])

    selling_message['good_list'] = good_list
    selling_message['response_code'] = 0

    return selling_message


def cancel_good(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               goodsid: string
       :param conn:
           pymysql connection
       :return:
           cancel_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    cancel_message = dict()

    if not check(['goodsid'], data, 'cancel good'):
        cancel_message['response_code'] = 1
        return cancel_message

    cursor = conn.cursor()
    sql = F"delete from goods "\
          F"where goodsid = {data['goodsid']};"

    cursor.execute(sql)
    conn.commit()
    cursor.close()

    cancel_message['response_code'] = 0
    return cancel_message


def change_good(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               goodsid: string
               type: string
               content: string
       :param conn:
           pymysql connection
       :return:
           change_message:
               response_code:
                   0 for success
                   1 for wrong data
    """

    change_message = dict()
    if not check(['goodsid', 'type', 'content'], data, "change good"):
        change_message['response_code'] = 1

    cursor = conn.cursor()
    if data['type'] == "price":
        sql = F"update goods set price = {data['content']} "\
              F"where goodsid = {data['goodsid']};"
    else:
        sql = F"update goods set {data['type']} = '{data['content']}' "\
              F"where goodsid = {data['goodsid']};"

    cursor.execute(sql)
    conn.commit()
    cursor.close()

    change_message['response_code'] = 0
    return change_message


def sold_good(data: dict, conn :Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
               username: string

       :param conn:
           pymysql connection
       :return:
           sold_message:
               response_code:
                   0 for success
                   1 for wrong data
               good_list：goodname, buyer, ordertime, comment
    """

    sold_message = dict()
    if not check(['username'], data, "sold good"):
        sold_message['response_code'] = 1
        return sold_message


    print(data)
    sql = F"select G.goodname, U.nickname, O.time, G.comment from goods as G, orders as O, users as U "\
          F"where G.goodsid = O.goodsid and G.seller = '{data['username']}' and U.username = O.buyer "\
          F"ORDER BY O.time DESC, U.nickname ASC;"
    cursor = conn.cursor()
    cursor.execute(sql)

    rows = cursor.fetchall()
    cursor.close()

    good_list = []
    for row in rows:
        good_list.append([row[0], row[1], row[2], row[3]])

    sold_message['response_code'] = 0
    sold_message['good_list'] = good_list

    return sold_message


def get_request(conn: Connection):
    """
       :param conn:
           pymysql connection
       :return:
           req_message:
               response_code:
                   0 for success
                   1 for wrong data
               req_list：nickname, phone, gender, age, id
    """
    req_message = dict()
    cursor = conn.cursor()
    sql = F"select nickname, phone, gender, age, idrequests from requests;"

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    req_list = [row for row in rows]
    req_message['response_code'] = 0
    req_message['req_list'] = req_list

    return req_message


def req_manage(data: dict, conn: Connection):
    """
       :param data:
           python dictionary, containing keys as follows:
                   idrequests: string
                   agree: string

       :param conn:
           pymysql connection
       :return:
           manage_message:
               response_code:
                   0 for success
                   1 for wrong data
    """
    manage_message = dict()
    if not check(['idrequests', 'agree'], data, "req manage"):
        manage_message['response_code'] = 1
        return manage_message

    cursor = conn.cursor()

    if int(data['agree']) == 1:
        sql = F"select username, password, nickname, phone, gender, age from requests "\
              F"where idrequests = {data['idrequests']};"
        cursor.execute(sql)
        rows = cursor.fetchall()
        row = rows[0]
        sql = F"insert into users(username, password, authority, nickname, phone, gender, age) "\
              F"VALUE('{row[0]}', '{row[1]}', 1, '{row[2]}', '{row[3]}', '{row[4]}', {row[5]});"
        cursor.execute(sql)
        conn.commit()

    sql = F"delete from requests where idrequests = {data['idrequests']};"
    cursor.execute(sql)

    conn.commit()
    cursor.close()

    manage_message['response_code'] = 0
    return manage_message


def get_orders(conn: Connection):
    """
       :param conn:
           pymysql connection
       :return:
           od_message:
               response_code:
                   0 for success
                   1 for wrong data
               od_list：seller, buyer, goodname, price, time
    """
    od_message = dict()

    cursor = conn.cursor()
    sql = F"select G.seller, O.buyer, G.goodname, G.price, O.time "\
          F"from orders as O, goods as G "\
          F"where O.goodsid = G.goodsid " \
          F"ORDER BY O.time DESC;"

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    od_message['response_code'] = 0
    od_message['od_list'] = [row for row in rows]

    return od_message


def tuhao_buyer(conn: Connection):
    """
       :param conn:
           pymysql connection
       :return:
           th_message:
               response_code:
                   0 for success
               good_list：username, gender, age, total
    """

    th_message = dict()
    cursor = conn.cursor()

    sql = F"select b, n, g, a, p from "\
          F"(select O.buyer as b, U.nickname as n, U.gender as g, U.age as a, sum(G.price) as p "\
          F"from orders as O, users as U, goods as G "\
          F"where O.goodsid = G.goodsid and O.buyer = U.username "\
          F"GROUP BY b, g, a) as info "\
          F"ORDER BY p DESC, b DESC;"

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    good_list = []
    for row in rows:
        good_list.append([row[0], row[1], row[2], row[3],int(row[4])])

    th_message['good_list'] = good_list
    th_message['response_code'] = 0

    return th_message


def similar_buyer(data: dict, conn: Connection):
    """
       :param conn:
           pymysql connection
       :param data:
          python dictionary, containing keys as follows:
               username: string
       :return:
           sm_message:
               response_code:
                   0 for success
                   1 for wrong data
                   2 for not found
                   3 for haven't bought
               usr_list: username, nickname, gender, age, phonenum
    """

    sm_message = dict()
    if not check(['username'], data, "similar buyer"):
        sm_message['response_code'] = 1
        return sm_message

    cursor = conn.cursor()

    sql = F"select username from users where authority = 0;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    rows = [row[0] for row in rows]
    if data['username'] not in rows:
        cursor.close()
        logging.debug(F'user {data["username"]} not found')
        sm_message['response_code'] = 2
        return sm_message

    sql = F"select buyer from orders;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    rows = [row[0] for row in rows]
    if data['username'] not in rows:
        cursor.close()
        logging.debug(F'user {data["username"]} not buy')
        sm_message['response_code'] = 3
        return sm_message

    target = data['username']

    sql = F"select U.username, U.nickname, U.gender, U.age, U.phone, count(*) as c "\
          F"from users as U, orders as O "\
          F"where not exists( "\
          F"select G.seller "\
          F"from goods as G, orders as OO "\
          F"where G.goodsid = OO.goodsid and OO.buyer = '{target}' and "\
          F"G.seller not in( "\
          F"select G.seller "\
          F"from goods as G, orders as OO "\
          F"where G.goodsid = OO.goodsid and OO.buyer = U.username)) "\
          F"and not exists( "\
          F"select G.seller "\
          F"from goods as G, orders as OO "\
          F"where G.goodsid = OO.goodsid and OO.buyer = U.username and "\
          F"G.seller not in( "\
          F"select G.seller "\
          F"from goods as G, orders as OO "\
          F"where G.goodsid = OO.goodsid and OO.buyer = '{target}')) "\
          F"and U.username = O.buyer "\
          F"and U.username <> '{target}' "\
          F"GROUP BY O.buyer "\
          F"ORDER BY c DESC, username DESC;"

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    usr_list = []
    for row in rows:
        usr_list.append([row[0], row[1], row[2], row[3], row[4], row[5]])

    sm_message['response_code'] = 0
    sm_message['usr_list'] = usr_list
    return sm_message


def get_audience(conn: Connection):
    """
       :param conn:
           pymysql connection
       :return:
           ad_message:
               response_code:
                   0 for success
                   1 for wrong data
               usr_list: username, nickname, teen, mid, old
    """
    ad_message = dict()

    cursor = conn.cursor()

    sql = F"select username, nickname from users where authority = 1;"
    cursor.execute(sql)

    rows = cursor.fetchall()
    names = [(row[0], row[1]) for row in rows]

    usr_list = []
    for name in names:
        sql = F"select count(teen.t) from "\
              F"(select distinct U.username as t "\
              F"from users as U, orders as O, goods as G "\
              F"where O.goodsid = G.goodsid "\
              F"and G.seller = '{name[0]}' "\
              F"and O.buyer = U.username "\
              F"and U.age < 30) as teen; "
        cursor.execute(sql)
        rows = cursor.fetchall()
        teencnt = rows[0][0]

        sql = F"select count(mid.t) from " \
              F"(select distinct U.username as t " \
              F"from users as U, orders as O, goods as G " \
              F"where O.goodsid = G.goodsid " \
              F"and G.seller = '{name[0]}' " \
              F"and O.buyer = U.username " \
              F"and U.age >= 30 and U.age < 50) as mid; "
        cursor.execute(sql)
        rows = cursor.fetchall()
        midcnt = rows[0][0]

        sql = F"select count(senior.t) from " \
              F"(select distinct U.username as t " \
              F"from users as U, orders as O, goods as G " \
              F"where O.goodsid = G.goodsid " \
              F"and G.seller = '{name[0]}' " \
              F"and O.buyer = U.username " \
              F"and U.age >= 50) as senior; "
        cursor.execute(sql)
        rows = cursor.fetchall()
        oldcnt = rows[0][0]

        usr_list.append([name[0], name[1], teencnt, midcnt, oldcnt])

    cursor.close()
    ad_message['response_code'] = 0
    ad_message['usr_list'] = usr_list

    return ad_message


def get_hot(conn: Connection):
    """
       :param conn:
           pymysql connection
       :return:
           ht_message:
               response_code:
                   0 for success
                   1 for wrong data
               usr_list: username, nickname, gender, age, total
    """
    ht_message = dict()

    cursor = conn.cursor()
    sql = F"select a, nickname, gender, age , b from "\
          F"(select U.username as a, count(G.comment) as b "\
          F"from goods as G, users as U "\
          F"where U.authority = 1 "\
          F"and G.seller = U.username "\
          F"GROUP BY G.seller) as comm, Users "\
          F"where b >= (select avg(b) from "\
          F"(select U.username as a, count(G.comment) as b "\
          F"from goods as G, users as U "\
          F"where U.authority = 1 " \
          F"and G.seller = U.username " \
          F"GROUP BY G.seller) as comm) and a = username "\
          F"ORDER BY b DESC;"

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    usr_list = []
    for row in rows:
        usr_list.append([row[0], row[1], row[2], row[3], row[4]])

    ht_message['usr_list'] = usr_list
    ht_message['response_code'] = 0

    return ht_message

