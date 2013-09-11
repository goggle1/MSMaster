#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models
import string

def get_task_local(platform):
    ms_list = []
    if(platform == 'mobile'):
        ms_list = models.mobile_task.objects.all()
    elif(platform == 'pc'):
        ms_list = models.pc_task.objects.all()    
    return ms_list


def get_task_list(request, platform):
    tasks = get_task_local(platform)    
    
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
    
    tasks2 = tasks
    if(len(order_by) > 0):
        tasks2 = tasks.order_by(order_by)
    
    start_index = string.atoi(start)
    limit_num = string.atoi(limit)
    
    index = 0
    num = 0
    return_datas = {'success':True, 'data':[]}
    return_datas['total_count'] = len(tasks2)
    for task in tasks2:
        if(index >= start_index) and (num < limit_num):
            return_datas['data'].append(task.todict())
            num += 1
        index += 1
        
    return HttpResponse(json.dumps(return_datas))

def down_hot_tasks(request, platform):
    tasks = get_task_local(platform)    
    
    print request.REQUEST
    #print request.REQUEST['start']
    #print request.REQUEST['limit']
    #{u'sort': u'server_id', u'start': u'0', u'limit': u'20', u'dir': u'ASC'}
    #{u'sort': u'server_name', u'start': u'0', u'limit': u'20', u'dir': u'DESC'}
    task_num = request.REQUEST['task_num']
    
    tasks2 = tasks.order_by('-hits_num')
        
    index = 0
    num = 0
    output = ''
    for task in tasks2:
        if(index >= 0) and (num < task_num):
            output += '%s,%s,%s,%s\n' % (task.hash, task.create_time, task.hits_num, task.cold)
            num += 1
        index += 1
    
    response = HttpResponse(output, content_type='text/comma-separated-values')
    response['Content-Disposition'] = 'attachment; filename=hot_tasks_%s_%s.csv' % (platform, task_num)
    return response

def down_cold_tasks(request, platform):
    tasks = get_task_local(platform)    
    
    print request.REQUEST
    #print request.REQUEST['start']
    #print request.REQUEST['limit']
    #{u'sort': u'server_id', u'start': u'0', u'limit': u'20', u'dir': u'ASC'}
    #{u'sort': u'server_name', u'start': u'0', u'limit': u'20', u'dir': u'DESC'}
    task_num = request.REQUEST['task_num']
    
    tasks2 = tasks.order_by('cold')
        
    index = 0
    num = 0
    output = ''
    for task in tasks2:
        if(index >= 0) and (num < task_num):
            output += '%s,%s,%s,%s\n' % (task.hash, task.create_time, task.hits_num, task.cold)
            num += 1
        index += 1
    
    response = HttpResponse(output, content_type='text/comma-separated-values')
    response['Content-Disposition'] = 'attachment; filename=cold_tasks_%s_%s.csv' % (platform, task_num)
    return response