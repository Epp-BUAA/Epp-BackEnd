"""
摘要报告表
"""
from django.db import models


class AbstractReport(models.Model):
    """
    Field:
        - file_local_path      文件本地地址
        - report_path          摘要报告文件地址
    """
    
    file_local_path = models.CharField(max_length=255, primary_key=True)
    report_path = models.CharField(max_length=255, unique=True)
