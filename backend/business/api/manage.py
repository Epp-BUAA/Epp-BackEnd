"""
    管理端功能
    api/manage/...
    鉴权先不加了吧...
"""
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache
import json
from business.models import User, Paper, Admin, CommentReport, Notification, FirstLevelComment, SecondLevelComment
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
    mode = int(request.GET.get('mode'))
    if mode == 1:
        # 获取未处理的举报信息
        reports = CommentReport.objects.filter(judgment__isnull=True).order_by('-date')
    elif mode == 2:
        # 获取已处理的举报信息
        reports = CommentReport.objects.filter(judgment__isnull=False).order_by('-date')
    else:
        return reply.fail(msg="mode参数有误")

    data = {"total": len(reports), "reports": []}
    for report in reports:
        obj = {
            'id': report.id,
            'comment': {
                "comment_id": report.comment_id_1.comment_id if report.comment_id_1 else report.comment_id_2.comment_id,
                "user": report.comment_id_1.user_id.simply_desc() if report.comment_id_1 else report.comment_id_2.user_id.simply_desc(),
                "paper": report.comment_id_1.paper_id.simply_desc() if report.comment_id_1 else report.comment_id_2.paper_id.simply_desc(),
                "date": report.comment_id_1.date.strftime(
                    "%Y-%m-%d %H:%M:%S") if report.comment_id_1 else report.comment_id_2.date.strftime(
                    "%Y-%m-%d %H:%M:%S"),
                "content": report.comment_id_1.text if report.comment_id_1 else report.comment_id_2.text
            },
            'user': report.user_id.simply_desc(),
            'comment_level': report.comment_level,
            'date': report.date.strftime("%Y-%m-%d %H:%M:%S"),
            'content': report.content
        }
        if report.judgment:
            obj['judgement'] = report.judgment
        data['reports'].append(obj)

    return reply.success(data=data, msg="举报信息获取成功")


@require_http_methods('POST')
def judge_comment_report(request):
    """ 举报审核意见 """
    # todo 管理员鉴权
    params: dict = json.loads(request.body)
    report_id = params.get('id')
    judgment = params.get('judgment')
    # 讲审核意见填入举报表，同时发送信息给举报用户
    report = CommentReport.objects.filter(id=report_id).first()
    report.judgment = judgment
    report.save()
    Notification(user_id=report.user_id, title="您的举报已被审核", content=judgment).save()

    return reply.success(msg="举报已审核")


@require_http_methods('DELETE')
def delete_comment(request):
    """ 删除评论 """
    params: dict = json.loads(request.body)
    report_id = params.get('id')
    report = CommentReport.objects.filter(id=report_id).first()
    # 删除评论并通知用户
    level = report.comment_level
    if level == 1:
        Notification(user_id=report.comment_id_1.user_id, title="您的评论被举报了！",
                     content=f"您在 {report.comment_id_1.date.strftime('%Y-%m-%d %H:%M:%S')} 对论文《{report.comment_id_1.paper_id.title}》的评论内容 \"{report.comment_id_1.text}\" 被其他用户举报，根据EPP平台管理规定，检测到您的评论确为不合规，该评论现已删除。\n请注意遵守平台评论规范，理性发言！"
                     ).save()
        report.comment_id_1.delete()
    elif level == 2:
        Notification(user_id=report.comment_id_2.user_id, title="您的评论被举报了！",
                     content=f"您在 {report.comment_id_2.date.strftime('%Y-%m-%d %H:%M:%S')} 对论文《{report.comment_id_2.paper_id.title}》的评论内容 \"{report.comment_id_2.text}\" 被其他用户举报，根据EPP平台管理规定，检测到您的评论确为不合规，该评论现已删除。\n请注意遵守平台评论规范，理性发言！"
                     ).save()
        report.comment_id_2.delete()

    return reply.success(msg="评论已删除")
