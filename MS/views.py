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
from operation.models import mobile_operation
from operation.models import pc_operation
import threading


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
    sql = ""
    
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    db = DB_MYSQL()
    db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
    if(platform == 'mobile'):
        sql = "select s.server_id, s.server_name, s.server_ip, s.server_port, s.controll_ip, s.controll_port, s.ml_room_id, l.room_name, s.server_version, s.protocol_version, s.is_valid from fs_server s, fs_server_location l where s.ml_room_id=l.room_id and s.is_valid=1 order by s.server_id"
    elif(platform == 'pc'):
        sql = "select s.server_id, s.server_name, s.server_ip, s.server_port, s.controll_ip, s.controll_port, s.room_id, l.room_name, s.server_version, s.protocol_version, s.is_valid from fs_server s, fs_server_location l where s.room_id=l.room_id and s.is_valid=1 order by s.server_id"    
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
    print 'get_ms_list'
    print request.REQUEST
    
    start = request.REQUEST['start']
    limit = request.REQUEST['limit']
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    
    sort = ''
    if 'sort' in request.REQUEST:
        sort  = request.REQUEST['sort']
        
    dire = ''
    if 'dir' in request.REQUEST:
        dire   = request.REQUEST['dir']
            
    order_by = ''
    if(len(dire) > 0):
        if(dire == 'ASC'):
            order_by += ''
        elif(dire == 'DESC'):
            order_by += '-'
                
    if(len(sort) > 0):
        order_by += sort
    
    servers = get_ms_local(platform)    
    servers2 = []
    if(len(order_by) > 0):
        servers2 = servers.order_by(order_by)[start_index:start_index+limit_num]
    else:
        servers2 = servers[start_index:start_index+limit_num]
    
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = servers.count()
    for server in servers2:
        return_datas['data'].append(server.todict())
        
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


def get_operation_record(platform, the_type, the_name):
    records = []
    if(platform == 'mobile'):
        records = mobile_operation.objects.filter(type=the_type, name=the_name)
    elif(platform == 'pc'):
        records = pc_operation.objects.filter(type=the_type, name=the_name)
    return records


def create_operation_record(platform, the_type, the_name, the_dispatch_time):
    record = None    
    if(platform == 'mobile'):
        record = mobile_operation(type=the_type, name=the_name, dispatch_time=the_dispatch_time, status=0)
        record.save()
    elif(platform == 'pc'):
        record = pc_operation(type=the_type, name=the_name, dispatch_time=the_dispatch_time, status=0)
        record.save()
    return record


class MyThread(threading.Thread):
    platform = ''
    record = None
    
    def __init__(self, the_platform, the_record):
        super(MyThread, self).__init__()        
        self.platform = the_platform
        self.record = the_record
        
        
    def run(self):
        now_time = time.localtime(time.time())        
        begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        self.record.begin_time = begin_time
        self.record.status = 1
        self.record.save()
    
        ms_list_macross = get_ms_macross(self.platform)    
        ms_list_local = get_ms_local(self.platform)
    
        num_macross = ms_list_macross.__len__()
        num_local = ms_list_local.count()
    
        num_insert = 0
        num_update = 0
        num_delete = 0
    
        for ms_local in ms_list_local:
            ms_local.is_valid = 0
    
        for ms_macross in ms_list_macross:
            ms_local = ms_list_find(ms_list_local, ms_macross['server_id'])
            if(ms_local == None):
                if(self.platform == 'mobile'):
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
                                               check_time         = begin_time           \
                                               ) 
                elif(self.platform == 'pc'):
                    ms_local = models.pc_ms_server(server_id          = ms_macross['server_id'],        \
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
                                               check_time         = begin_time           \
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
                ms_local.check_time         = begin_time
                ms_local.save()
                num_update += 1
                
        for ms_local in ms_list_local:
            if(ms_local.is_valid == 0):
                ms_local.delete()
                num_delete += 1  
    
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        self.record.end_time = end_time
        self.record.status = 2        
        output = 'now: %s, ' % (end_time)
        output += 'macross: %d, ' % (num_macross)
        output += 'local: %d, ' % (num_local)
        output += 'insert: %d, ' % (num_insert)
        output += 'num_update: %d, ' % (num_update)
        output += 'num_delete: %d' % (num_delete)
        self.record.memo = output
        self.record.save()
        
            
            
def sync_ms_db(request, platform):  
    print 'sync_ms_db'
    print request.REQUEST
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation = {}
    operation['type'] = 'sync_ms_db'
    operation['name'] = today
        
    output = ''
    records = get_operation_record(platform, operation['type'], operation['name'])
    if(len(records) == 0):
        record = create_operation_record(platform, operation['type'], operation['name'], dispatch_time)
        if(record != None):
            output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
            # start thread.
            t = MyThread(platform, record)            
            t.start()
    else:
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    
    return HttpResponse(output)       

