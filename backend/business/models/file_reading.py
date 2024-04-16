"""
用户论文研读记录表
"""
from django.db import models

from .user import User


class FileReading(models.Model):
    """
    Field:
        - user_id               用户ID
        - file_local_path       研读文件本地地址
        - title                 研读标题
        - conservation_path     对话记录文件地址
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    file_local_path = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    conversation_path = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = [['user_id', 'file_local_path']]
