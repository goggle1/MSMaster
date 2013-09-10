#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import urllib2 
import json
import models
import sys
import re
import MySQLdb
import time
import string


def get_ms_local(platform):
    ms_list = []
    if(platform == 'mobile'):
        ms_list = models.mobile_ms_server.objects.all()
    elif(platform == 'pc'):
        ms_list = models.pc_ms_server.objects.all()    
    return ms_list

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
        
        
def get_ms_macross(platform):
    ms_list = []
    
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    db = DB_MYSQL()
    db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
    sql = "select s.server_id, s.server_name, s.server_ip, s.server_port, s.controll_ip, s.controll_port, s.ml_room_id, l.room_name, s.server_version, s.protocol_version, s.is_valid from fs_server s, fs_server_location l where s.ml_room_id=l.room_id and s.is_valid=1 order by s.server_id"
    db.execute(sql)
    
    for row in db.cur.fetchall():
        ms = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                ms['server_id'] = r
            elif(col_num == 1):
                ms['server_name'] = r
            elif(col_num == 2):
                ms['server_ip'] = r
            elif(col_num == 3):
                ms['server_port'] = r
            elif(col_num == 4):
                ms['controll_ip'] = r
            elif(col_num == 5):
                ms['controll_port'] = r
            elif(col_num == 6):
                ms['room_id'] = r
            elif(col_num == 7):
                ms['room_name'] = r
            elif(col_num == 8):
                ms['server_version'] = r
            elif(col_num == 9):
                ms['protocol_version'] = r
            elif(col_num == 10):
                ms['is_valid'] = r
            col_num += 1
        ms_list.append(ms)    
    
    db.close()  
     
    return ms_list

        
def get_ms_list(request, platform):
    servers = get_ms_local(platform)    
    
    print request.REQUEST
    #print request.REQUEST['start']
    #print request.REQUEST['limit']
    #{u'sort': u'server_id', u'start': u'0', u'limit': u'20', u'dir': u'ASC'}
    #{u'sort': u'server_name', u'start': u'0', u'limit': u'20', u'dir': u'DESC'}
    start = request.REQUEST['start']
    limit = request.REQUEST['limit']
    sort = ''
    if 'sort' in request.REQUEST:
        sort  = request.REQUEST['sort']
    dir = ''
    if 'dir' in request.REQUEST:
        dir   = request.REQUEST['dir']
            
    order_by = ''
    if(len(dir) > 0):
        if(dir == 'ASC'):
            order_by += ''
        elif(dir == 'DESC'):
            order_by += '-'
                
    if(len(sort) > 0):
        order_by += sort
    
    servers2 = servers
    if(len(order_by) > 0):
        servers2 = servers.order_by(order_by)
    
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    
    index = 0
    num = 0
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = len(servers2)
    for server in servers2:
        if(index >= start_index) and (num < limit_num):
            return_datas['data'].append(server.todict())
            num += 1
        index += 1
        
    return HttpResponse(json.dumps(return_datas))


def show_ms_list(request, platform):  
    output = ''
    ips = request.REQUEST['ips']    
    ip_list = ips.split(',')
    for ip in ip_list:
        title = '<h1>ip: %s</h1>' % (ip)
        output += title  
        req = urllib2.Request('http://124.254.47.122:11000/ms/check?detail=2')
        response = urllib2.urlopen(req)
        the_page = response.read()
        output += the_page
    return HttpResponse(output)
 
def ms_list_find(ms_list, server_id):
    for ms in ms_list:
        if(ms.server_id == server_id):
            return ms
    return None
    
def sync_ms_db(request, platform):  
    ms_list_macross = get_ms_macross(platform)    
    ms_list_local = get_ms_local(platform)
    
    num_macross = len(ms_list_macross)
    num_local = len(ms_list_local)
    
    num_insert = 0
    num_update = 0
    num_delete = 0
    
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    
    for ms_local in ms_list_local:
        ms_local.is_valid = 0
    
    for ms_macross in ms_list_macross:
        ms_local = ms_list_find(ms_list_local, ms_macross['server_id'])
        if(ms_local == None):
            ms_local = models.mobile_ms_server(server_id          = ms_macross['server_id'],        \
                                               server_name        = ms_macross['server_name'],      \
                                               server_ip          = ms_macross['server_ip'],        \
                                               server_port        = ms_macross['server_port'],      \
                                               controll_ip        = ms_macross['controll_ip'],      \
                                               controll_port      = ms_macross['controll_port'],    \
                                               room_id            = ms_macross['room_id'],          \
                                               room_name          = ms_macross['room_name'],        \
                                               server_version     = ms_macross['server_version'],   \
                                               protocol_version   = ms_macross['protocol_version'], \
                                               is_valid           = ms_macross['is_valid'],         \
                                               task_number        = 0,                              \
                                               server_status1     = 0,                              \
                                               server_status2     = 0,                              \
                                               server_status3     = 0,                              \
                                               server_status4     = 0,                              \
                                               check_time         = now_time           \
                                               )
            ms_local.save()
            num_insert += 1
        else:
            ms_local.server_id          = ms_macross['server_id']
            ms_local.server_name        = ms_macross['server_name']
            ms_local.server_ip          = ms_macross['server_ip']
            ms_local.server_port        = ms_macross['server_port']
            ms_local.controll_ip        = ms_macross['controll_ip']
            ms_local.controll_port      = ms_macross['controll_port']
            ms_local.room_id            = ms_macross['room_id']
            ms_local.room_name          = ms_macross['room_name']
            ms_local.server_version     = ms_macross['server_version']
            ms_local.protocol_version   = ms_macross['protocol_version']
            ms_local.is_valid           = ms_macross['is_valid']
            ms_local.check_time         = now_time
            ms_local.save()
            num_update += 1
                
    for ms_local in ms_list_local:
        if(ms_local.is_valid == 0):
            ms_local.delete()
            num_delete += 1  
    
    output = 'now: %s, ' % (now_time)
    output += 'macross: %d, ' % (num_macross)
    output += 'local: %d, ' % (num_local)
    output += 'insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    output += 'num_delete: %d' % (num_delete)
        
    return HttpResponse(output)
    