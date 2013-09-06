#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json
import models

def get_room_list(request, platform):
    rooms = []
    if(platform == 'mobile'):
        rooms = models.mobile_room.objects.all()
    elif(platform == 'pc'):
        rooms = models.pc_room.objects.all()

    return_datas = {'success':True, 'data':[]}
    for room in rooms:
        return_datas['data'].append(room.todict())
    return HttpResponse(json.dumps(return_datas))
