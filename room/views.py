#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import time
import string
#import MS.models
import DB.db
#from DB.db import *
import MS.models
#from MS.models import mobile_ms_server
#from MS.models import pc_ms_server
import operation.views
#from operation.views import get_operation_record
#from operation.views import get_operation_record_undone
#from operation.views import create_operation_record
from task.views import get_tasks_local
import threading
from ms import *
import MS.views
#from MS.views import get_ms_status
                                           
def room_insert(platform, v_room_id, v_room_name, v_is_valid, v_check_time):
    if(platform == 'mobile'): 
        hash_local = models.mobile_room(room_id = v_room_id,                    \
                                        room_name = v_room_name,                \
                                        is_valid = v_is_valid,                  \
                                        check_time = v_check_time)
        hash_local.save()
    elif(platform == 'pc'):
        hash_local = models.pc_room(room_id = v_room_id,                    \
                                        room_name = v_room_name,                \
                                        is_valid = v_is_valid,                  \
                                        check_time = v_check_time)
        hash_local.save()
        

def get_room_local(platform):
    rooms = []
    if(platform == 'mobile'):
        rooms = models.mobile_room.objects.all()
    elif(platform == 'pc'):
        rooms = models.pc_room.objects.all()

    return rooms
        
        
def get_room_macross(platform):
    room_list = []
    sql = ""
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
    if(platform == "mobile"):
        sql = "select l.room_id, l.room_name, l.is_valid from fs_server s, fs_mobile_location l where s.ml_room_id=l.room_id and s.is_valid=1 and l.is_valid=1 group by l.room_id order by l.room_id"
    elif(platform == "pc"):
        sql = "select l.room_id, l.room_name, l.is_valid from fs_server s, fs_server_location l where s.room_id=l.room_id and s.is_valid=1 and l.is_valid=1 group by l.room_id order by l.room_id"
    db.execute(sql)
    
    for row in db.cur.fetchall():
        room = {}  
        col_num = 0  
        for r in row:
            if(col_num == 0):
                room['room_id'] = r
            elif(col_num == 1):
                room['room_name'] = r
            elif(col_num == 2):
                room['is_valid'] = r            
            col_num += 1
        room_list.append(room)    
    
    db.close()  
     
    return room_list


def get_room_list(request, platform):
    print 'get_room_list'
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
            
    order_condition = ''
    if(len(dire) > 0):
        if(dire == 'ASC'):
            order_condition += ''
        elif(dire == 'DESC'):
            order_condition += '-'
                
    if(len(sort) > 0):
        order_condition += sort
    
    rooms = get_room_local(platform) 
    rooms2 = []
    if(len(order_condition) > 0):
        rooms2 = rooms.order_by(order_condition)[start_index:start_index+limit_num]
    else:
        rooms2 = rooms[start_index:start_index+limit_num]
    
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = rooms.count()
    for room in rooms2:
        return_datas['data'].append(room.todict())
        
    return HttpResponse(json.dumps(return_datas))


def get_ms_list_in_room(platform, the_room_id):
    ms_list = []
    if(platform == 'mobile'):
        ms_list = MS.models.mobile_ms.objects.filter(room_id=the_room_id)
    elif(platform == 'pc'):
        ms_list = MS.models.pc_ms.objects.filter(room_id=the_room_id)
    return ms_list
        
    
def show_room_list(request, platform):  
    output = ''
    ids = request.REQUEST['ids']    
    id_list = ids.split(',')
    for room_id in id_list:                         
        ms_list = get_ms_list_in_room(platform, room_id)
        title = '<h1>id: %s, ms_num: %d</h1>' % (id, len(ms_list))
        output += title        
        for ms in ms_list:
            output += '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s<br>' \
            % (str(ms.server_id), str(ms.server_name), str(ms.server_ip), str(ms.server_port), \
               str(ms.controll_ip), str(ms.controll_port), str(ms.task_number), str(ms.server_status1), \
               str(ms.server_status2), str(ms.total_disk_space), str(ms.free_disk_space), str(ms.check_time))
    return HttpResponse(output)


def room_list_find(room_list, room_id):
    for room in room_list:
        if(room.room_id == room_id):
            return room
    return None


def do_add_hot_tasks(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()

    room_id = record.name
    num_dispatching = record.memo
    total_num = string.atoi(num_dispatching)
    
    ms_list = get_ms_list_in_room(platform, room_id)
    if(len(ms_list) <= 0):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_id: %s, ' % (room_id)
        output += 'num_dispatching: %s, ' % (num_dispatching)
        output += 'ms num: %d, ' % (len(ms_list))
        record.end_time = end_time
        record.status = 2        
        record.memo = output
        record.save()
        return False
        
    print 'ms_list num: %d' % (len(ms_list))
    
    file_name = 'hot_tasks_%s_%s.log' % (room_id, num_dispatching)
    log_file = open(file_name, 'w')        
    
    ms_all = MS_ALL(platform, ms_list)
    ms_all.get_tasks()
            
    num = 0
    result = False
    tasks = get_tasks_local(platform) 
    print 'tasks count: %d' % (tasks.count())
    #hot_tasks = tasks.order_by('-hot')
    hot_tasks = tasks.filter(hot__gt=0).order_by('-hot')
    print 'hot_tasks count: %d' % (hot_tasks.count())
    for task in hot_tasks:
        print 'hot task: %d %s' % (task.hot, task.hash)
        one_ms = ms_all.find_task(task.hash)
        if(one_ms == None):
            print '%s dispatched' % (task.hash)            
            result = ms_all.dispatch_hot_task(task.hash)
            if(result == None):
                print '%s can not dispatched\n' % (task.hash) 
                log_file.write('%s can not dispatched\n' % (task.hash))
                break
            else:
                print '%s dispatched to %s\n' % (task.hash, str(result.db_record.controll_ip))
                log_file.write('%s dispatched to %s\n' % (task.hash, str(result.db_record.controll_ip)))
            num += 1
            if(num >= total_num):
                break
        else:
            print '%s exist at %s' % (task.hash, one_ms.db_record.controll_ip)
            log_file.write('%s exist at %s\n' % (task.hash, one_ms.db_record.controll_ip))

    log_file.close()
    
    ms_all.do_dispatch()
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'room_id: %s, ' % (room_id)
    output += 'num_dispatching: %s, ' % (num_dispatching)
    output += 'ms num: %d, ' % (len(ms_list))
    output += 'task num: %d, ' % (num)
    print output
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
    return True


def do_sync_room_db(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    room_list_macross = get_room_macross(platform)    
    room_list_local = get_room_local(platform)

    num_macross = room_list_macross.__len__()
    num_local = room_list_local.count()
    
    num_insert = 0
    num_update = 0
    num_delete = 0    

    for room_local in room_list_local:
        room_local.is_valid = 0
    
    for room_macross in room_list_macross:
        room_local = room_list_find(room_list_local, room_macross['room_id'])
        print room_macross['room_id'], room_macross['room_name'], room_macross['is_valid']
        if(room_local == None):
            room_insert(platform, room_macross['room_id'], room_macross['room_name'], room_macross['is_valid'], begin_time)                
            num_insert += 1
        else:
            room_local.room_id           = room_macross['room_id']
            room_local.room_name         = room_macross['room_name']
            room_local.is_valid          = room_macross['is_valid']
            room_local.check_time        = begin_time
            room_local.save()
            num_update += 1
            
    for room_local in room_list_local:
        if(room_local.is_valid == 0):
            room_local.delete()
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
     
    
def do_sync_room_status(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()

    ms_num = 0
    
    rooms = get_room_local(platform)
    for room in rooms:
        print 'room_id=%d, %s' % (room.room_id, str(room.room_name))
        ms_list = get_ms_list_in_room(platform, room.room_id)
        room.ms_number = len(ms_list)
        room.task_number = 0
        room.total_disk_space = 0
        room.free_disk_space = 0
        room.suggest_task_number = 0
        room.num_dispatching = 0
        room.num_deleting = 0
        for ms in ms_list:
            ms_num += 1
            #print 'ms_ip=%s' % (str(ms.controll_ip))                
            room.task_number += ms.task_number
            room.total_disk_space += ms.total_disk_space
            room.free_disk_space  += ms.free_disk_space
        room.save()
                
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'room num: %s, ' % (len(rooms))
    output += 'ms num: %d, ' % (ms_num)
    print output
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
        
    
class Thread_SYNC_ROOM_DB(threading.Thread):
    #platform = ''
    #record = None
    
    def __init__(self, the_platform, the_record):
        super(Thread_SYNC_ROOM_DB, self).__init__()        
        self.platform = the_platform
        self.record = the_record
        
        
    def run(self):
        result = do_sync_room_db(self.platform, self.record)
        return result
    
        now_time = time.localtime(time.time())        
        begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        self.record.begin_time = begin_time
        self.record.status = 1
        self.record.save()
    
        room_list_macross = get_room_macross(self.platform)    
        room_list_local = get_room_local(self.platform)
    
        num_macross = room_list_macross.__len__()
        num_local = room_list_local.count()
    
        num_insert = 0
        num_update = 0
        num_delete = 0    
    
        for room_local in room_list_local:
            room_local.is_valid = 0
    
        for room_macross in room_list_macross:
            room_local = room_list_find(room_list_local, room_macross['room_id'])
            print room_macross['room_id'], room_macross['room_name'], room_macross['is_valid']
            if(room_local == None):
                room_insert(self.platform, room_macross['room_id'], room_macross['room_name'], room_macross['is_valid'], begin_time)                
                num_insert += 1
            else:
                room_local.room_id           = room_macross['room_id']
                room_local.room_name         = room_macross['room_name']
                room_local.is_valid          = room_macross['is_valid']
                room_local.check_time        = begin_time
                room_local.save()
                num_update += 1
                
        for room_local in room_list_local:
            if(room_local.is_valid == 0):
                room_local.delete()
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
     
        
class Thread_ADD_HOT_TASKS(threading.Thread):
    #platform = ''
    #record = None
    
    def __init__(self, the_platform, the_record):
        super(Thread_ADD_HOT_TASKS, self).__init__()        
        self.platform = the_platform
        self.record = the_record
        
        
    def run(self):
        result = do_add_hot_tasks(self.platform, self.record)
        return result
       


class Thread_DELETE_COLD_TASKS(threading.Thread):
    #platform = ''
    #record = None
    
    def __init__(self, the_platform, the_record):
        super(Thread_DELETE_COLD_TASKS, self).__init__()        
        self.platform = the_platform
        self.record = the_record
        
        
    def run(self):
        now_time = time.localtime(time.time())        
        begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        self.record.begin_time = begin_time
        self.record.status = 1
        self.record.save()
    
        room_id = self.record.name
        num_deleting = self.record.memo
        total_num = string.atoi(num_deleting)
        
        ms_list = get_ms_list_in_room(self.platform, room_id)
        if(len(ms_list) <= 0):
            now_time = time.localtime(time.time())        
            end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
            output = 'now: %s, ' % (end_time)
            output += 'room_id: %s, ' % (room_id)
            output += 'num_deleting: %s, ' % (num_deleting)
            output += 'ms num: %d, ' % (len(ms_list))
            self.record.end_time = end_time
            self.record.status = 2        
            self.record.memo = output
            self.record.save()
            return False
        
        print 'ms_list num: %d' % (len(ms_list))
        file_name = 'cold_tasks_%s_%s.log' % (room_id, num_deleting)
        log_file = open(file_name, 'w')
        
        ms_all = MS_ALL(self.platform, ms_list)
        ms_all.get_tasks()
            
        num = 0
        result = False
        tasks = get_tasks_local(self.platform) 
        print 'tasks count: %d' % (tasks.count())
        cold_tasks = tasks.order_by('cold1')
        print 'cold_tasks count: %d' % (cold_tasks.count())
        for task in cold_tasks:
            one_ms = ms_all.find_task(task.hash)
            if(one_ms != None):
                #print '%s delete' % (task.hash)
                log_file.write('[%f]%s delete from %s\n' % (task.cold1, task.hash, one_ms.db_record.controll_ip))
                result = ms_all.delete_cold_task(one_ms, task.hash)
                if(result == False):
                    break
                num += 1
                if(num >= total_num):
                    break
            else:
                #print '%s non_exist' % (task.hash)
                log_file.write('[%f]%s non_exist\n' % (task.cold1, task.hash))
    
        log_file.close()
        
        ms_all.do_delete()
        
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_id: %s, ' % (room_id)
        output += 'num_deleting: %s, ' % (num_deleting)
        output += 'ms num: %d, ' % (len(ms_list))
        output += 'task num: %d, ' % (num)
        print output
        self.record.end_time = end_time
        self.record.status = 2        
        self.record.memo = output
        self.record.save()
   
    
        
class Thread_SYNC_ROOM_STATUS(threading.Thread):
    #platform = ''
    #record = None
    
    def __init__(self, the_platform, the_record):
        super(Thread_SYNC_ROOM_STATUS, self).__init__()        
        self.platform = the_platform
        self.record = the_record
        
        
    def run(self):
        result = do_sync_room_status(self.platform, self.record)
        return result
    
        now_time = time.localtime(time.time())        
        begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        self.record.begin_time = begin_time
        self.record.status = 1
        self.record.save()
    
        room_ids = self.record.memo
        room_id_list = room_ids.split(',')
        
        ms_num = 0
        for room_id in room_id_list:
            print 'room_id=%s' % (room_id)
            ms_list = get_ms_list_in_room(self.platform, room_id)
            for ms in ms_list:
                print 'ms_ip=%s' % (str(ms.controll_ip))                
                MS.views.get_ms_status(ms)
                ms_num += 1
                    
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_ids: %s, ' % (room_ids)
        output += 'ms num: %d, ' % (ms_num)
        print output
        self.record.end_time = end_time
        self.record.status = 2        
        self.record.memo = output
        self.record.save()
       
    
                       
def sync_room_db(request, platform):  
    print 'sync_room_db'
    print request.REQUEST
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'sync_room_db'
    operation1['name'] = today
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = ''
        
    output = ''
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
            # start thread.
            t = Thread_SYNC_ROOM_DB(platform, record)            
            t.start()
    else:
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    
    return HttpResponse(output)     



def add_hot_tasks(request, platform):
    print 'add_hot_tasks'
    print request.REQUEST
    
    room_id = request.REQUEST['room_id']
    num_dispatching = request.REQUEST['num_dispatching']
    #num_deleting = request.REQUEST['num_deleting']
    print 'room_id: %s, num_dispatching: %s' % (room_id, num_dispatching)
   
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'add_hot_tasks'
    operation1['name'] = room_id
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = num_dispatching
        
    output = ''
    records = operation.views.get_operation_record_undone(platform, operation1['type'], operation1['name'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
            # start thread.
            t = Thread_ADD_HOT_TASKS(platform, record)            
            t.start()
    else:
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    
    return_datas = {'success':True, 'data':output, "dispatch_time":dispatch_time}    
    return HttpResponse(json.dumps(return_datas))   


def delete_cold_tasks(request, platform):
    print 'delete_cold_tasks'    
    
    room_id = request.REQUEST['room_id']
    num_deleting = request.REQUEST['num_deleting']
    #num_deleting = request.REQUEST['num_deleting']
    print 'room_id: %s, num_deleting: %s' % (room_id, num_deleting)
   
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'delete_cold_tasks'
    operation1['name'] = room_id
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = num_deleting
        
    output = ''
    records = operation.views.get_operation_record_undone(platform, operation1['type'], operation1['name'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
            # start thread.
            t = Thread_DELETE_COLD_TASKS(platform, record)            
            t.start()
    else:
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    
    return_datas = {'success':True, 'data':output, "dispatch_time":dispatch_time}    
    return HttpResponse(json.dumps(return_datas))   



def sync_room_status(request, platform):  
    print 'sync_room_status'    
    #ids = request.REQUEST['ids']
    #print ids
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'sync_room_status'
    operation1['name'] = today
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    #operation1['memo'] = ids
    operation1['memo'] = ''
        
    output = ''
    records = operation.views.get_operation_record_undone(platform, operation1['type'], operation1['name'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
            # start thread.
            t = Thread_SYNC_ROOM_STATUS(platform, record)            
            t.start()
    else:
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
    
    return HttpResponse(output)    


    