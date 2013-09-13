#coding=utf-8
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
import json

def main(request):
    return render_to_response('main.html')

def tree(request):    
    module_tree = []
    
    # 生成目录树节点
    tree_node = {}
    tree_node['href'] = "javascript:void(index_main('main_page', 'MediaServer管理系统'))"
    tree_node['icon'] = '/static/css/img/tree/earth.gif'
    tree_node['id'] = 1
    tree_node['leaf'] = True
    tree_node['qtip'] = '根节点'
    tree_node['singleClickExpand'] = True
    tree_node['text'] = 'MediaServer管理系统'
    module_tree.append(tree_node)
    
    # 移动平台
    tree_node = {}
    tree_node['href'] = ""
    tree_node['icon'] = '/static/css/img/tree/files.gif'
    tree_node['id'] = 3
    tree_node['leaf'] = False
    tree_node['qtip'] = '移动平台'
    tree_node['singleClickExpand'] = True
    tree_node['text'] = '移动平台'
    tree_node['children'] = []
    module_tree.append(tree_node)    
    
    child_node = {}
    child_node['href'] = "javascript:void(index_main('ms', '移动MS列表', 'mobile'))"
    child_node['icon'] = '/static/css/img/tree/files.gif'
    child_node['id'] = 5
    child_node['leaf'] = True
    child_node['qtip'] = 'MS列表'
    child_node['singleClickExpand'] = True
    child_node['text'] = 'MS列表'    
    tree_node['children'].append(child_node)
    
    child_node = {}
    child_node['href'] = "javascript:void(index_main('room', '移动机房列表', 'mobile'))"
    child_node['icon'] = '/static/css/img/tree/files.gif'
    child_node['id'] = 6
    child_node['leaf'] = True
    child_node['qtip'] = '机房列表'
    child_node['singleClickExpand'] = True
    child_node['text'] = '机房列表'
    tree_node['children'].append(child_node)
    
    child_node = {}
    child_node['href'] = "javascript:void(index_main('task', '移动任务列表', 'mobile'))"
    child_node['icon'] = '/static/css/img/tree/files.gif'
    child_node['id'] = 7
    child_node['leaf'] = True
    child_node['qtip'] = '任务列表'
    child_node['singleClickExpand'] = True
    child_node['text'] = '任务列表'
    tree_node['children'].append(child_node)
    
    child_node = {}
    child_node['href'] = "javascript:void(index_main('operation', '移动操作列表', 'mobile'))"
    child_node['icon'] = '/static/css/img/tree/files.gif'
    child_node['id'] = 8
    child_node['leaf'] = True
    child_node['qtip'] = '操作列表'
    child_node['singleClickExpand'] = True
    child_node['text'] = '操作列表'
    tree_node['children'].append(child_node)
    
    # PC平台
    tree_node = {}
    tree_node['href'] = ""
    tree_node['icon'] = '/static/css/img/tree/files.gif'
    tree_node['id'] = 4
    tree_node['leaf'] = False
    tree_node['qtip'] = 'PC平台'
    tree_node['singleClickExpand'] = True
    tree_node['text'] = 'PC平台'
    tree_node['children'] = []
    module_tree.append(tree_node)
    
    child_node = {}
    child_node['href'] = "javascript:void(index_main('ms', 'PC MS列表', 'pc'))"
    child_node['icon'] = '/static/css/img/tree/files.gif'
    child_node['id'] = 9
    child_node['leaf'] = True
    child_node['qtip'] = 'MS列表'
    child_node['singleClickExpand'] = True
    child_node['text'] = 'MS列表'    
    tree_node['children'].append(child_node)
    
    child_node = {}
    child_node['href'] = "javascript:void(index_main('room', 'PC机房列表', 'pc'))"
    child_node['icon'] = '/static/css/img/tree/files.gif'
    child_node['id'] = 10
    child_node['leaf'] = True
    child_node['qtip'] = '机房列表'
    child_node['singleClickExpand'] = True
    child_node['text'] = '机房列表'
    tree_node['children'].append(child_node)
    
    child_node = {}
    child_node['href'] = "javascript:void(index_main('task', 'PC任务列表', 'pc'))"
    child_node['icon'] = '/static/css/img/tree/files.gif'
    child_node['id'] = 11
    child_node['leaf'] = True
    child_node['qtip'] = '任务列表'
    child_node['singleClickExpand'] = True
    child_node['text'] = '任务列表'
    tree_node['children'].append(child_node)
    
    child_node = {}
    child_node['href'] = "javascript:void(index_main('operation', 'PC操作列表', 'pc'))"
    child_node['icon'] = '/static/css/img/tree/files.gif'
    child_node['id'] = 12
    child_node['leaf'] = True
    child_node['qtip'] = '操作列表'
    child_node['singleClickExpand'] = True
    child_node['text'] = '操作列表'
    tree_node['children'].append(child_node)
    
    # 退出系统节点
    tree_node = {}
    tree_node['href'] = "javascript:void(index_main('logout', '退出'))"
    tree_node['icon'] = '/static/css/img/tree/exits.gif'
    tree_node['id'] = 2
    tree_node['leaf'] = True
    tree_node['qtip'] = '退出'
    tree_node['singleClickExpand'] = True
    tree_node['text'] = '退出'
    module_tree.append(tree_node)
    
    return HttpResponse(json.dumps(module_tree))
