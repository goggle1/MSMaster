#coding=utf-8
import MySQLdb

class DB_MYSQL :
    conn = None
    cur = None
    def connect(self, host, port, user, passwd, db, charset='utf8') :
        self.conn = MySQLdb.connect(host, user, passwd, db, port, charset='utf8')
        self.cur  = self.conn.cursor()
    def execute(self, sql):           
        self.cur.execute(sql)
    def close(self):
        self.cur.close()
        self.conn.close()
        
        
class DB_CONFIG:
    host        = '192.168.8.101'
    port        = 3317
    user        = 'public'
    password    = 'funshion'
    db          = 'macross'
    

class HITS_FILE:
    template_mobile = '/media2/data_analysis/topdata/mo/logdata/logdata_%s_hashid_sort.result'
    template_pc     = '/media2/data_analysis/topdata/pc/logdata/logdata_%s_hashid_sort.result'
    hot_period      = 30
        