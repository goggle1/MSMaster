#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import string

def get_operation_record(platform, v_type, v_name):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type, name=v_name)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type, name=v_name)
    return records


def get_operation_record_undone(platform, v_type, v_name):
    records = []
    if(platform == 'mobile'):
        records = models.mobile_operation.objects.filter(type=v_type, name=v_name).exclude(status=models.STATUS_DONE)
    elif(platform == 'pc'):
        records = models.pc_operation.objects.filter(type=v_type, name=v_name).exclude(status=models.STATUS_DONE)
    return records


def create_operation_record(platform, v_type, v_name, v_dispatch_time, v_memo=''):
    record = None    
    if(platform == 'mobile'):
        record = models.mobile_operation(type=v_type, name=v_name, dispatch_time=v_dispatch_time, status=models.STATUS_DISPATCHED, memo=v_memo)
        record.save()
    elif(platform == 'pc'):
        record = models.pc_operation(type=v_type, name=v_name, dispatch_time=v_dispatch_time, status=models.STATUS_DISPATCHED, memo=v_memo)
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
            
    order_by = ''
    if(len(dire) > 0):
        if(dire == 'ASC'):
            order_by += ''
        elif(dire == 'DESC'):
            order_by += '-'
                
    if(len(sort) > 0):
        order_by += sort
    
    operations = get_operation_local(platform)
    operations2 = []
    if(len(order_by) > 0):
        operations2 = operations.order_by(order_by)[start_index:start_index+limit_num]
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
    for the_id in id_list:
        operation_list = models.mobile_operation.objects.filter(id=the_id)
        title = '<h1>id: %s</h1>' % (the_id)
        output += title  
        for operation in operation_list:
            output += '%s,%s,%s,%s,%s,%s,%s,%s<br>' \
            % (str(operation.id), str(operation.type), str(operation.name), str(operation.dispatch_time), \
               str(operation.status), str(operation.begin_time), str(operation.end_time), str(operation.memo))
        
        
    return HttpResponse(output)

    