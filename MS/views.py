#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models

def get_ms_list(request, platform):
    servers = []
    if(platform == 'mobile'):
        servers = models.mobile_ms_server.objects.all()
    elif(platform == 'pc'):
        servers = models.pc_ms_server.objects.all()

    return_datas = {'success':True, 'data':[]}
    for server in servers:
        return_datas['data'].append(server.todict())
    return HttpResponse(json.dumps(return_datas))
