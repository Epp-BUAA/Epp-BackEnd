"""
    数据管理模块API
    api/admin/...
"""
from django.views.decorators.http import require_http_methods
import json


from business.models import User
from business.utils import reply


@require_http_methods('GET')
def user_list(request):
    """ 检索用户列表 """
    pass


@require_http_methods('GET')
def paper_list(request):
    """ 论文列表 """
    pass


@require_http_methods('GET')
def comment_report_list(request):
    """ 举报列表 """
    pass


@require_http_methods('POST')
def judge_comment(request):
    """ 处理举报信息和评论 """
    pass
