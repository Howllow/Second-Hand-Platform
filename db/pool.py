from dbutils.pooled_db import PooledDB
import pymysql

Pool_Config = {
    "maxconnections": 0,
    "mincached": 1,
    "maxcached": 100,
    "maxusage": None,
    "blocking": False,
    "ping":0,
    'host':'8.tcp.ngrok.io',
    'port':17536,
    'user':'jj',
    'password':'gimmemoney',
    'database':'gmm',
    'charset':'utf8mb4'
}

class DB_Pool(object):
    def __init__(self, config=Pool_Config, db_type=pymysql):
        self.__pool = PooledDB(creator=db_type, **config)

    def connection(self):
        return self.__pool.connection()