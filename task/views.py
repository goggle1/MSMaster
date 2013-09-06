#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models

def get_task_list(request, platform):
    tasks = []
    if(platform == 'mobile'):
        tasks = models.mobile_task.objects.all()
    elif(platform == 'pc'):
        tasks = models.pc_task.objects.all()

    return_datas = {'success':True, 'data':[]}
    for task in tasks:
        return_datas['data'].append(task.todict())
    return HttpResponse(json.dumps(return_datas))
