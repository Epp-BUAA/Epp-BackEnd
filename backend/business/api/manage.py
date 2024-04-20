"""
    数据管理模块API
    api/manage/...
"""
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json

from business.models import User, Paper
from business.utils import reply


@require_http_methods('GET')
def user_list(request):
    """ 检索用户列表 """
    keyword = request.GET.get('keyword', default=None)  # 搜索关键字
    page_num = request.GET.get('page_num', default=1)  # 页码
    page_size = request.GET.get('page_size', default=15)  # 每页条目数

    if keyword and len(keyword) > 0:
        users = User.objects.all().filter(username__contains=keyword)
    else:
        users = User.objects.all()

    paginator = Paginator(users, page_size)
    try:
        contacts = paginator.page(page_num)
    except PageNotAnInteger:
        # 如果用户请求的页码号不是整数，显示第一页
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果用户请求的页码号超过了最大页码号，显示最后一页
        contacts = paginator.page(paginator.num_pages)

    data = {"total": len(users), "users": list(map(
        lambda param: {
            "user_id": param.user_id,
            "username": param.username,
            "password": param.password,
            "registration_date": param.registration_date.strftime("%Y-%m-%d %H:%M:%S")
        },
        contacts))}

    return reply.success(data=data, msg="用户列表获取成功")


@require_http_methods('GET')
def paper_list(request):
    """ 论文列表 """
    keyword = request.GET.get('keyword', default=None)  # 搜索关键字
    page_num = request.GET.get('page_num', default=1)  # 页码
    page_size = request.GET.get('page_size', default=15)  # 每页条目数

    if keyword and len(keyword) > 0:
        papers = Paper.objects.all().filter(title__contains=keyword)
    else:
        papers = Paper.objects.all()

    paginator = Paginator(papers, page_size)
    try:
        contacts = paginator.page(page_num)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    data = {"total": len(papers), "papers": list(map(
        lambda paper: {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": paper.authors.split(','),
            "publication_date": paper.publication_date.strftime("%Y-%m-%d"),
            "journal": paper.journal,
            "citation_count": paper.citation_count,
            "read_count": paper.read_count,
            "like_count": paper.like_count,
            "collect_count": paper.collect_count,
            "download_count": paper.download_count,
            "score": paper.score
        },
        contacts))}

    return reply.success(data=data, msg="论文列表获取成功")


@require_http_methods('GET')
def comment_report_list(request):
    """ 举报列表 """
    pass


@require_http_methods('POST')
def judge_comment(request):
    """ 处理举报信息和评论 """
    pass
