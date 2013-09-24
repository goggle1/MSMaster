#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import string
import time
import sys
#from DB.db import DB_MYSQL
#from DB.db import DB_CONFIG
from DB.db import *
import operation.views
import threading
import datetime

def day_diff(date1, date2):
    d1 = datetime.datetime(string.atoi(date1[0:4]), string.atoi(date1[5:7]), string.atoi(date1[8:10]))
    d2 = datetime.datetime(string.atoi(date2[0:4]), string.atoi(date2[5:7]), string.atoi(date2[8:10]))
    return (d1-d2).days


def task_insert(platform, hash_id, v_online_time, v_is_valid, v_hot, v_cold1, v_cold2, v_cold3, v_last_hit_time, v_total_hits_num):
    if(platform == 'mobile'):
        hash_local = models.mobile_task(hash      = hash_id,                  \
                                       online_time        = v_online_time,    \
                                       is_valid           = v_is_valid,       \
                                       hot                = v_hot,            \
                                       cold1              = v_cold1,          \
                                       cold2              = v_cold2,          \
                                       cold3              = v_cold3,          \
                                       last_hit_time      = v_last_hit_time,  \
                                       total_hits_num     = v_total_hits_num  \
                                       ) 
        hash_local.save()
    elif(platform == 'pc'):
        hash_local = models.pc_task(hash      = hash_id,                  \
                                       online_time        = v_online_time,    \
                                       is_valid           = v_is_valid,       \
                                       hot                = v_hot,            \
                                       cold1              = v_cold1,          \
                                       cold2              = v_cold2,          \
                                       cold3              = v_cold3,          \
                                       last_hit_time      = v_last_hit_time,  \
                                       total_hits_num     = v_total_hits_num  \
                                       )    
        hash_local.save()
        
    

def get_task_local(platform):
    ms_list = []
    if(platform == 'mobile'):
        ms_list = models.mobile_task.objects.all()
    elif(platform == 'pc'):
        ms_list = models.pc_task.objects.all()    
    return ms_list
        

def get_task_list(request, platform):
    print 'get_task_list'
    print request.REQUEST
            
    start = request.REQUEST['start']
    limit = request.REQUEST['limit']
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    print '%d,%d' % (start_index, limit_num)
    
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
       
    tasks2 = [] 
    tasks = get_task_local(platform)
        
    #now_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.localtime(time.time()))
    #print now_time
    if(len(order_by) > 0):        
        #tasks2 = models.mobile_task.objects.order_by(order_by)[start_index:limit_num]
        tasks2 = tasks.order_by(order_by)[start_index:start_index+limit_num]     
    else:
        #tasks2 = models.mobile_task.objects.all()[start_index:limit_num]
        tasks2 = tasks[start_index:start_index+limit_num]
    #now_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.localtime(time.time()))
    #print now_time
        
    return_datas = {'success':True, 'data':[]}
    #now_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.localtime(time.time()))
    #print now_time
    return_datas['total_count'] = tasks.count()
    print tasks.count()
    #now_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.localtime(time.time()))
    #print now_time
        
    #now_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.localtime(time.time()))
    #print now_time
    for task in tasks2:        
        return_datas['data'].append(task.todict())            
    #now_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.localtime(time.time()))
    #print now_time    
        
    return HttpResponse(json.dumps(return_datas))


def down_hot_tasks(request, platform):
    print 'down_hot_tasks'
    print request.REQUEST    
    task_num = request.REQUEST['task_num']
    
    tasks = get_task_local(platform) 
    tasks2 = tasks.order_by('-hot')[0:task_num]
    
    output = ''
    for task in tasks2:
        output += '%s,%s,%s\n' % (task.hash, task.online_time, task.hot)
            
    response = HttpResponse(output, content_type='text/comma-separated-values')
    response['Content-Disposition'] = 'attachment; filename=hot_tasks_%s_%s.csv' % (platform, task_num)
    return response


def down_cold_tasks(request, platform):
    print 'down_cold_tasks'
    print request.REQUEST  
      
    task_num = request.REQUEST['task_num']
        
    tasks = get_task_local(platform)  
    #tasks2 = tasks.order_by('cold1,cold2,cold3')
    tasks2 = tasks.order_by('cold1')[0:task_num]
       
    output = ''
    for task in tasks2:
        output += '%s,%s,%s,%s,%s\n' % (task.hash, task.online_time, task.cold1, task.cold2, task.cold3)
    
    response = HttpResponse(output, content_type='text/comma-separated-values')
    response['Content-Disposition'] = 'attachment; filename=cold_tasks_%s_%s.csv' % (platform, task_num)
    return response


def get_task_macross(platform, begin_date, end_date):
    ms_list = []
    sql = ""
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    where_condition = ''
    if(len(begin_date) > 0):
        begin_time = '%s-%s-%s 00:00:00' % (begin_date[0:4], begin_date[4:6], begin_date[6:8])
        where_condition += " where create_time >= '%s'" % (begin_time)
    if(len(end_date) > 0):
        end_time = '%s-%s-%s 00:00:00' % (end_date[0:4], end_date[4:6], end_date[6:8])
        where_condition += " and create_time < '%s'" % (end_time)
    
    db = DB_MYSQL()
    db.connect(DB_CONFIG.host, DB_CONFIG.port, DB_CONFIG.user, DB_CONFIG.password, DB_CONFIG.db)
    if(platform == 'mobile'):
        sql = "select dat_hash, create_time from fs_mobile_dat" + where_condition
    elif(platform == 'pc'):
        sql = "select task_hash, create_time from fs_task" + where_condition   
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        ms = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                ms['hash'] = r
            elif(col_num == 1):
                ms['online_time'] = r
            col_num += 1
        ms_list.append(ms)    
    
    db.close()  
     
    return ms_list


def task_list_find(task_list, hashid):
    for task in task_list:
        if(task.hash == hashid):
            return task
    return None



def show_task_list(request, platform):  
    output = ''
    hashs = request.REQUEST['hashs']    
    hash_list = hashs.split(',')
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    
    db = DB_MYSQL()
    #db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
    db.connect(DB_CONFIG.host, DB_CONFIG.port, DB_CONFIG.user, DB_CONFIG.password, DB_CONFIG.db)
    if(platform == 'mobile'):
        sql = 'select dat_hash, cid, serialid, media_id, dat_name from fs_mobile_dat where dat_hash='
    elif(platform == 'pc'):
        sql = 'select a.hashid, a.dat_id, a.serialid, b.media_id, a.dat_name from fs_dat_file a, fs_media_serials b where a.serialid=b.serialid and a.hashid='    
        
    for hashid in hash_list:
        title = '<h1>hash: %s</h1>' % (hashid)
        output += title          
        sql_where = sql + '"%s"'%(hashid)
        db.execute(sql_where)
        
        task_list = []
        for row in db.cur.fetchall():
            task = {}      
            col_num = 0  
            for r in row:
                if(col_num == 0):
                    task['hash'] = r
                elif(col_num == 1):
                    task['cid'] = r
                elif(col_num == 2):
                    task['serialid'] = r
                elif(col_num == 3):
                    task['media_id'] = r
                elif(col_num == 4):
                    task['dat_name'] = r
                col_num += 1
            task_list.append(task)   
        
        for task in task_list:
            output += '%s,%s,%s,%s,%s\n' % (task['hash'], task['cid'], task['serialid'], task['media_id'], task['dat_name']) 
      
    db.close()  
      
    return HttpResponse(output)


def upload_sub_hits_num(platform, previous_day):
    num_insert2 = 0
    num_update2 = 0
    # check if uploaded
    #     true: sub it,
    #     false: do nothing.
    operation_list = operation.views.get_operation_by_type_name(platform, 'upload_hits_num', previous_day)
    if(len(operation_list) <= 0):
        print 'sub_hits_num %s not uploaded' % (previous_day)
        return (True, num_insert2, num_update2)
        
    upload_file = ""
    if(platform == 'mobile'):
        upload_file = HITS_FILE.template_mobile % (previous_day)
    elif(platform == 'pc'):
        upload_file = HITS_FILE.template_pc % (previous_day)
    print 'sub_hits_num %s' % (upload_file)
       
    line_num = 0
    try:
        hits_file = open(upload_file, "r")
    except:            
        return (False, num_insert2, num_update2)
        
    hash_list_local = get_task_local(platform)  
        
    content = hits_file.readlines()
    for line in content:
        items = line.split(' ')
        if(len(items) >= 2):
            hits_num = items[0].strip()
            hash_id = items[1].strip()
            print '%s, %s' % (hits_num, hash_id)
            task_list = hash_list_local.filter(hash=hash_id)
            if(len(task_list) > 0):
                print 'update -' 
                hash_local = task_list[0]
                if(hash_local.hot > string.atoi(hits_num)): 
                    hash_local.hot -= string.atoi(hits_num)
                else:
                    hash_local.hot = 0                    
                hash_local.save()
                num_update2 += 1
            else:
                print 'insert -' 
                num_insert2 += 1
        line_num += 1
        #if(line_num > 55):
        #    break
    hits_file.close()
    print 'sub_hits_num line_num=%d, num_insert2=%d, num_update2=%d' % (line_num, num_insert2, num_update2)        
    return (True, num_insert2, num_update2)
    
    
def upload_add_hits_num(platform, hits_date):
    num_insert = 0
    num_update = 0
    
    upload_file = ""
    if(platform == 'mobile'):
        #upload_file = "/home/xiongming/data_analysis/topdata/mo/logdata/logdata_%s_hashid_sort.result" % (hits_date)
        upload_file = HITS_FILE.template_mobile % (hits_date)
    elif(platform == 'pc'):
        upload_file = HITS_FILE.template_mobile % (hits_date)
    print 'add_hits_num %s' % (upload_file)
       
    hits_time = '%s-%s-%sT12:00:00+00:00' % (hits_date[0:4], hits_date[4:6], hits_date[6:8])  
        
    line_num = 0
    try:
        hits_file = open(upload_file, "r")
    except:            
        return (False, num_insert, num_update)
        
    hash_list_local = get_task_local(platform)
                    
    content = hits_file.readlines()
    for line in content:
        items = line.split(' ')
        if(len(items) >= 2):
            hits_num = items[0].strip()
            hash_id = items[1].strip()
            print '%s, %s' % (hits_num, hash_id)
            task_list = hash_list_local.filter(hash=hash_id)
            if(len(task_list) > 0):
                #print 'update %s' % (hash_id)
                hash_local = task_list[0]
                # if last_hit_time is equal to hits_time, it's updated, then do nothing
                if(str(hash_local.last_hit_time) != hits_time):
                    hash_local.hot += string.atoi(hits_num)
                    # if last_hit_time < hits_time, update last_hit_time
                    if(cmp(str(hash_local.last_hit_time), hits_time) < 0):
                        hash_local.last_hit_time = hits_time
                        hash_local.cold1 = 0.0
                    hash_local.total_hits_num += string.atoi(hits_num)
                    hash_local.save()
                num_update += 1
            else:
                print 'insert %s' % (hash_id) 
                v_hits_num = string.atoi(hits_num)
                task_insert(platform, hash_id, '2000-01-01T00:00:00+00:00', 1, v_hits_num, 0.0, 0.0, 0.0, hits_time, v_hits_num)
                num_insert += 1
        line_num += 1
        #if(line_num > 55):
        #    break
    hits_file.close()        
    print 'add_hits_num line_num=%d, num_insert=%d, num_update=%d' % (line_num, num_insert, num_update)            
    return (True, num_insert, num_update)


def do_cold(platform, record):
    num_calc = 0
    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    hits_time = time.strftime("%Y-%m-%dT00:00:00+00:00", now_time)   
    
    hash_list_local = get_task_local(platform)  
            
    #hash_list_cold = hash_list_local.filter(last_hit_time__lte = hits_time)  
    hash_list_cold = hash_list_local
    print 'hash_list_cold count %d' % (hash_list_cold.count())
    for task in hash_list_cold:
        task.cold1 = day_diff(str(task.last_hit_time), hits_time)
        print '%d: %s cold1: %f' % (num_calc, task.hash, task.cold1)
        task.save()
        num_calc += 1            
        
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_calc: %d, ' % (num_calc)
    print output
    record.end_time = end_time
    record.status = 2                
    record.memo = output
    record.save()
    return True
    
    
            
def do_upload(platform, record):
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    hits_date = record.name
    (result, num_insert, num_update) = upload_add_hits_num(platform, hits_date)
    if(result == False):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'error@add_hits_num %s' % (hits_date)            
        print output            
        record.end_time = end_time
        record.status = 2
        record.memo = output
        record.save()
        return False
                 
    #last = datetime.date(datetime.date.today().year,datetime.date.today().month,1)-datetime.timedelta(1)
    #print last
    day_delta = HITS_FILE.hot_period
    num_year = string.atoi(hits_date[0:4])
    num_mon = string.atoi(hits_date[4:6])
    num_day = string.atoi(hits_date[6:8])
    previous_date = datetime.date(num_year, num_mon, num_day) - datetime.timedelta(days=day_delta)
    previous_day = '%04d%02d%02d' % (previous_date.year, previous_date.month, previous_date.day)
        
    (result, num_insert2, num_update2) = upload_sub_hits_num(platform, previous_day)
    if(result == False):
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'error@sub_hits_num %s' % (previous_day)            
        print output            
        record.end_time = end_time
        record.status = 2
        record.memo = output
        record.save()
        return False
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    print 'end@ %s' % (end_time)
    output = 'now: %s, ' % (end_time)
    output += 'num_insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    output += 'num_insert2: %d, ' % (num_insert2)
    output += 'num_update2: %d, ' % (num_update2)
    print output
    record.end_time = end_time
    record.status = 2 
    record.memo = output
    record.save()
        
        
def do_sync(platform, record):    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    print 'begin@%s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    begin_date = ''
    end_date = ''
    
    date_range = record.memo
    if(len(date_range) > 0):
        parts = date_range.split('&')
        date1 = parts[0]
        date2 = parts[1]   
        sub_parts = date1.split('=')
        begin_date = sub_parts[1]        
        sub_parts = date2.split('=')
        end_date = sub_parts[1]
    
    hash_list_macross = get_task_macross(platform, begin_date, end_date)
    num_macross = hash_list_macross.__len__()
    print 'num_macross=%d' % (num_macross)
    
    hash_list_local = get_task_local(platform)
    num_local = hash_list_local.count()
    print 'num_local=%d' % (num_local)
    
    num_insert = 0
    num_update = 0
    num_delete = 0
    
    #for hash_local in hash_list_local:
    #    hash_local.is_valid = 0
    
    for hash_macross in hash_list_macross:        
        create_time = '%s+00:00' % (hash_macross['online_time'])
        print '%s, %s' % (hash_macross['hash'], create_time)
        #hash_local = task_list_find(hash_list_local, hash_macross['hash'])
        hash_list = hash_list_local.filter(hash=hash_macross['hash'])
        if(len(hash_list) <= 0):
            print 'insert'
            task_insert(platform, hash_macross['hash'], create_time, 1, 0, 0.0, 0.0, 0.0, create_time, 0)                
            num_insert += 1
        else:                
            if(str(hash_list[0].online_time) != create_time):
                print 'update, online_time %s != %s' % (str(hash_list[0].online_time), create_time)
                hash_list[0].online_time = create_time
                hash_list[0].save()   
            else:
                print 'update, do nothing'         
            num_update += 1
                
    #for hash_local in hash_list_local:
    #    if(hash_local.is_valid == 0):
    #        hash_local.delete()
    #        num_delete += 1  
    
    now_time = time.localtime(time.time())        
    end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    output = 'now: %s, ' % (end_time)
    output += 'macross: %d, ' % (num_macross)
    output += 'local: %d, ' % (num_local)
    output += 'insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    output += 'num_delete: %d' % (num_delete)
    print output
    record.end_time = end_time
    record.status = 2
    record.memo = output
    record.save()
    return True

    
class Thread_UPLOAD(threading.Thread):
    platform = ''
    record_list = []
    num_insert = 0
    num_update = 0
    num_insert2 = 0
    num_update2 = 0
    
    def __init__(self, v_platform, v_record_list):
        super(Thread_UPLOAD, self).__init__()        
        self.platform = v_platform
        self.record_list = v_record_list        
    
    def add_hits_num(self, hits_date):
        upload_file = ""
        if(self.platform == 'mobile'):
            #upload_file = "/home/xiongming/data_analysis/topdata/mo/logdata/logdata_%s_hashid_sort.result" % (hits_date)
            upload_file = HITS_FILE.template_mobile % (hits_date)
        elif(self.platform == 'pc'):
            upload_file = HITS_FILE.template_mobile % (hits_date)
        print 'add_hits_num %s' % (upload_file)
       
        hits_time = '%s-%s-%sT12:00:00+00:00' % (hits_date[0:4], hits_date[4:6], hits_date[6:8])  
        
        line_num = 0
        try:
            hits_file = open(upload_file, "r")
        except:            
            return False
        
        hash_list_local = get_task_local(self.platform)
                    
        content = hits_file.readlines()
        for line in content:
            items = line.split(' ')
            if(len(items) >= 2):
                hits_num = items[0].strip()
                hash_id = items[1].strip()
                print '%s, %s' % (hits_num, hash_id)
                task_list = hash_list_local.filter(hash=hash_id)
                if(len(task_list) > 0):
                    #print 'update %s' % (hash_id)
                    hash_local = task_list[0]
                    hash_local.hot += string.atoi(hits_num)
                    hash_local.last_hit_time = hits_time
                    hash_local.cold1 = 0.0
                    hash_local.total_hits_num += string.atoi(hits_num)
                    hash_local.save()
                    self.num_update += 1
                else:
                    print 'insert %s' % (hash_id) 
                    v_hits_num = string.atoi(hits_num)
                    task_insert(self.platform, hash_id, '2000-01-01T00:00:00+00:00', 1, v_hits_num, 0.0, 0.0, 0.0, hits_time, v_hits_num)
                    self.num_insert += 1
            line_num += 1
            #if(line_num > 55):
            #    break
        hits_file.close()        
        print 'add_hits_num line_num=%d' % (line_num)
            
        return True
    
    
    def sub_hits_num(self, previous_day):
        # check if uploaded
        #     true: sub it,
        #     false: do nothing.
        operation_list = operation.views.get_operation_by_type_name(self.platform, 'upload_hits_num', previous_day)
        if(len(operation_list) <= 0):
            print 'sub_hits_num %s not uploaded' % (previous_day)
            return True;
        
        upload_file = ""
        if(self.platform == 'mobile'):
            upload_file = HITS_FILE.template_mobile % (previous_day)
        elif(self.platform == 'pc'):
            upload_file = HITS_FILE.template_pc % (previous_day)
        print 'sub_hits_num %s' % (upload_file)
       
        line_num = 0
        try:
            hits_file = open(upload_file, "r")
        except:            
            return False
        
        hash_list_local = get_task_local(self.platform)  
        
        content = hits_file.readlines()
        for line in content:
            items = line.split(' ')
            if(len(items) >= 2):
                hits_num = items[0].strip()
                hash_id = items[1].strip()
                print '%s, %s' % (hits_num, hash_id)
                task_list = hash_list_local.filter(hash=hash_id)
                if(len(task_list) > 0):
                    print 'update -' 
                    hash_local = task_list[0]
                    if(hash_local.hot > string.atoi(hits_num)): 
                        hash_local.hot -= string.atoi(hits_num)
                    else:
                        hash_local.hot = 0                    
                    hash_local.save()
                    self.num_update2 += 1
                else:
                    print 'insert -' 
                    self.num_insert2 += 1
            line_num += 1
            #if(line_num > 55):
            #    break
        hits_file.close()
        print 'sub_hits_num line_num=%d' % (line_num)
        
        return True
    
    def run_record(self, record):
        result = do_upload(self.platform, record)
        return result
        # below will be deleted.
        
        now_time = time.localtime(time.time())        
        begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        print 'begin@ %s' % (begin_time)
        record.begin_time = begin_time
        record.status = 1
        record.save()
    
        hits_date = record.name
        result = self.add_hits_num(hits_date)
        #result = True
        if(result == False):
            now_time = time.localtime(time.time())        
            end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
            output = 'now: %s, ' % (end_time)
            output += 'error@add_hits_num %s' % (hits_date)            
            print output            
            record.end_time = end_time
            record.status = 2
            record.memo = output
            record.save()
            return False
                 
        #last = datetime.date(datetime.date.today().year,datetime.date.today().month,1)-datetime.timedelta(1)
        #print last
        day_delta = HITS_FILE.hot_period
        num_year = string.atoi(hits_date[0:4])
        num_mon = string.atoi(hits_date[4:6])
        num_day = string.atoi(hits_date[6:8])
        previous_date = datetime.date(num_year, num_mon, num_day) - datetime.timedelta(days=day_delta)
        previous_day = '%04d%02d%02d' % (previous_date.year, previous_date.month, previous_date.day)
        
        result = self.sub_hits_num(previous_day)
        if(result == False):
            now_time = time.localtime(time.time())        
            end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
            output = 'now: %s, ' % (end_time)
            output += 'error@sub_hits_num %s' % (previous_day)            
            print output            
            record.end_time = end_time
            record.status = 2
            record.memo = output
            record.save()
            return False
    
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        print 'end@ %s' % (end_time)
        output = 'now: %s, ' % (end_time)
        output += 'num_insert: %d, ' % (self.num_insert)
        output += 'num_update: %d, ' % (self.num_update)
        output += 'num_insert2: %d, ' % (self.num_insert2)
        output += 'num_update2: %d, ' % (self.num_update2)
        print output
        record.end_time = end_time
        record.status = 2 
        record.memo = output
        record.save()
        
        
    def run(self):
        for record in self.record_list:            
            self.run_record(record)
                

class Thread_COLD(threading.Thread):
    platform = ''
    record = None
    num_calc = 0
    
    def __init__(self, the_platform, the_record):
        super(Thread_COLD, self).__init__()        
        self.platform = the_platform
        self.record = the_record        
            
    def run(self):
        result = do_cold(self.platform, self.record)
        return result
        # below will be deleted.
        
        now_time = time.localtime(time.time())        
        begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        print 'begin@ %s' % (begin_time)
        self.record.begin_time = begin_time
        self.record.status = 1
        self.record.save()
    
        hits_time = time.strftime("%Y-%m-%dT00:00:00+00:00", now_time)    
        
        hash_list_local = get_task_local(self.platform)  
            
        #hash_list_cold = hash_list_local.filter(last_hit_time__lte = hits_time)  
        hash_list_cold = hash_list_local
        print 'hash_list_cold count %d' % (hash_list_cold.count())
        for task in hash_list_cold:
            task.cold1 = day_diff(str(task.last_hit_time), hits_time)
            print '%d: %s cold1: %f' % (self.num_calc, task.hash, task.cold1)
            task.save()
            self.num_calc += 1            
        
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        print 'end@ %s' % (end_time)
        output = 'now: %s, ' % (end_time)
        output += 'num_calc: %d, ' % (self.num_calc)
        print output
        self.record.end_time = end_time
        self.record.status = 2                
        self.record.memo = output
        self.record.save()


class Thread_SYNC(threading.Thread):
    platform = ''
    record = None
    
    def __init__(self, the_platform, the_record):
        super(Thread_SYNC, self).__init__()        
        self.platform = the_platform
        self.record = the_record        
        
    def run(self):
        result = do_sync(self.platform, self.record)
        return result
        # below will be deleted.
    
        '''
        now_time = time.localtime(time.time())        
        begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        print 'begin@%s' % (begin_time)
        self.record.begin_time = begin_time
        self.record.status = 1
        self.record.save()
    
        hash_list_macross = get_task_macross(self.platform)
        hash_list_local = get_task_local(self.platform)
    
        num_macross = hash_list_macross.__len__()
        num_local = hash_list_local.count()
    
        num_insert = 0
        num_update = 0
        num_delete = 0
    
        #for hash_local in hash_list_local:
        #    hash_local.is_valid = 0
    
        for hash_macross in hash_list_macross:
            hash_local = task_list_find(hash_list_local, hash_macross['hash'])
            create_time = '%s+00:00' % (hash_macross['online_time'])
            print '%s, %s' % (hash_macross['hash'], create_time)
            if(hash_local == None):
                print 'insert'
                task_insert(self.platform, hash_macross['hash'], create_time, 1, 0, 0.0, 0.0, 0.0, create_time, 0)                
                num_insert += 1
            else:                
                if(hash_local.online_time != create_time):
                    print 'update, online_time'
                    hash_local.online_time = create_time
                    hash_local.save()   
                else:
                    print 'update, do nothing'         
                num_update += 1
                
        #for hash_local in hash_list_local:
        #    if(hash_local.is_valid == 0):
        #        hash_local.delete()
        #        num_delete += 1  
    
        now_time = time.localtime(time.time())        
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
        output = 'now: %s, ' % (end_time)
        output += 'macross: %d, ' % (num_macross)
        output += 'local: %d, ' % (num_local)
        output += 'insert: %d, ' % (num_insert)
        output += 'num_update: %d, ' % (num_update)
        output += 'num_delete: %d' % (num_delete)
        print output
        self.record.end_time = end_time
        self.record.status = 2
        self.record.memo = output
        self.record.save()
        return True
        '''
        

def add_record_sync_hash_db(platform, record_list, operation1):
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False
       
            
def sync_hash_db(request, platform):
    print 'sync_hash_db'  
    print request.REQUEST
    #{u'start_now': u'on', u'begin_date': u'20130922', u'end_date': u'20130923'}
    #{u'begin_date': u'', u'end_date': u''}
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
       
    operation = {}
    operation['type'] = 'sync_hash_db'
    operation['name'] = today
    operation['user'] = request.user.username
    operation['dispatch_time'] = dispatch_time
    operation['memo'] = ('begin_date=%s&end_date=%s' % (request.REQUEST['begin_date'], request.REQUEST['end_date']))
    
    return_datas = {}
    
    record_list = []
    result = add_record_sync_hash_db(platform, record_list, operation)
    if(result == False):
        return_datas['success'] = False
        return_datas['data'] = 'sync_hash_db operation add error, maybe exist.'
        return HttpResponse(json.dumps(return_datas))
    
    if(start_now == True):
        # start thread.
        t = Thread_SYNC(platform, record_list[0])            
        t.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'sync_hash_db operation add success'
    return HttpResponse(json.dumps(return_datas)) 

  

def add_record_upload_hits_num(platform, record_list, operation1):
    records = operation.views.get_operation_by_type_name(platform, operation1['type'], operation1['name'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False    
    
    

def upload_hits_num(request, platform):
    print 'upload_hits_num'  
    print request.REQUEST
    #{u'start_now': u'on', u'begin_date': u'20130922', u'end_date': u'20130923'}
    #{u'begin_date': u'', u'end_date': u''}
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    begin_date = request.REQUEST['begin_date']
    print begin_date    
    
    end_date = request.REQUEST['end_date']
    print end_date
        
    now_time = time.localtime(time.time())
    #today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    begin_day = None
    return_datas = {}
    if(len(begin_date) >= 8):
        begin_day = datetime.date(string.atoi(begin_date[0:4]), string.atoi(begin_date[4:6]), string.atoi(begin_date[6:8])) 
    else:
        return_datas['success'] = False
        return_datas['data'] = 'begin_date %s error' % (begin_date)  
        return HttpResponse(json.dumps(return_datas))
    
    end_day = begin_day      
    if(len(end_date) >= 8):
        end_day = datetime.date(string.atoi(end_date[0:4]), string.atoi(end_date[4:6]), string.atoi(end_date[6:8])) 
       
    record_list = []
    
    operation = {}
    operation['type'] = 'upload_hits_num'
    operation['name'] = ''
    operation['user'] = request.user.username
    operation['dispatch_time'] = dispatch_time
    operation['memo'] = ''
    
    day_num = 0
    operation['name'] = '%04d%02d%02d' % (begin_day.year, begin_day.month, begin_day.day)
    result = add_record_upload_hits_num(platform, record_list, operation)
    day_num += 1    
    while(True):
        d1 = begin_day
        delta = datetime.timedelta(days=day_num)
        d2 = d1 + delta
        if(d2 >= end_day):
            break
        else:
            operation['name'] = '%04d%02d%02d' % (d2.year, d2.month, d2.day)
            result = add_record_upload_hits_num(platform, record_list, operation)
            if(result == False):
                return_datas['success'] = False
                return_datas['data'] = 'date %s error' % (begin_date)  
                return HttpResponse(json.dumps(return_datas))
        day_num += 1 
            
    if(start_now == True):
        # start thread.
        t = Thread_UPLOAD(platform, record_list)            
        t.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'day_num %d' % (day_num)  
    return HttpResponse(json.dumps(return_datas))
        
        
def add_record_calc_cold(platform, record_list, operation1):
    records = operation.views.get_operation_undone_by_type(platform, operation1['type'])
    if(len(records) == 0):
        record = operation.views.create_operation_record_by_dict(platform, operation1)
        if(record != None):
            record_list.append(record)
        else:
            return False
    else:
        return False
    
    
def calc_cold(request, platform):
    print 'calc_cold'
    print request.REQUEST
    #{u'start_now': u'on', u'begin_date': u'20130922', u'end_date': u'20130923'}
    #{u'begin_date': u'', u'end_date': u''}
    start_now = False
    if 'start_now' in request.REQUEST:
        if(request.REQUEST['start_now'] == 'on'):
            start_now = True
    
    now_time = time.localtime(time.time())
    today = time.strftime("%Y-%m-%d", now_time)
    dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    
    operation = {}
    operation['type'] = 'calc_cold'
    operation['name'] = today
    operation['user'] = request.user.username
    operation['dispatch_time'] = dispatch_time
    operation['memo'] = ''
    
    return_datas = {}
    
    record_list = []
    result = add_record_calc_cold(platform, record_list, operation)
    if(result == False):
        return_datas['success'] = False
        return_datas['data'] = 'calc_cold operation add error, maybe exist.'
        return HttpResponse(json.dumps(return_datas))
    
    if(start_now == True):
        # start thread.
        t = Thread_COLD(platform, record_list[0])            
        t.start()
        
    return_datas['success'] = True
    return_datas['data'] = 'calc_cold operation add success'
    return HttpResponse(json.dumps(return_datas)) 

