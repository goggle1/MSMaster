#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import string
import threading
import time
#from task.views import do_sync
import task.views
import room.views


def get_operation_record(platform, v_type, v_name):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type, name=v_name)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type, name=v_name)
    return records


def get_operation_by_type_name(platform, v_type, v_name):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type, name=v_name)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type, name=v_name)
    return records



def get_operation_undone_by_type(platform, v_type):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type).exclude(status=models.STATUS_DONE)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type).exclude(status=models.STATUS_DONE)
    return records


def get_operation_record_undone(platform, v_type, v_name):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type, name=v_name).exclude(status=models.STATUS_DONE)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type, name=v_name).exclude(status=models.STATUS_DONE)
    return records


def create_operation_record(platform, v_type, v_name, v_user, v_dispatch_time, v_memo=''):
    record = None    
    if(platform == 'mobile'):
        record = models.mobile_operation(type=v_type, name=v_name, user=v_user, dispatch_time=v_dispatch_time, status=models.STATUS_DISPATCHED, memo=v_memo)
        record.save()
    elif(platform == 'pc'):
        record = models.pc_operation(type=v_type, name=v_name, user=v_user, dispatch_time=v_dispatch_time, status=models.STATUS_DISPATCHED, memo=v_memo)
        record.save()
    return record


def create_operation_record_by_dict(platform, operation):
    record = None    
    if(platform == 'mobile'):
        record = models.mobile_operation(type=operation['type'], name=operation['name'], user=operation['user'], dispatch_time=operation['dispatch_time'], status=models.STATUS_DISPATCHED, memo=operation['memo'])
        record.save()
    elif(platform == 'pc'):
        record = models.pc_operation(type=operation['type'], name=operation['name'], user=operation['user'], dispatch_time=operation['dispatch_time'], status=models.STATUS_DISPATCHED, memo=operation['memo'])
        record.save()
    return record



def get_operation_local(platform):
    operation_list = []
    if(platform == 'mobile'):
        operation_list = models.mobile_operation.objects.all()
    elif(platform == 'pc'):
        operation_list = models.pc_operation.objects.all()    
    return operation_list
       

def get_operation_list(request, platform):
    print 'get_operation_list'
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
    
    operations = get_operation_local(platform)
    operations2 = []
    if(len(order_condition) > 0):
        operations2 = operations.order_by(order_condition)[start_index:start_index+limit_num]
    else:
        operations2 = operations[start_index:start_index+limit_num]
    
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = operations.count()
    for operation in operations2:
        return_datas['data'].append(operation.todict())
        
    return HttpResponse(json.dumps(return_datas))


def show_operation_list(request, platform):  
    output = ''
    ids = request.REQUEST['ids']    
    id_list = ids.split(',')
    operations = get_operation_local(platform)
    
    for the_id in id_list:
        operation_list = operations.filter(id=the_id)
        title = '<h1>id: %s</h1>' % (the_id)
        output += title  
        for operation in operation_list:
            output += '%s,%s,%s,%s,%s,%s,%s,%s<br>' \
            % (str(operation.id), str(operation.type), str(operation.name), str(operation.dispatch_time), \
               str(operation.status), str(operation.begin_time), str(operation.end_time), str(operation.memo))        
        
    return HttpResponse(output)


g_thread = None

class Thread_JOBS(threading.Thread):
    #platform = ''
    #operation_list = []
    
    def __init__(self, v_platform, operation_list):
        super(Thread_JOBS, self).__init__()        
        self.platform = v_platform
        self.operation_list = operation_list
                
    
    def run_operation(self, operation):
        result = False
        if(operation.status == models.STATUS_DONE):
            return True
        if(operation.type == 'sync_hash_db'):
            result = task.views.do_sync(self.platform, operation)
        elif(operation.type == 'upload_hits_num'):
            result = task.views.do_upload(self.platform, operation)
        elif(operation.type == 'calc_cold'):
            result = task.views.do_cold(self.platform, operation)
        elif(operation.type == 'add_hot_tasks'):
            result = room.views.do_add_hot_tasks(self.platform, operation)
        else:
            print 'unknown operation type: %s' % (operation.type)
            
        return result
            
            
    def run(self):
        # sort 
        # 1. sync_hash_db
        # 2. upload_hits_num ...        
        # 3. calc_cold
        # todo:
        for operation in self.operation_list:
            self.run_operation(operation)  
        global g_thread      
        g_thread = None


def operation_type_int(v_type):
    # todo:
    # dict = { 'sync_hash_db':1, 'upload_hits_num':2, }
    result = 0
    if(v_type == 'sync_hash_db'):
        result = 1
    elif(v_type == 'upload_hits_num'):
        result = 2
    elif(v_type == 'calc_cold'):
        result = 3
    return result

            
def operation_cmp(op1, op2):
    type1 = operation_type_int(op1.type)
    type2 = operation_type_int(op2.type)
    
    if(type1 == type2):
        return cmp(op1.name, op2.name)
    else:
        if(type1<type2):
            return -1
        else:
            return 1
            

    
def do_selected_operations(request, platform):  
    output = ''
    operation_list = []
    operations = get_operation_local(platform)
    
    ids = request.REQUEST['ids']    
    id_list = ids.split(',')
    for the_id in id_list:
        op_list = operations.filter(id=the_id)
        operation_list.extend(op_list)
    
    print 'before:'
    for op in operation_list:
        print '%s %s' % (op.type, op.name)
    operation_list.sort(operation_cmp)
    print 'after:'
    for op in operation_list:
        print '%s %s' % (op.type, op.name)
    
    global g_thread
    if(g_thread == None):    
        g_thread = Thread_JOBS(platform, operation_list)            
        g_thread.start()
        output += 'do %s' % (ids)
    else:
        output += 'Thread_JOBS has started!'
             
        
    return HttpResponse(output)


def do_all_operations(request, platform):  
    output = ''
    operation_list = []
    operations = get_operation_local(platform)    
    #temp_list = operations.filter(status=models.STATUS_DISPATCHED)
    temp_list = operations.exclude(status=models.STATUS_DONE)
    operation_list.extend(temp_list)
    
    print 'before:'
    for op in operation_list:
        print '%s %s' % (op.type, op.name)
    operation_list.sort(operation_cmp)
    print 'after:'
    for op in operation_list:
        print '%s %s' % (op.type, op.name)
    
    global g_thread
    if(g_thread == None):
        g_thread = Thread_JOBS(platform, operation_list)            
        g_thread.start()    
        output += 'do '  
        for operation in operation_list:      
            output += '%s,' % (str(operation.id))
    else:
        output += 'Thread_JOBS has started!'
            
    return HttpResponse(output)    