from django.db import models

# Create your models here.

class webusers(models.Model):
    username = models.CharField(max_length=30)
    pwd      = models.CharField(max_length=128)
    def __str__(self):# 在Python3中用 __str__ 代替 __unicode__
        return self.username