"""
综述报告表
"""
from django.db import models

from .user import User


class SummaryReport(models.Model):
    """
    Field:
        - user_id            用户ID
        - report_path        综述报告文件地址
        - title              综述报告title
        - date               时间
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    report_path = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
