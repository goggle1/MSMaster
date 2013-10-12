#!/usr/bin/env python
import os
import sys


class STH:
    def __init__(self):
        self.a = 1
        
if __name__ == "__main__":
    '''
    my_dict = {}
    sth = STH()
    my_dict['1'] = sth
    
    value1 = my_dict['1']
    value1.a = 2
    print 'value1: %d' % (value1.a)
    
    value2 = my_dict['1']
    print 'value2: %d' % (value2.a) 
    '''
    
    '''
    my_dict = {}
    my_dict['1'] = 1000
    
    value1 = my_dict['1']
    value1 = 2000
    print 'value1: %d' % (value1)
    
    value2 = my_dict['1']
    print 'value2: %d' % (value2)
    '''
    
    '''
    my_dict = {}
    my_dict['1'] = 'string1'
    
    value1 = my_dict['1']
    value1 = 'string2'
    print 'value1: %s' % (value1)
    
    value2 = my_dict['1']
    print 'value2: %s' % (value2)
    '''
    
    '''    
    my_dict = {}
    list1 = []
    list1.append(1000)
    list1.append(2000)
    my_dict['1'] = list1
    
    value1 = my_dict['1']
    value1.append(3000)
    print value1
    
    value2 = my_dict['1']
    print value2    
    '''
    
    '''
    my_dict = {}
    dict1 = {}
    dict1['key1'] = 1000
    dict1['key2'] = 2000
    my_dict['1'] = dict1
    
    value1 = my_dict['1']
    value1['key3'] = 3000
    print value1.items()
    
    value2 = my_dict['1']
    print value2.items()
    '''
       
    
    reload(sys)                         
    sys.setdefaultencoding('utf-8')  
       
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MSMaster.settings")
    
    from django.core.management import execute_from_command_line
    
    execute_from_command_line(sys.argv)
    
    
    
    
    
