"""
举报审核表
"""
from django.db import models

from .user import User


class CommentReport(models.Model):
    """
    Field:
        - comment_id         评论ID
        - user_id            用户ID
        - date               举报时间
        - content            举报内容
        - judgment           处理意见
    """
    comment_id = models.IntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=255)
    judgment = models.CharField(max_length=255, null=True, blank=True)
