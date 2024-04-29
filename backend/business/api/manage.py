"""
    管理端功能
    api/manage/...
    鉴权先不加了吧...
"""
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache

from business.models import User, Paper, Admin, CommentReport
from business.utils import reply


@require_http_methods('GET')
def user_list(request):
    """ 检索用户列表 """
    # 鉴权先不加了吧...
    # manager_name = request.session.get('managerName')
    # manager = Admin.objects.filter(admin_name=manager_name).first()
    # if not manager:
    #    return reply.fail(msg="请完成管理员身份验证")

    keyword = request.GET.get('keyword', default=None)  # 搜索关键字
    page_num = request.GET.get('page_num', default=1)  # 页码
    page_size = request.GET.get('page_size', default=15)  # 每页条目数

    if keyword and len(keyword) > 0:
        users = User.objects.all().filter(username__contains=keyword)
    else:
        users = User.objects.all()

    key = 'userPaginator'
    paginator = cache.get(key)
    if not paginator:
        paginator = Paginator(users, page_size)
        cache.set(key, paginator)

    # 分页逻辑
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
    # 鉴权先不加了吧...
    # manager_name = request.session.get('managerName')
    # manager = Admin.objects.filter(admin_name=manager_name).first()
    # if not manager:
    #     return reply.fail(msg="请完成管理员身份验证")

    keyword = request.GET.get('keyword', default=None)  # 搜索关键字
    page_num = request.GET.get('page_num', default=1)  # 页码
    page_size = request.GET.get('page_size', default=15)  # 每页条目数

    if keyword and len(keyword) > 0:
        papers = Paper.objects.all().filter(title__contains=keyword)
    else:
        papers = Paper.objects.all()

    key = 'paperPaginator'
    paginator = cache.get(key)
    if not paginator:
        paginator = Paginator(papers, page_size)
        cache.set(key, paginator)
    try:
        contacts = paginator.page(page_num)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    print(len(contacts))
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
    # 鉴权先不加了吧...
    # manager_name = request.session.get('managerName')
    # manager = Admin.objects.filter(admin_name=manager_name).first()
    # if not manager:
    #     return reply.fail(msg="请完成管理员身份验证")

    pass


@require_http_methods('POST')
def reply_comment_report(request):
    """ 回复举报 """
    # todo 管理员鉴权

    pass

@require_http_methods('DELETE')
def delete_comment(request):
    """ 删除评论 """

