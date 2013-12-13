#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import time
import string
from multiprocessing import Process

import DB.db
import MS.models
import operation.views
import task.views
import threading
from ms import *
import MS.views
import datetime

import gc
import sys
                                           
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
    
    kwargs = {}
    
    v_room_id = ''
    if 'room_id' in request.REQUEST:
        v_room_id = request.REQUEST['room_id']
    if(v_room_id != ''):
        kwargs['room_id'] = v_room_id
        
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
    
    rooms = get_room_local(platform)
    rooms1 = rooms.filter(**kwargs)
    rooms2 = None
    if(len(order_condition) > 0):
        rooms2 = rooms1.order_by(order_condition)[start_index:start_index+limit_num]
    else:
        rooms2 = rooms1[start_index:start_index+limit_num]
    
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = rooms1.count()
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
        title = '<h1>id: %s, ms_num: %d</h1>' % (room_id, len(ms_list))
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


'''
def do_add_hot_tasks(platform, record):
    # Enable automatic garbage collection.
    gc.enable()
    #gc.set_debug(gc.DEBUG_LEAK) 
    # Set the garbage collection debugging flags.
    #gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | \
    #    gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
    gc.set_debug( gc.DEBUG_UNCOLLECTABLE | \
        gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS | gc.DEBUG_SAVEALL)
    
    a=range(10000*10000)
    del a
        
    print 'begin collect...'
    _unreachable = gc.collect()
    print 'unreachable object num:%d' % _unreachable
    print 'garbage object num:%d' % len(gc.garbage)
    index = 0
    for garbage in gc.garbage: 
        print 'index=[%d], type=[%s]' % (index, type(garbage))        
        #print garbage
        index += 1
        
    return True
'''

'''
def do_add_hot_tasks(platform, record):
    # Enable automatic garbage collection.
    gc.enable()
    #gc.set_debug(gc.DEBUG_LEAK) 
    # Set the garbage collection debugging flags.
    #gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | \
    #    gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
    gc.set_debug( gc.DEBUG_UNCOLLECTABLE | \
        gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS | gc.DEBUG_SAVEALL)
    
    hot_tasks = task.views.get_hot_tasks_local(platform)
    print 'hot_tasks count: %d' % (hot_tasks.count())
    for task1 in hot_tasks:
        print 'hot task: %d, %s' % (task1.hot, task1.hash)       
    
    print 'hot_tasks ref count0:%d' % sys.getrefcount(hot_tasks)
    del hot_tasks
    try:
        print 'hot_tasks ref count1:%d' % sys.getrefcount(hot_tasks)
    except UnboundLocalError:
        print 'hot_tasks is invalid!'
        
    print 'begin collect...'
    _unreachable = gc.collect()
    print 'unreachable object num:%d' % _unreachable
    print 'garbage object num:%d' % len(gc.garbage)
    index = 0
    count = 0
    for garbage in gc.garbage:    
        if(index > 300000):                
            print 'index=[%d], type=[%s]' % (index, type(garbage))        
            print garbage
            count += 1
            if(count > 50):
                break
        index += 1
        
    return True
'''


def do_add_hot_tasks(platform, record):
    # Enable automatic garbage collection.
    gc.enable()
    #gc.set_debug(gc.DEBUG_LEAK) 
    # Set the garbage collection debugging flags.
    #gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | \
    #    gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
    gc.set_debug( gc.DEBUG_UNCOLLECTABLE | \
        gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS | gc.DEBUG_SAVEALL)
        
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()

    room_id = record.name
    fields = record.memo.split('|')
    s_suggest_task_number = fields[0]
    s_num_dispatching = fields[1]
    
    suggest_task_number = string.atoi(s_suggest_task_number)
    num_dispatching = string.atoi(s_num_dispatching)
    
    ms_list = get_ms_list_in_room(platform, room_id)
    if(len(ms_list) <= 0):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_id: %s, ' % (room_id)
        output += 'suggest_task_number: %d, ' % (suggest_task_number)
        output += 'num_dispatching: %d, ' % (num_dispatching)
        output += 'ms num: %d, ' % (len(ms_list))
        record.end_time = end_time
        record.status = 2        
        record.memo = output
        record.save()
        return False
        
    print 'ms_list num: %d' % (len(ms_list))            
    
    ms_all = MS_ALL(platform, ms_list)
    #ms_all.get_tasks()
    ms_all.get_tasks_macross()
    
    ms_tasks_num = ms_all.get_tasks_num()
    total_dispatch_num = num_dispatching
    if(suggest_task_number > 0):        
        if(suggest_task_number > ms_tasks_num):
            total_dispatch_num = suggest_task_number - ms_tasks_num
            
    if(total_dispatch_num <= 0):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_id: %s, ' % (room_id)
        output += 'suggest_task_number: %d, ' % (suggest_task_number)
        output += 'num_dispatching: %d, ' % (num_dispatching)
        output += 'ms num: %d, ' % (len(ms_list))
        output += 'ms tasks num: %d, ' % (ms_tasks_num)
        output += 'total_dispatch_num: %d, ' % (total_dispatch_num)
        print output
        record.end_time = end_time
        record.status = 2        
        record.memo = output
        record.save()
        return True
    
    print 'total_dispatch_num count: %d' % (total_dispatch_num)
    
    file_name = 'hot_tasks_%s_%d_%d.log' % (room_id, suggest_task_number, num_dispatching)
    log_file = open(file_name, 'w')
            
    num = 0
    result = False
    #all_tasks = task.views.get_tasks_local(platform) 
    #print 'tasks count: %d' % (all_tasks.count())
    #hot_tasks = all_tasks.order_by('-hot')
    #hot_tasks = all_tasks.filter(hot__gt=0).order_by('-hot')
    hot_tasks = task.views.get_hot_tasks_local(platform)
    print 'hot_tasks count: %d' % (hot_tasks.count())
    #for task1 in hot_tasks:
    for task1 in hot_tasks.iterator():
        #print 'hot task: %d, %s' % (task1.hot, task1.hash)
        one_ms = ms_all.find_task(task1.hash)
        if(one_ms == None):                        
            result = ms_all.dispatch_hot_task(task1.hash)
            if(result == None):
                #print '%d, %s, can not be dispatched\n' % (task1.hot, task1.hash) 
                log_file.write('%d, %s, can not be dispatched\n' % (task1.hot, task1.hash))                
                break
            else:
                #print '%d, %s, dispatched to %d, %s' % (task1.hot, task1.hash, result.db_record.server_id, result.db_record.controll_ip)
                log_file.write('%d, %s, dispatched to %d, %s\n' % (task1.hot, task1.hash, result.db_record.server_id, result.db_record.controll_ip))
            num += 1
            if(num >= total_dispatch_num):
                break
        else:
            #print '%d, %s, exist at %d, %s' % (task1.hot, task1.hash, one_ms.db_record.server_id, one_ms.db_record.controll_ip)
            log_file.write('%d, %s, exist at %d, %s\n' % (task1.hot, task1.hash, one_ms.db_record.server_id, one_ms.db_record.controll_ip))
    
    log_file.close()    
    
    ms_all.do_dispatch()
            
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'room_id: %s, ' % (room_id)
    output += 'suggest_task_number: %d, ' % (suggest_task_number)
    output += 'num_dispatching: %d, ' % (num_dispatching)
    output += 'ms num: %d, ' % (len(ms_list))
    output += 'ms tasks num: %d, ' % (ms_tasks_num)
    output += 'total_dispatch_num: %d, ' % (total_dispatch_num)
    print output
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
    
    print 'hot_tasks ref count0:%d' % sys.getrefcount(hot_tasks)
    del hot_tasks
    try:
        print 'hot_tasks ref count1:%d' % sys.getrefcount(hot_tasks)
    except UnboundLocalError:
        print 'hot_tasks is invalid!'
    
    #print 'all_tasks ref count0:%d' % sys.getrefcount(all_tasks)
    #del all_tasks
    #try:
    #    print 'tasks all_tasks count1:%d' % sys.getrefcount(all_tasks)
    #except UnboundLocalError:
    #    print 'all_tasks is invalid!'
       
    print 'ms_all ref count0:%d' % sys.getrefcount(ms_all)
    del ms_all
    try:
        print 'ms_all ref count1:%d' % sys.getrefcount(ms_all)
    except UnboundLocalError:
        print 'ms_all is invalid!'
         
    print 'ms_list ref count0:%d' % sys.getrefcount(ms_list)
    del ms_list
    try:
        print 'ms_list ref count1:%d' % sys.getrefcount(ms_list)
    except UnboundLocalError:
        print 'ms_list is invalid!' 
        
    print 'begin collect...'
    _unreachable = gc.collect()
    print 'unreachable object num:%d' % _unreachable
    print 'garbage object num:%d' % len(gc.garbage)
    '''
    index = 0
    for garbage in gc.garbage:
        print 'index=[%d], type=[%s]' % (index, type(garbage))        
        #print garbage
        index += 1
    '''
                
    return True


def do_delete_cold_tasks(platform, record):
    # Enable automatic garbage collection.
    gc.enable()
    #gc.set_debug(gc.DEBUG_LEAK) 
    # Set the garbage collection debugging flags.
    #gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | \
    #    gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
    gc.set_debug( gc.DEBUG_UNCOLLECTABLE | \
        gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS | gc.DEBUG_SAVEALL)
    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    room_id = record.name
    fields = record.memo.split('|')
    s_suggest_task_number = fields[0]
    s_num_deleting = fields[1]
    
    suggest_task_number = string.atoi(s_suggest_task_number)
    num_deleting = string.atoi(s_num_deleting)
        
    ms_list = get_ms_list_in_room(platform, room_id)
    if(len(ms_list) <= 0):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_id: %s, ' % (room_id)
        output += 'suggest_task_number: %d, ' % (suggest_task_number)
        output += 'num_deleting: %d, ' % (num_deleting)
        output += 'ms num: %d, ' % (len(ms_list))
        record.end_time = end_time
        record.status = 2        
        record.memo = output
        record.save()
        return False
        
    print 'ms_list num: %d' % (len(ms_list))
    
    ms_all = MS_ALL(platform, ms_list)
    #ms_all.get_tasks()
    ms_all.get_tasks_macross()
    
    ms_tasks_num = ms_all.get_tasks_num()    
    total_delete_num = num_deleting
    if(suggest_task_number > 0):
        if(ms_tasks_num > suggest_task_number):
            total_delete_num = ms_tasks_num - suggest_task_number
    
    if(total_delete_num <= 0):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_id: %s, ' % (room_id)
        output += 'suggest_task_number: %d, ' % (suggest_task_number)
        output += 'num_deleting: %d, ' % (num_deleting)
        output += 'ms num: %d, ' % (len(ms_list))
        output += 'ms tasks num: %d, ' % (ms_tasks_num)
        output += 'total_delete_num: %d, ' % (total_delete_num)
        print output
        record.end_time = end_time
        record.status = 2        
        record.memo = output
        record.save()
        return True
    
    file_name = 'cold_tasks_%s_%d_%d.log' % (room_id, suggest_task_number, num_deleting)
    log_file = open(file_name, 'w')    
            
    real_delete_num = 0
    result = False
    all_tasks = task.views.get_tasks_local(platform) 
    print 'all_tasks count: %d' % (all_tasks.count())
        
    # rule 1:
    log_file.write('rule 1 begin\n')
    cold_tasks = all_tasks.filter(cold1__lt=-10.0).order_by('cold1', 'hot')
    print 'cold_tasks count: %d' % (cold_tasks.count())
    for task1 in cold_tasks.iterator():
        one_ms = ms_all.find_task(task1.hash)
        if(one_ms != None):
            #print '%s delete' % (task1.hash)            
            result = ms_all.delete_cold_task(one_ms, task1.hash)
            if(result == True):
                log_file.write('[%s, %d, %f]%s delete from %d, %s\n' % (task1.online_time, task1.hot, task1.cold1, task1.hash, one_ms.db_record.server_id, one_ms.db_record.controll_ip))
                real_delete_num += 1
                if(real_delete_num >= total_delete_num):
                    break
            else:
                log_file.write('[%s, %d, %f]%s marked\n' % (task1.online_time, task1.hot, task1.cold1, task1.hash))
        else:
            #print '%s non_exist' % (task1.hash)
            log_file.write('[%s, %d, %f]%s non_exist\n' % (task1.online_time, task1.hot, task1.cold1, task1.hash))
    log_file.write('rule 1 end\n')
    print 'after rule 1, total_delete_num=%d, real_delete_num=%d' % (total_delete_num, real_delete_num) 
    
    print 'cold_tasks ref count0:%d' % sys.getrefcount(cold_tasks)
    del cold_tasks
    try:
        print 'cold_tasks ref count1:%d' % sys.getrefcount(cold_tasks)
    except UnboundLocalError:
        print 'cold_tasks is invalid!'
        
    # rule 2:    
    if(real_delete_num < total_delete_num):
        log_file.write('rule 2 begin\n')
        now = datetime.datetime.now()
        day_delta = 10
        days_ago = now - datetime.timedelta(days=day_delta)
        time_limit = '%04d-%02d-%02d 00:00:00+00:00' % (days_ago.year, days_ago.month, days_ago.day)
        cold_tasks = all_tasks.filter(online_time__lt=time_limit).order_by('hot')
        print 'cold_tasks count: %d' % (cold_tasks.count())
        #cold_tasks2 = cold_tasks.filter(hot__lt=300)
        cold_tasks2 = cold_tasks
        print 'cold_tasks2 count: %d' % (cold_tasks2.count())
        #for task1 in cold_tasks:
        for task1 in cold_tasks2.iterator():
            one_ms = ms_all.find_task(task1.hash)
            if(one_ms != None):
                #print '%s delete' % (task1.hash)                
                result = ms_all.delete_cold_task(one_ms, task1.hash)
                if(result == True):
                    log_file.write('[%s, %d, %f]%s delete from %d, %s\n' % (task1.online_time, task1.hot, task1.cold1, task1.hash, one_ms.db_record.server_id, one_ms.db_record.controll_ip))                    
                    real_delete_num += 1
                    if(real_delete_num >= total_delete_num):
                        break
                else:
                    log_file.write('[%s, %d, %f]%s delete from %d, %s\n' % (task1.online_time, task1.hot, task1.cold1, task1.hash, one_ms.db_record.server_id, one_ms.db_record.controll_ip))
            else:
                #print '%s non_exist' % (task1.hash)
                log_file.write('[%s, %d, %f]%s non_exist\n' % (task1.online_time, task1.hot, task1.cold1, task1.hash))
        log_file.write('rule 2 end\n')
        print 'after rule 2, total_delete_num=%d, real_delete_num=%d' % (total_delete_num, real_delete_num)         
    log_file.close()
    
    ms_all.do_delete()
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'room_id: %s, ' % (room_id)
    output += 'suggest_task_number: %d, ' % (suggest_task_number)
    output += 'num_deleting: %d, ' % (num_deleting)
    output += 'ms num: %d, ' % (len(ms_list))
    output += 'ms tasks num: %d, ' % (ms_tasks_num)
    output += 'total_delete_num: %d, real_delete_num: %d' % (total_delete_num, real_delete_num)
    print output
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
    
    print 'cold_tasks ref count0:%d' % sys.getrefcount(cold_tasks)
    del cold_tasks
    try:
        print 'cold_tasks ref count1:%d' % sys.getrefcount(cold_tasks)
    except UnboundLocalError:
        print 'cold_tasks is invalid!'
    
    print 'all_tasks ref count0:%d' % sys.getrefcount(all_tasks)
    del all_tasks
    try:
        print 'tasks all_tasks count1:%d' % sys.getrefcount(all_tasks)
    except UnboundLocalError:
        print 'all_tasks is invalid!'
       
    print 'ms_all ref count0:%d' % sys.getrefcount(ms_all)
    del ms_all
    try:
        print 'ms_all ref count1:%d' % sys.getrefcount(ms_all)
    except UnboundLocalError:
        print 'ms_all is invalid!'
         
    print 'ms_list ref count0:%d' % sys.getrefcount(ms_list)
    del ms_list
    try:
        print 'ms_list ref count1:%d' % sys.getrefcount(ms_list)
    except UnboundLocalError:
        print 'ms_list is invalid!' 
        
    print 'begin collect...'
    _unreachable = gc.collect()
    print 'unreachable object num:%d' % _unreachable
    print 'garbage object num:%d' % len(gc.garbage)
    '''
    index = 0
    for garbage in gc.garbage:
        print 'index=[%d], type=[%s]' % (index, type(garbage))        
        #print garbage
        index += 1
    '''
    
    return True

'''
def do_delete_cold_tasks(platform, record):
    # Enable automatic garbage collection.
    gc.enable()
    #gc.set_debug(gc.DEBUG_LEAK) 
    # Set the garbage collection debugging flags.
    #gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | \
    #    gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
    gc.set_debug( gc.DEBUG_UNCOLLECTABLE | \
        gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS | gc.DEBUG_SAVEALL)
        
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    room_id = record.name
    fields = record.memo.split('|')
    s_suggest_task_number = fields[0]
    s_num_deleting = fields[1]
    
    suggest_task_number = string.atoi(s_suggest_task_number)
    num_deleting = string.atoi(s_num_deleting)
        
    ms_list = get_ms_list_in_room(platform, room_id)
    if(len(ms_list) <= 0):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_id: %s, ' % (room_id)
        output += 'suggest_task_number: %d, ' % (suggest_task_number)
        output += 'num_deleting: %d, ' % (num_deleting)
        output += 'ms num: %d, ' % (len(ms_list))
        record.end_time = end_time
        record.status = 2        
        record.memo = output
        record.save()
        return False
        
    print 'ms_list num: %d' % (len(ms_list))
    
    ms_all = MS_ALL(platform, ms_list)
    #ms_all.get_tasks()
    ms_all.get_tasks_macross()
    
    ms_tasks_num = ms_all.get_tasks_num()    
    total_delete_num = num_deleting
    if(suggest_task_number > 0):
        if(ms_tasks_num > suggest_task_number):
            total_delete_num = ms_tasks_num - suggest_task_number
    
    if(total_delete_num <= 0):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'room_id: %s, ' % (room_id)
        output += 'suggest_task_number: %d, ' % (suggest_task_number)
        output += 'num_deleting: %d, ' % (num_deleting)
        output += 'ms num: %d, ' % (len(ms_list))
        output += 'ms tasks num: %d, ' % (ms_tasks_num)
        output += 'total_delete_num: %d, ' % (total_delete_num)
        print output
        record.end_time = end_time
        record.status = 2        
        record.memo = output
        record.save()
        return True
    
    file_name = 'cold_tasks_%s_%d_%d.log' % (room_id, suggest_task_number, num_deleting)
    log_file = open(file_name, 'w')    
            
    real_delete_num = 0
    result = False
    #all_tasks = task.views.get_tasks_local(platform) 
    #print 'all_tasks count: %d' % (all_tasks.count())
        
    # rule 1:
    log_file.write('rule 1 begin\n')
    #cold_tasks = all_tasks.filter(cold1__lt=-30.0).order_by('cold1', 'hot')
    #cold_tasks = all_tasks.filter(cold1__lt=-10.0).order_by('cold1', 'hot')
    #print 'cold_tasks count: %d' % (cold_tasks.count())
    cold_tasks = task.views.get_cold_tasks_rule1(platform)
    print 'cold_tasks count: %d' % (len(cold_tasks))
    #for task1 in cold_tasks.iterator():
    for task1 in cold_tasks:
        #print 'cold_task %s, %s, %s, %s, %s' % (task1['hash'], task1['online_time'], task1['hot'], task1['cold1'], task1['last_hit_time'])
        cold1 = string.atof(task1['cold1'])
        if(cold1 >= -10.0):
            break
        one_ms = ms_all.find_task(task1['hash'])
        if(one_ms != None):
            #print '%s delete' % (task1.hash)            
            result = ms_all.delete_cold_task(one_ms, task1['hash'])
            if(result == True):
                log_file.write('[%s, %s, %s]%s delete from %d, %s\n' % (task1['online_time'], task1['hot'], task1['cold1'], task1['hash'], one_ms.db_record.server_id, one_ms.db_record.controll_ip))
                real_delete_num += 1
                if(real_delete_num >= total_delete_num):
                    break
            else:
                log_file.write('[%s, %s, %s]%s marked\n' % (task1['online_time'], task1['hot'], task1['cold1'], task1['hash']))
        else:
            #print '%s non_exist' % (task1.hash)
            log_file.write('[%s, %s, %s]%s non_exist\n' % (task1['online_time'], task1['hot'], task1['cold1'], task1['hash']))
    log_file.write('rule 1 end\n')
            
    print 'real_delete_num=%d, total_delete_num=%d' % (real_delete_num, total_delete_num)
    
    # rule 2:    
    if(real_delete_num < total_delete_num):
        log_file.write('rule 2 begin\n')
        now = datetime.datetime.now()
        #day_delta = 30
        day_delta = 10
        days_ago = now - datetime.timedelta(days=day_delta)
        #time_limit = '%04d-%02d-%02d 00:00:00+00:00' % (days_ago.year, days_ago.month, days_ago.day)
        time_limit = '%04d-%02d-%02d 00:00:00' % (days_ago.year, days_ago.month, days_ago.day)
        #cold_tasks = all_tasks.filter(online_time__lt=time_limit).order_by('hot')
        #cold_tasks = all_tasks.order_by('hot')
        cold_tasks = task.views.get_cold_tasks_rule2(platform, time_limit)
        print 'cold_tasks count: %d' % (len(cold_tasks))    
        #for task1 in cold_tasks:
        for task1 in cold_tasks:
            #print 'cold_task %s, %s, %s, %s, %s' % (task1['hash'], task1['online_time'], task1['hot'], task1['cold1'], task1['last_hit_time'])
            one_ms = ms_all.find_task(task1['hash'])
            if(one_ms != None):
                #print '%s delete' % (task1.hash)                
                result = ms_all.delete_cold_task(one_ms, task1['hash'])
                if(result == True):
                    log_file.write('[%s, %s, %s]%s delete from %d, %s\n' % (task1['online_time'], task1['hot'], task1['cold1'], task1['hash'], one_ms.db_record.server_id, one_ms.db_record.controll_ip))                    
                    real_delete_num += 1
                    if(real_delete_num >= total_delete_num):
                        break
                else:
                    log_file.write('[%s, %s, %s]%s delete from %d, %s\n' % (task1['online_time'], task1['hot'], task1['cold1'], task1['hash'], one_ms.db_record.server_id, one_ms.db_record.controll_ip))
            else:
                #print '%s non_exist' % (task1.hash)
                log_file.write('[%s, %s, %s]%s non_exist\n' % (task1['online_time'], task1['hot'], task1['cold1'], task1['hash']))
        log_file.write('rule 2 end\n')
        
    log_file.close()
    
    ms_all.do_delete()
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'room_id: %s, ' % (room_id)
    output += 'suggest_task_number: %d, ' % (suggest_task_number)
    output += 'num_deleting: %d, ' % (num_deleting)
    output += 'ms num: %d, ' % (len(ms_list))
    output += 'ms tasks num: %d, ' % (ms_tasks_num)
    output += 'total_delete_num: %d, real_delete_num: %d' % (total_delete_num, real_delete_num)
    print output
    record.end_time = end_time
    record.status = 2        
    record.memo = output
    record.save()
        
    print 'begin collect...'
    _unreachable = gc.collect()
    print 'unreachable object num:%d' % _unreachable
    print 'garbage object num:%d' % len(gc.garbage)
        
    return True
'''
      
    
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
        result = do_delete_cold_tasks(self.platform, self.record)
        return result   
    
        
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
    
                       
def sync_room_db(request, platform):  
    print 'sync_room_db'
    print request.REQUEST
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'sync_room_db'
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
    return_datas['success'] = True
    return_datas['data'] = output
        
    if(start_now == True):
        # start thread.
        #t = Thread_SYNC_ROOM_DB(platform, record)            
        #t.start()
        # start process
        p = Process(target=do_sync_room_db, args=(platform, record))
        p.start()
    
    return HttpResponse(json.dumps(return_datas))   



def add_hot_tasks(request, platform):
    print 'add_hot_tasks'
    print request.REQUEST
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
            
    v_room_id = request.REQUEST['room_id']
    v_suggest_task_number = request.REQUEST['suggest_task_number']
    v_num_dispatching = request.REQUEST['num_dispatching']
    print 'room_id: %s, suggest_task_number:%s, num_dispatching: %s' % (v_room_id, v_suggest_task_number, v_num_dispatching)
    
    rooms = get_room_local(platform)
    room_list = rooms.filter(room_id=v_room_id)
    if(len(room_list) <= 0):
        return_datas = {'success':False, 'data':'error room_id=%s' % v_room_id} 
        return HttpResponse(json.dumps(return_datas))
      
    the_room = room_list[0]
    the_room.suggest_task_number = v_suggest_task_number
    the_room.num_dispatching = v_num_dispatching
    the_room.save()    
   
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'add_hot_tasks'
    operation1['name'] = v_room_id
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = '%s|%s' % (v_suggest_task_number, v_num_dispatching)
        
    output = ''
    records = operation.views.get_operation_record_undone(platform, operation1['type'], operation1['name'])    
    if(len(records) > 0):
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas = {'success':False, 'data':output} 
        return HttpResponse(json.dumps(return_datas))
        
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas = {'success':False, 'data':output} 
        return HttpResponse(json.dumps(return_datas)) 
    
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)    
    
    if(start_now == True):
        # start thread.
        #t = Thread_ADD_HOT_TASKS(platform, record)            
        #t.start()
        # start process
        p = Process(target=do_add_hot_tasks, args=(platform, record))
        p.start()    
    
    return_datas = {'success':True, 'data':output, "dispatch_time":dispatch_time}    
    return HttpResponse(json.dumps(return_datas)) 


def delete_cold_tasks(request, platform):
    print 'delete_cold_tasks'   
    print request.REQUEST  
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
            
    v_room_id = request.REQUEST['room_id']
    v_suggest_task_number = request.REQUEST['suggest_task_number']
    v_num_deleting = request.REQUEST['num_deleting']    
    print 'room_id: %s, suggest_task_number:%s, num_deleting: %s' % (v_room_id, v_suggest_task_number, v_num_deleting)
    
    rooms = get_room_local(platform)
    room_list = rooms.filter(room_id=v_room_id)
    if(len(room_list) <= 0):
        return_datas = {'success':False, 'data':'error room_id=%s' % v_room_id} 
        return HttpResponse(json.dumps(return_datas))
      
    the_room = room_list[0]
    the_room.suggest_task_number = v_suggest_task_number
    the_room.num_deleting = v_num_deleting
    the_room.save()    
   
    now_time = time.localtime(time.time())    
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation1 = {}
    operation1['type'] = 'delete_cold_tasks'
    operation1['name'] = v_room_id
    operation1['user'] = request.user.username
    operation1['dispatch_time'] = dispatch_time
    operation1['memo'] = '%s|%s' % (v_suggest_task_number, v_num_deleting)
    
    output = ''
    records = operation.views.get_operation_record_undone(platform, operation1['type'], operation1['name'])
    if(len(records) > 0):
        for record in records:
            output += 'operation exist, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)
        return_datas = {'success':False, 'data':output} 
        return HttpResponse(json.dumps(return_datas))
        
    record = operation.views.create_operation_record_by_dict(platform, operation1)
    if(record == None):
        output += 'operation create failure'
        return_datas = {'success':False, 'data':output} 
        return HttpResponse(json.dumps(return_datas)) 
    
    output += 'operation add, id=%d, type=%s, name=%s, dispatch_time=%s, status=%d' % (record.id, record.type, record.name, record.dispatch_time, record.status)    
    
    if(start_now == True):
        # start thread.
        #t = Thread_DELETE_COLD_TASKS(platform, record)            
        #t.start()    
        # start process
        p = Process(target=do_delete_cold_tasks, args=(platform, record))
        p.start()  
    
    return_datas = {'success':True, 'data':output, "dispatch_time":dispatch_time}    
    return HttpResponse(json.dumps(return_datas))



def sync_room_status(request, platform):  
    print 'sync_room_status' 
    print request.REQUEST   
    #ids = request.REQUEST['ids']
    #print ids
    
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
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
    return_datas['success'] = True
    return_datas['data'] = output
        
    if(start_now == True):
        # start thread.
        #t = Thread_SYNC_ROOM_STATUS(platform, record)            
        #t.start()
        # start process
        p = Process(target=do_sync_room_status, args=(platform, record))
        p.start()
    
    return HttpResponse(json.dumps(return_datas))    


    
    