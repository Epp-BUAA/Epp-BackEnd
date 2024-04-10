"""
用户搜索记录表
"""
from django.db import models
import uuid

from .user import User


class SearchRecord(models.Model):
    """
    Field:
        - search_record_id      搜素记录ID
        - user_id               用户ID
        - keyword               搜索关键字
    """
    search_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=255)