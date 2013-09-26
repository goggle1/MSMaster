#coding=utf-8
import time
import urllib
import urllib2
import hashlib

class MS_INFO:
    platform = ''
    db_record = None
    #task_list = []
    task_dict = {}
    change_list = []
    
    def __init__(self, v_platform, v_db_record):
        self.platform = v_platform
        self.db_record = v_db_record
        
        
        
class MS_ALL:
    ms_list = []
    round_robin_index = 0
    
    def __init__(self, v_platform, v_ms_list):
        for ms in v_ms_list:
            ms_info = MS_INFO(v_platform, ms)
            self.ms_list.append(ms_info)
            
            
    def get_tasks(self):
        for one in self.ms_list:
            print '%s get tasks begin' % (one.db_record.controll_ip)
            try:        
                url = 'http://%s:%d/macross?cmd=enumtask' % (one.db_record.controll_ip, one.db_record.controll_port)
                print url
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                output = response.read()
                #print output
                #return=ok
                #result=骑呢大状（国语版）-第16集-PAD:fsp:0:0:100:00001C597A755CF0D6A19D7F675C927047FF267E:1|国家地理之伟大工程巡礼系列-超级潜艇-HDPAD:fsp:0:0:100:00009D980AC62CE44ECFB4C22C735CF3EDA8267C:1|
                lines = output.split('\n')
                if(len(lines)>=2):
                    line_1 = lines[0].strip()
                    line_2 = lines[1].strip()
                    if(line_1 == 'return=ok'):
                        fields = line_2.split('=')
                        field2 = fields[1]
                        values = field2.split('|')
                        for value in values:
                            items = value.split(':')
                            if(len(items) >= 7):
                                #one.task_list.append(items[5])
                                one.task_dict[items[5]] = '1'
                                #print '%s append task %s' % (one.db_record.controll_ip, items[5])
            except:
                print '%s get tasks error' % (one.db_record.controll_ip)
            #print '%s get tasks end, %d' % (one.db_record.controll_ip, len(one.task_list))    
            print '%s get tasks end, %d' % (one.db_record.controll_ip, len(one.task_dict))
            
        return True
    
    
    def find_task(self, task_hash):
        '''
        for one in self.ms_list:
            for hash_id in one.task_list:
                if(hash_id == task_hash):
                    return True
        '''
        for one in self.ms_list:
            if(one.task_dict.has_key(task_hash)):
                return True            
        return False
    
    
    def dispatch_task(self, task_hash):        
        one = self.ms_list[self.round_robin_index]
        one.change_list.append(task_hash)
        print '%s dispatch task %s' % (one.db_record.controll_ip, task_hash)
        
        self.round_robin_index += 1
        if(self.round_robin_index >= len(self.ms_list)):
            self.round_robin_index = 0    
            
        return True
    
    '''
    http://MacrossAddress[:MacrossPort]/api?cli=ms&cmd=report_hot_task
            提交方式：POST
            参数说明：
            $server_id：设备id
            $priority：处理的优先级权重,范围1~10，默认为1
            $ctime：当前时间戳，单位：秒
            $t：热门任务的hashid hashid,hashid,hashid[,hashid,……],hashid统一使用大写
            $sign：验证码；sign=md5(msreport_hot_task$server_id$priority$ctime$t$key),sign统一为小写
    '''
    def dispatch_to_ms(self, one):
        cmd = 'report_hot_task'
        
        server_id = one.db_record.server_id
        priority = 1
        ctime = int(time.time())        
        t = ''
        key = ''
        sign = ''    
        
        num = 0
        for task_hash in one.change_list:
            if(num > 0):
                t += ','
            t += task_hash
            num += 1 
            
        src = ''
        src += cmd
        src += str(server_id)
        src += str(priority)
        src += str(ctime)
        src += t
        src += key
        sign = hashlib.md5(src).hexdigest().upper()
        
        values = {}
        values['server_id'] = str(server_id)
        values['priority']  = str(priority)
        values['ctime']     = str(ctime)
        values['t']         = t
        values['sign']      = sign
        
        macross_ip = '192.168.160.128'
        macross_port = 80
        url = 'http://%s:%d/api?cli=ms&cmd=report_hot_task' % (macross_ip, macross_port)
        
        data = urllib.urlencode(values)
        print data
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        print the_page
        
        return True
        
        
    
    def do_dispatch(self):        
        for one in self.ms_list:
            self.dispatch_to_ms(one)
        return True
                
    
    
    def get_cur_ms(self):
        one = self.ms_list[self.round_robin_index]
        return one
    
        
