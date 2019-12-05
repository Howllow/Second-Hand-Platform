from db.config import *
from db.dbgmm import *

if __name__ == '__main__':
    connection = pymysql.connect(**config)