#coding=utf-8
import urllib2

class MS_INFO:
    platform = ''
    db_record = None
    task_list = []
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
                                one.task_list.append(items[5])
                                #print '%s append task %s' % (one.db_record.controll_ip, items[5])
            except:
                print '%s get tasks error' % (one.db_record.controll_ip)
            print '%s get tasks end, %d' % (one.db_record.controll_ip, len(one.task_list))    
            
        return True
    
    
    def find_task(self, task_hash):
        result = False
    
        for one in self.ms_list:
            for hash_id in one.task_list:
                if(hash_id == task_hash):
                    return True
            
        return result
    
    
    def dispatch_task(self, task_hash):        
        one = self.ms_list[self.round_robin_index]
        one.change_list.append(task_hash)
        print '%s dispatch task %s' % (one.db_record.controll_ip, task_hash)
        
        self.round_robin_index += 1
        if(self.round_robin_index >= len(self.ms_list)):
            self.round_robin_index = 0    
            
        return True
    
    
    def get_cur_ms(self):
        one = self.ms_list[self.round_robin_index]
        return one
    
        
