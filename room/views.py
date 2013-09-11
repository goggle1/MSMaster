#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import sys
import re
import MySQLdb
import time
import string
#import MS.models
from MS.models import mobile_ms_server
from MS.models import pc_ms_server

def get_room_local(platform):
    rooms = []
    if(platform == 'mobile'):
        rooms = models.mobile_room.objects.all()
    elif(platform == 'pc'):
        rooms = models.pc_room.objects.all()

    return rooms

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
        
def get_room_macross(platform):
    room_list = []
    sql = ""
    
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    db = DB_MYSQL()
    db.connect("192.168.8.101", 3317, "public", "funshion", "macross")
    if(platform == "mobile"):
        sql = "select l.room_id, l.room_name, l.is_valid from fs_server s, fs_server_location l where s.ml_room_id=l.room_id and s.is_valid=1 and l.is_valid=1 group by l.room_id order by l.room_id"
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
    rooms = get_room_local(platform)    
    
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
    
    rooms2 = rooms
    if(len(order_by) > 0):
        rooms2 = rooms.order_by(order_by)
    
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    
    index = 0
    num = 0
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = len(rooms2)
    for room in rooms2:
        if(index >= start_index) and (num < limit_num):
            return_datas['data'].append(room.todict())
            num += 1
        index += 1
        
    return HttpResponse(json.dumps(return_datas))

def show_room_list(request, platform):  
    output = ''
    ids = request.REQUEST['ids']    
    id_list = ids.split(',')
    for id in id_list:                         
        ms_list = mobile_ms_server.objects.filter(room_id=id)
        title = '<h1>id: %s, ms_num: %d</h1>' % (id, len(ms_list))
        output += title        
        for ms in ms_list:
            output += '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s<br>' \
            % (str(ms.server_id), str(ms.server_name), str(ms.server_ip), str(ms.server_port), \
               str(ms.controll_ip), str(ms.controll_port), str(ms.task_number), str(ms.server_status1), \
               str(ms.server_status2), str(ms.server_status3), str(ms.server_status4), str(ms.check_time))
    return HttpResponse(output)

def room_list_find(room_list, room_id):
    for room in room_list:
        if(room.room_id == room_id):
            return room
    return None


def sync_room_db(request, platform):  
    room_list_macross = get_room_macross(platform)    
    room_list_local = get_room_local(platform)
    
    num_macross = len(room_list_macross)
    num_local = len(room_list_local)
    
    num_insert = 0
    num_update = 0
    num_delete = 0
    
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    
    for room_local in room_list_local:
        room_local.is_valid = 0
    
    for room_macross in room_list_macross:
        room_local = room_list_find(room_list_local, room_macross['room_id'])
        print room_macross['room_id'], room_macross['room_name'], room_macross['is_valid']
        if(room_local == None):
            if(platform == 'mobile'):
                room_local = models.mobile_room(room_id           = room_macross['room_id'],        \
                                           room_name          = room_macross['room_name'],      \
                                           is_valid           = room_macross['is_valid'],       \
                                           task_number        = 0,                              \
                                           room_status        = 0,                              \
                                           num_dispatching    = 0,                              \
                                           num_deleting       = 0,                              \
                                           operation_time     = now_time                        \
                                           )
            elif(platform == 'pc'):
                room_local = models.pc_room(room_id           = room_macross['room_id'],        \
                                           room_name          = room_macross['room_name'],      \
                                           is_valid           = room_macross['is_valid'],       \
                                           task_number        = 0,                              \
                                           room_status        = 0,                              \
                                           num_dispatching    = 0,                              \
                                           num_deleting       = 0,                              \
                                           operation_time     = now_time                        \
                                           )
            room_local.save()
            num_insert += 1
        else:
            room_local.room_id           = room_macross['room_id']
            room_local.room_name         = room_macross['room_name']
            room_local.is_valid          = room_macross['is_valid']
            room_local.operation_time    = now_time
            room_local.save()
            num_update += 1
                
    for room_local in room_list_local:
        if(room_local.is_valid == 0):
            room_local.delete()
            num_delete += 1  
    
    output = 'now: %s, ' % (now_time)
    output += 'macross: %d, ' % (num_macross)
    output += 'local: %d, ' % (num_local)
    output += 'insert: %d, ' % (num_insert)
    output += 'num_update: %d, ' % (num_update)
    output += 'num_delete: %d' % (num_delete)
        
    return HttpResponse(output)

def modify_room(request, platform):
    rooms = get_room_local(platform)    
        
    print request.REQUEST
    the_room_id = request.REQUEST['room_id']
    the_num_dispatching = request.REQUEST['num_dispatching']
    the_num_deleting = request.REQUEST['num_deleting']
    
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    rooms.filter(room_id=the_room_id).update(num_dispatching=the_num_dispatching, num_deleting=the_num_deleting, operation_time=now_time)
    
    #{"success":true,"data":"\u201cSDYD-25\u201d\u4fee\u6539\u6210\u529f","createTime":"2013-09-11 14:16:56"}
    return_datas = {'success':True, 'data': u'修改成功', "operationTime":"2013-09-11 14:16:56"}    
    return HttpResponse(json.dumps(return_datas))

    