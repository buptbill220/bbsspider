#!/usr/bin/python
# coding=utf-8

import MySQLdb as mdb
import time
import os

class MySQL:
    def __init__(self, host, user, passwd, db, port, charset, timeout, logger):
        print 'connect..., host=%s, user=%s, passwd=%s, db=%s, port=%s, charset=%s, timeout=%s' \
            %(host, user, passwd, db, port, charset, timeout);
        self.conn = mdb.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset=charset, connect_timeout=timeout)
        self.cursor = self.conn.cursor()
        self.log = logger

    def __del__(self):
        print 'close connect...'
        self.cursor.close()
        self.conn.close()

    def query(self, sql):
        print 'query sql [%s]' %sql;
        self.cursor.execute(sql);
        rows = self.cursor.fetchall()
        return rows

    def update(self, sql):
        print 'update sql [%s]...' % sql;
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            #print 'update sql[%s] failed' % sql; 
            print 'update failed';
    
if __name__ == '__main__':
    db = MySQL('127.0.0.1', 'root', '', 'bupt', 3306, 'utf8', 5, '');
    rows = db.query('select *from st_menu');
    print rows
