from db.config import *
from db.dbgmm import *

if __name__ == '__main__':
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    """
    sql = F"insert into users (username, password, authority, nickname, phone, gender)" \
          F" VALUE ('zjr', 'zjr954', 2, 'jerry', '11111111111', 0);"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    """
