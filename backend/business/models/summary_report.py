"""
综述报告表
"""
from django.db import models
import uuid

from .user import User


class SummaryReport(models.Model):
    """
    Field:
        - report_id          报告ID
        - user_id            用户ID
        - report_path        综述报告文件地址
        - title              综述报告title
        - date               时间
    """
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    report_path = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
