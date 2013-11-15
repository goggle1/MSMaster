#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import string
import time
import sys
import DB.db
#from DB.db import DB_MYSQL
#from DB.db import DB_CONFIG
#from DB.db import *
import operation.views
import threading
import datetime

def day_diff(date1, date2):
    d1 = datetime.datetime(string.atoi(date1[0:4]), string.atoi(date1[5:7]), string.atoi(date1[8:10]))
    d2 = datetime.datetime(string.atoi(date2[0:4]), string.atoi(date2[5:7]), string.atoi(date2[8:10]))
    return (d1-d2).days


def task_insert(platform, hash_id, v_filesize, v_online_time, v_is_valid, v_hot, v_cold1, v_cold2, v_cold3, v_last_hit_time, v_total_hits_num):
    if(platform == 'mobile'):
        hash_local = models.mobile_task(hash      = hash_id,                   \
                                        filesize = v_filesize,                 \
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
                                       filesize = v_filesize,                 \
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
        
    

def get_tasks_local(platform):
    task_list = None
    if(platform == 'mobile'):
        task_list = models.mobile_task.objects.all()
    elif(platform == 'pc'):
        task_list = models.pc_task.objects.all()    
    return task_list


def get_tasks_by_hash(platform, hash_id):
    task_list = None
    if(platform == 'mobile'):
        task_list = models.mobile_task.objects.filter(hash=hash_id)
    elif(platform == 'pc'):
        task_list = models.pc_task.objects.filter(hash=hash_id)  
    return task_list
        

def get_task_list(request, platform):
    print 'get_task_list'
    print request.REQUEST
            
    start = request.REQUEST['start']
    limit = request.REQUEST['limit']    
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    print '%d,%d' % (start_index, limit_num)
    
    kwargs = {}
    
    hash_id = ''
    if(request.REQUEST.has_key('hash') == True):
        hash_id = request.REQUEST['hash']
    if(hash_id != ''):
        kwargs['hash'] = hash_id
    
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
    
    tasks = get_tasks_local(platform)
    tasks1 = tasks.filter(**kwargs)
    tasks2 = None
    
    if(len(order_condition) > 0):
        tasks2 = tasks1.order_by(order_condition)[start_index:start_index+limit_num]     
    else:        
        tasks2 = tasks1[start_index:start_index+limit_num]
            
    return_datas = {'success':True, 'data':[]}    
    return_datas['total_count'] = tasks1.count()
    
    for task in tasks2:        
        return_datas['data'].append(task.todict())
        
    return HttpResponse(json.dumps(return_datas))


def down_hot_tasks(request, platform):
    print 'down_hot_tasks'
    print request.REQUEST    
    task_num = request.REQUEST['task_num']
    
    tasks = get_tasks_local(platform) 
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
        
    tasks = get_tasks_local(platform)  
    #tasks2 = tasks.order_by('cold1,cold2,cold3')
    tasks2 = tasks.order_by('cold1', 'hot')[0:task_num]
       
    output = ''
    for task in tasks2:
        output += '%s,%s,%s,%s,%s\n' % (task.hash, task.online_time, task.cold1, task.cold2, task.cold3)
    
    response = HttpResponse(output, content_type='text/comma-separated-values')
    response['Content-Disposition'] = 'attachment; filename=cold_tasks_%s_%s.csv' % (platform, task_num)
    return response


def get_tasks_macross_mobile(begin_date, end_date):
    task_list = []
    sql = ""
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    where_condition = ''
    if(len(begin_date) > 0):
        begin_time = '%s-%s-%s 00:00:00' % (begin_date[0:4], begin_date[4:6], begin_date[6:8])
        where_condition += " and create_time >= '%s'" % (begin_time)
    if(len(end_date) > 0):
        end_time = '%s-%s-%s 00:00:00' % (end_date[0:4], end_date[4:6], end_date[6:8])
        where_condition += " and create_time < '%s'" % (end_time)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
    
    #sql = "select dat_hash, create_time from fs_mobile_dat where state!='dismissed' " + where_condition
    sql = "select dat_hash, create_time, filesize from fs_mobile_dat where state!='dismissed' " + where_condition           
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r
            elif(col_num == 2):
                task1['filesize'] = r
            col_num += 1
        task_list.append(task1)
    print 'task_list num: %d' % (len(task_list))
    
    sql = "select video_hash, create_time, filesize from fs_video_dat where state!='dismissed' " + where_condition           
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r
            elif(col_num == 2):
                task1['filesize'] = r
            col_num += 1
        task_list.append(task1)
    print 'task_list num: %d' % (len(task_list))
    
    db.close()  
     
    return task_list


def get_tasks_macross_pc(begin_date, end_date):
    task_list = []
    sql = ""
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    where_condition = ''
    if(len(begin_date) > 0):
        begin_time = '%s-%s-%s 00:00:00' % (begin_date[0:4], begin_date[4:6], begin_date[6:8])
        where_condition += " and fs_task.create_time >= '%s'" % (begin_time)
    if(len(end_date) > 0):
        end_time = '%s-%s-%s 00:00:00' % (end_date[0:4], end_date[4:6], end_date[6:8])
        where_condition += " and fs_task.create_time < '%s'" % (end_time)
    
    db = DB.db.DB_MYSQL()
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
    
    #where_condition = " and fs_task.task_hash='92A20D164F8D5F18F2433E9CB39703E2A381EDDC'"
    #sql = "select task_hash, create_time from fs_task where state!='dismissed' " + where_condition
    #sql = "select t.task_hash, t.create_time, d.file_size from fs_task t, fs_dat_file d where t.task_hash=d.hashid and t.state!='dismissed' " + where_condition
    sql = "select fs_task.task_hash, fs_task.create_time, fs_dat_file.file_size from fs_task LEFT JOIN fs_dat_file ON fs_task.task_hash=fs_dat_file.hashid where fs_task.state!='dismissed'" + where_condition              
    print sql
    db.execute(sql)
    
    for row in db.cur.fetchall():
        task1 = {}      
        col_num = 0  
        for r in row:
            if(col_num == 0):
                task1['hash'] = r
            elif(col_num == 1):
                task1['online_time'] = r
            elif(col_num == 2):
                task1['filesize'] = r
            col_num += 1
        task_list.append(task1)
    
    db.close()  
     
    return task_list



def get_tasks_macross(platform, begin_date, end_date):
    task_list = None
    if(platform == 'mobile'):
        task_list = get_tasks_macross_mobile(begin_date, end_date)
    elif(platform == 'pc'):        
        task_list = get_tasks_macross_pc(begin_date, end_date)
        
    return task_list



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
    
    db = DB.db.DB_MYSQL()
    #db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
    db.connect(DB.db.DB_CONFIG.host, DB.db.DB_CONFIG.port, DB.db.DB_CONFIG.user, DB.db.DB_CONFIG.password, DB.db.DB_CONFIG.db)
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
        upload_file = DB.db.HITS_FILE.template_mobile % (previous_day)
    elif(platform == 'pc'):
        upload_file = DB.db.HITS_FILE.template_pc % (previous_day)
    print 'sub_hits_num %s' % (upload_file)
       
    line_num = 0
    try:
        hits_file = open(upload_file, "r")
    except:            
        return (False, num_insert2, num_update2)
        
    hash_list_local = get_tasks_local(platform)  
        
    content = hits_file.readlines()
    for line in content:
        items = line.split(' ')
        if(len(items) >= 2):
            hits_num = items[0].strip()
            hash_id = items[1].strip()
            #print '%s, %s' % (hits_num, hash_id)
            task_list = hash_list_local.filter(hash=hash_id)
            if(len(task_list) > 0):
                #print '%s, %s [update -]' % (hits_num, hash_id)
                hash_local = task_list[0]
                if(hash_local.hot > string.atoi(hits_num)): 
                    hash_local.hot -= string.atoi(hits_num)
                else:
                    hash_local.hot = 0                    
                hash_local.save()
                num_update2 += 1
            else:
                print '%s, %s [insert -]' % (hits_num, hash_id)
                num_insert2 += 1
        line_num += 1
        if(line_num % 100 == 0):
            print 'file=%s, line_num=%d' % (upload_file, line_num)
    hits_file.close()
    print 'sub_hits_num line_num=%d, num_insert2=%d, num_update2=%d' % (line_num, num_insert2, num_update2)        
    return (True, num_insert2, num_update2)
    
    
def upload_add_hits_num(platform, hits_date):
    num_insert = 0
    num_update = 0
    
    upload_file = ""
    if(platform == 'mobile'):        
        upload_file = DB.db.HITS_FILE.template_mobile % (hits_date)
    elif(platform == 'pc'):
        upload_file = DB.db.HITS_FILE.template_pc % (hits_date)
    print 'add_hits_num %s' % (upload_file)
       
    hits_time = '%s-%s-%s 12:00:00+00:00' % (hits_date[0:4], hits_date[4:6], hits_date[6:8])  
    
    try:
        hits_file = open(upload_file, "r")
    except:            
        return (False, num_insert, num_update)
        
    hash_list_local = get_tasks_local(platform)
    
    line_num = 0 
    while(True): 
        line = ''        
        try:      
            line = hits_file.readline()
        except:            
            break 
        if(line == ''):
            break           
        items = line.split(' ')
        if(len(items) >= 2):
            hits_num = items[0].strip()
            hash_id = items[1].strip()
            #print '%s, %s' % (hits_num, hash_id)
            task_list = hash_list_local.filter(hash=hash_id)
            if(task_list.count() > 0):
                #print '%s, %s [update +]' % (hits_num, hash_id)
                hash_local = task_list[0]
                # if last_hit_time is equal to hits_time, it's updated, then do nothing
                #print '%s ? %s' % (str(hash_local.last_hit_time), hits_time)
                if(str(hash_local.last_hit_time) != hits_time):
                    hash_local.hot += string.atoi(hits_num)
                    # if last_hit_time < hits_time, update last_hit_time
                    compare_r = cmp(str(hash_local.last_hit_time), hits_time)
                    #print 'cmp %s ? %s return %d' % (str(hash_local.last_hit_time), hits_time, compare_r)
                    if(hash_local.last_hit_time == None) or (compare_r < 0):
                        hash_local.last_hit_time = hits_time
                        hash_local.cold1 = 0.0
                    hash_local.total_hits_num += string.atoi(hits_num)
                    hash_local.save()
                num_update += 1
            else:
                print '%s, %s [insert +]' % (hits_num, hash_id)
                v_hits_num = string.atoi(hits_num)
                #task_insert(platform, hash_id, '2000-01-01T00:00:00+00:00', 1, v_hits_num, 0.0, 0.0, 0.0, hits_time, v_hits_num)
                task_insert(platform, hash_id, 0, hits_time, 1, v_hits_num, 0.0, 0.0, 0.0, hits_time, v_hits_num)
                num_insert += 1
        line_num += 1
        if(line_num % 100 == 0):
            print 'file=%s, line_num=%d' % (upload_file, line_num)
        
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
    
    hash_list_local = get_tasks_local(platform)  
            
    #hash_list_cold = hash_list_local.filter(last_hit_time__lte = hits_time)  
    hash_list_cold = hash_list_local
    print 'hash_list_cold count %d' % (hash_list_cold.count())
    for task in hash_list_cold:
        last_hit_time = task.last_hit_time
        if(last_hit_time == None) or (last_hit_time == ''):
            last_hit_time = task.online_time
        task.cold1 = day_diff(str(last_hit_time), hits_time)
        print '%d: %s cold1: %f' % (num_calc, task.hash, task.cold1)
        task.save()
        num_calc += 1 
        #if(num_calc >= 55):
        #    break           
        
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
   
  
def db_calc_cold(platform):    
    sql = ""
    
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    
    db = DB.db.DB_MYSQL()
    #db.connect("192.168.160.203", 3306, "admin", "123456", "mediaserver")
    db.connect(DB.db.MS_DB_CONFIG.host, DB.db.MS_DB_CONFIG.port, DB.db.MS_DB_CONFIG.user, DB.db.MS_DB_CONFIG.password, DB.db.MS_DB_CONFIG.db)
    if(platform == 'mobile'):
        sql = "update mobile_task set cold1=TIMESTAMPDIFF(DAY, NOW(), last_hit_time) where last_hit_time is not null"
        db.execute(sql)
        sql = "update mobile_task set cold1=TIMESTAMPDIFF(DAY, NOW(), online_time) where last_hit_time is null and online_time is not null"
        db.execute(sql)
    elif(platform == 'pc'):
        sql = "update pc_task set cold1=TIMESTAMPDIFF(DAY, NOW(), last_hit_time) where last_hit_time is not null"
        db.execute(sql)
        sql = "update pc_task set cold1=TIMESTAMPDIFF(DAY, NOW(), online_time) where last_hit_time is null and online_time is not null"
        db.execute(sql)
    db.close() 
    return

  
def do_cold2(platform, record):
    num_calc = 0
    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    print 'begin@ %s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
         
    db_calc_cold(platform)
        
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
    day_delta = DB.db.HITS_FILE.hot_period
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
        
        
def do_sync_all(platform, record):    
    now_time = time.localtime(time.time())        
    begin_time = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", now_time)
    print 'begin@%s' % (begin_time)
    record.begin_time = begin_time
    record.status = 1
    record.save()
    
    begin_date = ''
    end_date = ''
        
    hash_list_macross = get_tasks_macross(platform, begin_date, end_date)
    num_macross = hash_list_macross.__len__()
    print 'num_macross=%d' % (num_macross)
    
    hash_list_local = get_tasks_local(platform)
    num_local = hash_list_local.count()
    print 'num_local=%d' % (num_local)
    
    num_insert = 0
    num_update = 0
    num_delete = 0
    
    #if(len(date_range) <= 0):
    #    for hash_local in hash_list_local:
    #        hash_local.is_valid = 0
    
    for hash_macross in hash_list_macross:        
        create_time = '%s+00:00' % (hash_macross['online_time'])        
        filesize = hash_macross['filesize']
        print '%s, %s' % (hash_macross['hash'], create_time)
        #hash_local = task_list_find(hash_list_local, hash_macross['hash'])
        hash_list = hash_list_local.filter(hash=hash_macross['hash'])
        #print 'insert before %d' % (len(hash_list)) 
        if(len(hash_list) <= 0):
            print 'insert'
            task_insert(platform, hash_macross['hash'], filesize, create_time, 2, 0, 0.0, 0.0, 0.0, create_time, 0)   
            #hash_list2 = hash_list_local.filter(hash=hash_macross['hash'])
            #print 'insert after %d' % (len(hash_list2))            
            num_insert += 1    
        else:      
            print 'update'          
            #if(str(hash_list[0].online_time) != create_time):
            #    print 'update, online_time %s != %s' % (str(hash_list[0].online_time), create_time)
            #    hash_list[0].online_time = create_time
            #    hash_list[0].save()   
            #else:
            #    print 'update, do nothing'  
            hash_list[0].online_time = create_time
            hash_list[0].filesize = filesize
            hash_list[0].is_valid = 2
            hash_list[0].save()       
            num_update += 1
               
    #for hash_local in hash_list_local:
    #    if(hash_local.is_valid == 0):
    #        hash_local.delete()
    #        num_delete += 1 
    hash_list_delete = hash_list_local.filter(is_valid=1)
    num_delete = hash_list_delete.count()
    hash_list_delete.delete()  
    
    get_tasks_local(platform).update(is_valid=1)
    
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
    
            
def do_sync_partial(platform, record):    
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
        parts = date_range.split('~')
        begin_date = parts[0] 
        end_date = parts[1]
    
    hash_list_macross = get_tasks_macross(platform, begin_date, end_date)
    num_macross = hash_list_macross.__len__()
    print 'num_macross=%d' % (num_macross)
    
    hash_list_local = get_tasks_local(platform)
    num_local = hash_list_local.count()
    print 'num_local=%d' % (num_local)
    
    num_insert = 0
    num_update = 0
    num_delete = 0
    
    for hash_macross in hash_list_macross:        
        create_time = '%s+00:00' % (hash_macross['online_time'])
        filesize = hash_macross['filesize']
        print '%s, %s' % (hash_macross['hash'], create_time)
        #hash_local = task_list_find(hash_list_local, hash_macross['hash'])
        hash_list = hash_list_local.filter(hash=hash_macross['hash'])
        #print 'insert before %d' % (len(hash_list)) 
        if(len(hash_list) <= 0):
            print 'insert'
            task_insert(platform, hash_macross['hash'], filesize, create_time, 1, 0, 0.0, 0.0, 0.0, create_time, 0)   
            #hash_list2 = hash_list_local.filter(hash=hash_macross['hash'])
            #print 'insert after %d' % (len(hash_list2))            
            num_insert += 1    
        else:      
            print 'update'          
            #if(str(hash_list[0].online_time) != create_time):
            #    print 'update, online_time %s != %s' % (str(hash_list[0].online_time), create_time)
            #    hash_list[0].online_time = create_time
            #    hash_list[0].save()   
            #else:
            #    print 'update, do nothing'  
            hash_list[0].online_time = create_time
            hash_list[0].filesize = filesize
            hash_list[0].is_valid = 1
            hash_list[0].save()       
            num_update += 1
    
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
    #platform = ''
    #record_list = []
    #num_insert = 0
    #num_update = 0
    #num_insert2 = 0
    #num_update2 = 0
    
    def __init__(self, v_platform, v_record_list):
        super(Thread_UPLOAD, self).__init__()        
        self.platform = v_platform
        self.record_list = v_record_list   
        self.num_insert = 0
        self.num_update = 0
        self.num_insert2 = 0
        self.num_update2 = 0     
        
      
    def run_record(self, record):
        result = do_upload(self.platform, record)
        return result
        
        
    def run(self):
        for record in self.record_list:            
            self.run_record(record)
                

class Thread_COLD(threading.Thread):
    #platform = ''
    #record = None
    #num_calc = 0
    
    def __init__(self, the_platform, the_record):
        super(Thread_COLD, self).__init__()        
        self.platform = the_platform
        self.record = the_record   
        self.num_calc = 0     
            
    def run(self):
        result = do_cold(self.platform, self.record)
        return result


class Thread_SYNC(threading.Thread):
    #platform = ''
    #record = None
    #sync_all = 0
    
    def __init__(self, the_platform, the_record):
        super(Thread_SYNC, self).__init__()        
        self.platform = the_platform
        self.record = the_record    
        if(self.record.memo == '~'):
            self.sync_all = 1
        else:
            self.sync_all = 0
        
    def run(self):
        result = False
        if(self.sync_all == 1):
            result = do_sync_all(self.platform, self.record)
        else:
            result = do_sync_partial(self.platform, self.record)
        return result        
        

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

    '''
    # temporary    
    import special
    file_name = '/home/xiongming/20131011.hashid.list'
    platform = 'pc'
    special.hot_tasks_to_rooms(platform, file_name)
    return_datas = {}
    return_datas['success'] = True
    return_datas['data'] = file_name
    return HttpResponse(json.dumps(return_datas)) 
    '''
    
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
    operation['memo'] = '%s~%s' % (request.REQUEST['begin_date'], request.REQUEST['end_date'])
    
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
    if(result == False):
        return_datas['success'] = False
        return_datas['data'] = 'date %s error' % (operation['name'])  
        return HttpResponse(json.dumps(return_datas))
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
                return_datas['data'] = 'date %s error' % (operation['name'])  
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

