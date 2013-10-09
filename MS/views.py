#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import urllib2 
import json
import models
import time
import string
import DB.db
#from DB.db import *
import operation.views
import threading

def ms_insert(platform, v_server_id, v_server_name, v_server_ip, v_server_port, v_controll_ip, v_controll_port, v_room_id, v_room_name, v_server_version, \
              v_protocol_version, v_is_valid, v_is_dispatch, v_is_pause, \
              v_task_number, v_server_status1, v_server_status2, v_server_status3, v_server_status4, v_total_disk_space, v_free_disk_space, v_check_time):
    if(platform == 'mobile'):
        hash_local = models.mobile_ms(server_id = v_server_id,               \
                                             server_name = v_server_name,           \
                                             server_ip = v_server_ip,               \
                                             server_port = v_server_port,           \
                                             controll_ip = v_controll_ip,           \
                                             controll_port = v_controll_port,       \
                                             room_id = v_room_id,                   \
                                             room_name = v_room_name,               \
                                             server_version = v_server_version,     \
                                             protocol_version = v_protocol_version, \
                                             is_valid = v_is_valid,                 \
                                             is_dispatch = v_is_dispatch,           \
                                             is_pause = v_is_pause,                 \
                                             task_number = v_task_number,           \
                                             server_status1 = v_server_status1,     \
                                             server_status2 = v_server_status2,     \
                                             server_status3 = v_server_status3,     \
                                             server_status4 = v_server_status4,     \
                                             total_disk_space = v_total_disk_space, \
                                             free_disk_space = v_free_disk_space,   \
                                             check_time = v_check_time) 
        hash_local.save()
    elif(platform == 'pc'):
        hash_local = models.pc_ms(server_id = v_server_id,               \
                                             server_name = v_server_name,           \
                                             server_ip = v_server_ip,               \
                                             server_port = v_server_port,           \
                                             controll_ip = v_controll_ip,           \
                                             controll_port = v_controll_port,       \
                                             room_id = v_room_id,                   \
                                             room_name = v_room_name,               \
                                             server_version = v_server_version,     \
                                             protocol_version = v_protocol_version, \
                                             is_valid = v_is_valid,                 \
                                             is_dispatch = v_is_dispatch,           \
                                             is_pause = v_is_pause,                 \
                                             task_number = v_task_number,           \
                                             server_status1 = v_server_status1,     \
                                             server_status2 = v_server_status2,     \
                                             server_status3 = v_server_status3,     \
                                             server_status4 = v_server_status4,     \
                                             total_disk_space = v_total_disk_space, \
                                             free_disk_space = v_free_disk_space,   \
                                             check_time = v_check_time) 
        hash_local.save()
        

def get_ms_local(platform):
    ms_list = []
    if(platform == 'mobile'):
        ms_list = models.mobile_ms.objects.all()
    elif(platform == 'pc'):
        ms_list = models.pc_ms.objects.all()    
    return ms_list
        
        
def get_ms_macross(platform):
    ms_list = []
    sql = ""
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    
    db = DB.db.DB_MYSQL()
    #db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
    if(platform == 'mobile'):
        sql = "select s.server_id, s.server_name, s.server_ip, s.server_port, s.controll_ip, s.controll_port, s.ml_room_id, l.room_name, \
                s.server_version, s.protocol_version, s.is_valid, s.is_dispatch, s.is_pause \
                from fs_server s, fs_mobile_location l where s.ml_room_id=l.room_id and s.is_valid=1 order by s.server_id"
    elif(platform == 'pc'):
        sql = "select s.server_id, s.server_name, s.server_ip, s.server_port, s.controll_ip, s.controll_port, s.room_id, l.room_name, \
                s.server_version, s.protocol_version, s.is_valid, s.is_dispatch, s.is_pause \
                from fs_server s, fs_server_location l where s.room_id=l.room_id and s.is_valid=1 order by s.server_id"    
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
            elif(col_num == 11):
                ms['is_dispatch'] = r
            elif(col_num == 12):
                ms['is_pause'] = r
            col_num += 1
        ms_list.append(ms)    
    
    db.close()  
     
    return ms_list

        
def get_ms_list(request, platform):
    print 'get_ms_list'
    print request.REQUEST
    
    #{u'server_name': u'TY', u'room_name': u'', u'start': u'0', u'limit': u'20', u'server_ip': u'', u'control_ip': u''}
    start = request.REQUEST['start']
    limit = request.REQUEST['limit']
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    
    kwargs = {}
    
    v_server_name = ''
    if 'server_name' in request.REQUEST:
        v_server_name = request.REQUEST['server_name']
    if(v_server_name != ''):
        kwargs['server_name__contains'] = v_server_name
            
    v_server_ip = ''
    if 'server_ip' in request.REQUEST:
        v_server_ip = request.REQUEST['server_ip']
    if(v_server_ip != ''):
        kwargs['server_ip'] = v_server_ip
    
    v_control_ip = ''
    if 'control_ip' in request.REQUEST:
        v_control_ip = request.REQUEST['control_ip']
    if(v_control_ip != ''):
        kwargs['controll_ip'] = v_control_ip
        
    v_room_name = ''
    if 'room_name' in request.REQUEST:
        v_room_name = request.REQUEST['room_name']
    if(v_room_name != ''):
        kwargs['room_name__contains'] = v_room_name
    
    print kwargs
    
    sort = ''
    if 'sort' in request.REQUEST:
        sort  = request.REQUEST['sort']
        
    dire = ''
    if 'dir' in request.REQUEST:
        dire   = request.REQUEST['dir']
            
    order_condition = ''
    if(len(dire) > 0):
        if(dire == 'ASC'):
            order_condition += ''
        elif(dire == 'DESC'):
            order_condition += '-'
                
    if(len(sort) > 0):
        order_condition += sort    
    
    print order_condition
    
    servers = get_ms_local(platform)  
    servers1 = servers.filter(**kwargs) 
    servers2 = None
    if(len(order_condition) > 0):
        servers2 = servers1.order_by(order_condition)[start_index:start_index+limit_num]
    else:
        servers2 = servers1[start_index:start_index+limit_num]
    
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = servers1.count()
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
        try:
            #req = urllib2.Request('http://%s:11000/ms/check?detail=2'%(ip))
            req = urllib2.Request('http://%s:11000/ms/check?detail=2'%('124.254.47.122'))
            response = urllib2.urlopen(req)
            the_page = response.read()
            output += the_page
        except:
            output += 'error'
    return HttpResponse(output)


def get_ms_status(ms_local):    
    try:
        # get task number
        url = 'http://%s:%d/macross?cmd=queryglobalinfo' % (ms_local.controll_ip, ms_local.controll_port)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        output = response.read()
        #return=ok
        #tasknumber=145796
        #peernumber=913
        #rate=51381
        #bufrate=0
        #totalpeer=913
        #activetasknumber=344
        result = -1
        lines = output.split('\n')
        for line in lines:
            fields = line.split('=')
            if(len(fields) >= 2):
                key   = fields[0].strip()
                value = fields[1].strip()
                if(key == 'return'):
                    if(value == 'ok'):
                        result = 0
                    else:
                        result = -1
                elif (key == 'tasknumber'):
                    ms_local.task_number = string.atoi(value)
    except:
        print '%s get task number error' % (ms_local.controll_ip)
    
    try:
        # get disk space
        url = 'http://%s:%d/macross?cmd=querydisk' % (ms_local.controll_ip, ms_local.controll_port)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        output = response.read()
        #return=ok
        #result=12|22005|2290
        lines = output.split('\n')
        if(len(lines)>=2):
            line_1 = lines[0].strip()
            line_2 = lines[1].strip()
            if(line_1 == 'return=ok'):
                fields = line_2.split('=')
                field2 = fields[1]
                values = field2.split('|')
                ms_local.total_disk_space = string.atoi(values[1])
                ms_local.free_disk_space = string.atoi(values[2])
    except:
        print '%s get disk space error' % (ms_local.controll_ip)
    
    try:
        # get status    
        #req = urllib2.Request('http://%s:11000/ms/check?detail=0'%(ip))
        req = urllib2.Request('http://%s:11000/ms/check?detail=0'%('124.254.47.122'))
        response = urllib2.urlopen(req)
        output = response.read()
        num_error = 0
        lines = output.split('\n')
        for line in lines:
            #print 'line: %s' % (line)
            fields = line.split('\t')        
            #print 'num: %d' % (len(fields))
            if(len(fields) >=2):
                field2 = fields[1].strip()
                values = field2.split()
                if(len(values)>=2) and (values[1] != 'ok'):
                    num_error += 1
        ms_local.server_status1 = num_error
    except:
        print '%s get status error' % (ms_local.controll_ip)
        
    print '%s: %ld, %ld, %d' % (ms_local.controll_ip, ms_local.total_disk_space, ms_local.free_disk_space, ms_local.server_status1)    
    ms_local.save()
    
    
 
def ms_list_find(ms_list, server_id):
    for ms in ms_list:
        if(ms.server_id == server_id):
            return ms
    return None


def do_sync_ms_db(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    ms_list_macross = get_ms_macross(platform)    
    ms_list_local = get_ms_local(platform)

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
            ms_insert(platform, ms_macross['server_id'], ms_macross['server_name'], ms_macross['server_ip'], ms_macross['server_port'], \
                      ms_macross['controll_ip'], ms_macross['controll_port'], ms_macross['room_id'], ms_macross['room_name'], \
                      ms_macross['server_version'], ms_macross['protocol_version'], ms_macross['is_valid'], ms_macross['is_dispatch'], ms_macross['is_pause'], \
                      0, 0, 0, 0, 0, 0, 0, begin_time)                
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
            ms_local.is_dispatch        = ms_macross['is_dispatch']
            ms_local.is_dispatch        = ms_macross['is_dispatch']
            ms_local.is_pause           = ms_macross['is_pause']
            ms_local.save()
            num_update += 1
                
    for ms_local in ms_list_local:
        if(ms_local.is_valid == 0):
            ms_local.delete()
            num_delete += 1  
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.end_time = end_time
    record.status = 2        
    output = 'now: %s, ' % (end_time)
    output += 'macross: %d, ' % (num_macross)
    output += 'local: %d, ' % (num_local)
    output += 'insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    output += 'num_delete: %d' % (num_delete)
    record.memo = output
    record.save()
        

def do_sync_ms_status(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
        
    ms_list_local = get_ms_local(platform)
    
    num_local = ms_list_local.count()
    
    for ms_local in ms_list_local:
        get_ms_status(ms_local)    

    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.end_time = end_time
    record.status = 2        
    output = 'now: %s, ' % (end_time)
    output += 'ms num: %d, ' % (num_local)    
    record.memo = output
    record.save()
        
            
class Thread_SYNC_MS_DB(threading.Thread):
    #platform = ''
    #record = None
    
    def __init__(self, the_platform, the_record):
        super(Thread_SYNC_MS_DB, self).__init__()
        self.platform = the_platform
        self.record = the_record
        
        
    def run(self):
        result = do_sync_ms_db(self.platform, self.record)
        return result        
        
            
class Thread_SYNC_MS_STATUS(threading.Thread):
    #platform = ''
    #record = None
    
    def __init__(self, the_platform, the_record):
        super(Thread_SYNC_MS_STATUS, self).__init__()        
        self.platform = the_platform
        self.record = the_record
        
        
    def run(self):
        result = do_sync_ms_status(self.platform, self.record)
        return result    
        
                    
def sync_ms_db(request, platform):  
    print 'sync_ms_db'
    print request.REQUEST
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'sync_ms_db'
    operation1['name'] = today
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
        
    return_datas = {}
    output = ''
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) > 0):          
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
    
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    return_datas['success'] = False
    return_datas['data'] = output
        
    if(start_now == True):
        # start thread.
        t = Thread_SYNC_MS_DB(platform, record)            
        t.start()
    
    return HttpResponse(json.dumps(return_datas))


def sync_ms_status(request, platform):  
    print 'sync_ms_status'
    print request.REQUEST
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'sync_ms_status'
    operation1['name'] = today
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
    
    return_datas = {}
    output = ''
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) > 0):          
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
    
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas['success'] = False
        return_datas['data'] = output
        return HttpResponse(json.dumps(return_datas)) 
        
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    return_datas['success'] = False
    return_datas['data'] = output
        
    if(start_now == True):
        # start thread.
        t = Thread_SYNC_MS_STATUS(platform, record)            
        t.start()
    
    return HttpResponse(json.dumps(return_datas))

