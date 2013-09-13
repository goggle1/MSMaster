#-*-coding:utf-8-*-
from django.db import models

# Create your models here.
class mobile_task(models.Model):
    # config
    hash            = models.CharField(max_length = 40, primary_key = True, verbose_name = u"hash")
    online_time     = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"online_time")   
    is_valid        = models.IntegerField(blank = False, null = True,  verbose_name = u"is_valid")    
    hot             = models.IntegerField(blank = False, null = True,  verbose_name = u"hot")    
    cold1           = models.FloatField(blank = False, null = True,  verbose_name = u"cold1")
    cold2           = models.FloatField(blank = False, null = True,  verbose_name = u"cold2")
    cold3           = models.FloatField(blank = False, null = True,  verbose_name = u"cold3")
    last_hit_time   = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"last_hit_time")
    total_hits_num  = models.IntegerField(blank = False, null = True,  verbose_name = u"total_hits_num") 
    
    class Meta:
        db_table    = "mobile_task"
        
    def todict(self):
        dic = {}
        dic['hash']             = str(self.hash)
        dic['online_time']      = str(self.online_time)
        dic['is_valid']         = str(self.is_valid)
        dic['hot']              = str(self.hot)
        dic['cold1']            = str(self.cold1)
        dic['cold2']            = str(self.cold2)
        dic['cold3']            = str(self.cold3)
        dic['last_hit_time']    = str(self.last_hit_time)
        dic['total_hits_num']   = str(self.total_hits_num)
        return dic
         
        
class pc_task(models.Model):
    # config
    hash            = models.CharField(max_length = 40, primary_key = True, verbose_name = u"hash")
    online_time     = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"online_time")  
    is_valid        = models.IntegerField(blank = False, null = True,  verbose_name = u"is_valid")    
    hot             = models.FloatField(blank = False, null = True,  verbose_name = u"hot")    
    cold1           = models.FloatField(blank = False, null = True,  verbose_name = u"cold1")
    cold2           = models.FloatField(blank = False, null = True,  verbose_name = u"cold2")
    cold3           = models.FloatField(blank = False, null = True,  verbose_name = u"cold3")
    last_hit_time   = models.DateTimeField(null = True, auto_now_add = False, verbose_name = u"last_hit_time")
    total_hits_num  = models.IntegerField(blank = False, null = True,  verbose_name = u"total_hits_num") 
    
    class Meta:
        db_table    = "pc_task"
        
    def todict(self):
        dic = {}
        dic['hash']             = str(self.hash)
        dic['online_time']      = str(self.online_time)
        dic['is_valid']         = str(self.is_valid)
        dic['hot']              = str(self.hot)
        dic['cold1']            = str(self.cold1)
        dic['cold2']            = str(self.cold2)
        dic['cold3']            = str(self.cold3)
        dic['last_hit_time']    = str(self.last_hit_time)
        dic['total_hits_num']   = str(self.total_hits_num)
        return dic  
    
