"""
数据库统计
"""
from django.db import models


class UserDailyAddition(models.Model):
    """
    Field:
        - date          时间
        - addition      用户新增
    """
    date = models.DateField(auto_now=True)
    addition = models.IntegerField(default=0)
