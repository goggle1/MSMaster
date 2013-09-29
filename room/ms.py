#coding=utf-8
import time
import urllib
import urllib2
import hashlib

class MS_INFO:
    #platform = ''
    #db_record = None
    #task_list = []
    #task_dict = {}
    #change_list = []
    
    def __init__(self, v_platform, v_db_record):        
        self.platform = ''
        self.db_record = None
        #self.task_list = []
        self.task_dict = {}
        self.change_list = []
    
        self.platform = v_platform
        self.db_record = v_db_record
        
        
        
class MS_ALL:
    #ms_list = []
    #round_robin_index = 0
    
    def __init__(self, v_platform, v_ms_list):
        self.ms_list = []
        self.round_robin_index = 0
        
        for ms in v_ms_list:
            ms_info = MS_INFO(v_platform, ms)
            self.ms_list.append(ms_info)
            
            
    def get_tasks(self):
        for one in self.ms_list:
            print '%s get tasks begin' % (one.db_record.controll_ip)
            #file_name = 'enum_task_%s.log' % (one.db_record.controll_ip)
            #log_file = open(file_name, 'w')
            try:        
                url = 'http://%s:%d/macross?cmd=enumtask' % (one.db_record.controll_ip, one.db_record.controll_port)
                print url
                #log_file.write('\nstep1: \n%s' % (url))
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                output = response.read()
                #print output
                #log_file.write('\nstep2: \n%s' % (output))
                #return=ok
                #result=骑呢大状（国语版）-第16集-PAD:fsp:0:0:100:00001C597A755CF0D6A19D7F675C927047FF267E:1|国家地理之伟大工程巡礼系列-超级潜艇-HDPAD:fsp:0:0:100:00009D980AC62CE44ECFB4C22C735CF3EDA8267C:1|
                lines = output.split('\n')
                if(len(lines)>=2):
                    line_1 = lines[0].strip()
                    line_2 = lines[1].strip()
                    if(line_1 == 'return=ok'):
                        #fields = line_2.split('=')
                        prefix_len = len('result=')                        
                        field2 = line_2[prefix_len:]
                        #log_file.write('\nstep3: \n%s' % (field2))
                        values = field2.split('|')
                        for value in values:
                            #log_file.write('\nstep4: \n%s' % (value))
                            items = value.split(':')
                            if(len(items) >= 7):
                                #one.task_list.append(items[5])
                                one.task_dict[items[5]] = '1'
                                #log_file.write('\nstep5: \n%s' % (items[5]))
                                #print '%s append task %s' % (one.db_record.controll_ip, items[5])
            except:
                print '%s get tasks error' % (one.db_record.controll_ip)
            #print '%s get tasks end, %d' % (one.db_record.controll_ip, len(one.task_list))    
            print '%s get tasks end, %d' % (one.db_record.controll_ip, len(one.task_dict))
            #log_file.write('\nstep6: tasks_num=%d\n' % (len(one.task_dict)))
            #log_file.close()
        return True
    
    
    def get_tasks_num(self):
        total_num = 0
        for one in self.ms_list:
            total_num += len(one.task_dict)
        return total_num
            
            
    def find_task(self, task_hash):
        '''
        for one in self.ms_list:
            for hash_id in one.task_list:
                if(hash_id == task_hash):
                    return True
        '''
        for one in self.ms_list:
            if(one.task_dict.has_key(task_hash)):
                return one            
        return None
            
        
    def dispatch_hot_task(self, task_hash):   
        # find_availiable_ms 
        the_ms = None
        ms_index = 0    
        for index in range(0, len(self.ms_list)):
            ms_index = self.round_robin_index + index
            if(ms_index >= len(self.ms_list)):
                ms_index = ms_index % len(self.ms_list)
            the_ms = self.ms_list[ms_index]
            if(the_ms.db_record.is_dispatch == 1):
                break
            else:
                print '%d: %s is_dispatched is %d' % (index, str(the_ms.db_record.controll_ip), the_ms.db_record.is_dispatch)
        if(the_ms == None):
            return None
        the_ms.change_list.append(task_hash)
        self.round_robin_index = ms_index
        return the_ms
        
    
    def delete_cold_task(self, one_ms, task_hash): 
        one_ms.change_list.append(task_hash)
        print '%s delete task %s' % (one_ms.db_record.controll_ip, task_hash)            
        return True
    
    
    '''
    http://MacrossAddress[:MacrossPort]/api/?cli=ms&cmd=report_hot_task
            提交方式：POST
            参数说明：
            $server_id：设备id
            $priority：处理的优先级权重,范围1~10，默认为1
            $ctime：当前时间戳，单位：秒
            $t：热门任务的hashid hashid,hashid,hashid[,hashid,……],hashid统一使用大写
            $sign：验证码；sign=md5(msreport_hot_task$server_id$priority$ctime$t$key),sign统一为小写
    '''
    def dispatch_batch(self, one, batch_list):
        cmd = 'report_hot_task'
        server_id = one.db_record.server_id
        priority = 1
        ctime = int(time.time())        
        t = ''
        key = ''
        sign = ''  
        
        num = 0
        for task_hash in batch_list:
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
        sign = hashlib.md5(src).hexdigest().lower()
        
        values = {}
        values['server_id'] = str(server_id)
        values['priority']  = str(priority)
        values['ctime']     = str(ctime)
        values['t']         = t
        values['sign']      = sign
        
        MACROSS_IP = '192.168.160.128'
        MACROSS_PORT = 80
        #MACROSS_IP = 'macross.funshion.com'
        #MACROSS_PORT = 27777
        url = 'http://%s:%d/api/?cli=ms&cmd=report_hot_task' % (MACROSS_IP, MACROSS_PORT)
        print url
        print 'num=%d' % (num)
        
        data = urllib.urlencode(values)
        print data
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        print the_page
        
        return True        
        
        
    def dispatch_to_ms(self, one):        
        BATCH_NUM = 2000                 
        
        num = 0
        batch_list = []
        for task_hash in one.change_list:
            batch_list.append(task_hash)
            num += 1 
            if(num>=BATCH_NUM):
                self.dispatch_batch(one, batch_list)                
                num = 0
                batch_list = []
        
        if(num > 0):
            self.dispatch_batch(one, batch_list)
               
        return True
        
    
    def do_dispatch(self):        
        for one in self.ms_list:
            self.dispatch_to_ms(one)
        return True
    
    
    '''
    http://MacrossAddress[:MacrossPort]/api/?cli=ms&cmd=report_cold_task
            提交方式：POST
            参数说明：
            $server_id：设备id
            $priority：处理的优先级权重,范围1~10，默认为1
            $ctime：当前时间戳，单位：秒
            $t：热门任务的hashid hashid,hashid,hashid[,hashid,……],hashid统一使用大写
            $sign：验证码；sign=md5(msreport_cold_task$server_id$priority$ctime$t$key),sign统一为小写
    '''
    def delete_batch(self, one, batch_list):
        cmd = 'report_cold_task'
        server_id = one.db_record.server_id
        priority = 1
        ctime = int(time.time())        
        t = ''
        key = ''
        sign = ''  
        
        num = 0
        for task_hash in batch_list:
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
        sign = hashlib.md5(src).hexdigest().lower()
        
        values = {}
        values['server_id'] = str(server_id)
        values['priority']  = str(priority)
        values['ctime']     = str(ctime)
        values['t']         = t
        values['sign']      = sign
        
        MACROSS_IP = '192.168.160.128'
        MACROSS_PORT = 80
        #MACROSS_IP = 'macross.funshion.com'
        #MACROSS_PORT = 27777
        url = 'http://%s:%d/api/?cli=ms&cmd=report_cold_task' % (MACROSS_IP, MACROSS_PORT)
        print url
        print 'num=%d' % (num)
        
        data = urllib.urlencode(values)
        print data
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        print the_page
        
        return True        
    
    
    def delete_from_ms(self, one):        
        BATCH_NUM = 2000                 
        
        num = 0
        batch_list = []
        for task_hash in one.change_list:
            batch_list.append(task_hash)
            num += 1 
            if(num>=BATCH_NUM):
                self.delete_batch(one, batch_list)                
                num = 0
                batch_list = []
        
        if(num > 0):
            self.delete_batch(one, batch_list)
               
        return True
    
    
    def do_delete(self):        
        for one in self.ms_list:
            self.delete_from_ms(one)
        return True
    
    
    def get_cur_ms(self):
        one = self.ms_list[self.round_robin_index]
        return one
    
        
