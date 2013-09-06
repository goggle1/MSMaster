from django.db import models

# Create your models here.

class mobile_task(models.Model):
    # config
    hash         = models.CharField(max_length=40, primary_key=True, verbose_name = u"hash")
    create_time  = models.DateTimeField(auto_now_add=True, verbose_name = u"create_time")
    hits_num     = models.IntegerField(blank = False, null = True,  verbose_name = u"hits_num")
    cold         = models.FloatField(blank = False, null = True,  verbose_name = u"cold") 
    
    def todict(self):
        dic = {}
        dic['hash'] = str(self.hash)
        dic['create_time'] = str(self.create_time)
        dic['hits_num'] = str(self.hits_num)
        dic['cold'] = str(self.cold)
        return dic
    
    class Meta:
        db_table    = "mobile_task" 
        
class pc_task(models.Model):
    # config
    hash         = models.CharField(max_length=40, primary_key=True, verbose_name = u"hash")
    create_time  = models.DateTimeField(auto_now_add=True, verbose_name = u"create_time")
    hits_num     = models.IntegerField(blank = False, null = True,  verbose_name = u"hits_num")
    cold         = models.FloatField(blank = False, null = True,  verbose_name = u"cold") 
    
    def todict(self):
        dic = {}
        dic['hash'] = str(self.hash)
        dic['create_time'] = str(self.create_time)
        dic['hits_num'] = str(self.hits_num)
        dic['cold'] = str(self.cold)
        return dic
    
    class Meta:
        db_table    = "pc_task" 
