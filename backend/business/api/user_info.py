"""
    用户信息模块API
    api/userInfo/...
"""
import json

from django.views.decorators.http import require_http_methods

from business.models import User
from business.models import SearchRecord
from business.models import SummaryReport
from business.models import UserDocument
from business.utils import reply


@require_http_methods('GET')
def user_info(request):
    """ 用户基础信息 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if user:
        return reply.success(data={'user_id': user.user_id,
                                   'username': user.username,
                                   'avatar': user.avatar.url,
                                   'registration_date': user.registration_date.strftime("%Y-%m-%d %H:%M:%S"),
                                   'collected_papers_cnt': user.collected_papers.all().count(),
                                   'liked_papers_cnt': user.liked_papers.all().count()},
                             msg='个人信息获取成功')
    else:
        return reply.fail(msg="请先正确登录")


@require_http_methods('POST')
def modify_avatar(request):
    """ 修改用户头像 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if user:
        user.avatar = request.FILES['avatar']
        user.save()
        return reply.success(data={'avatar': user.avatar.url}, msg='头像修改成功')
    else:
        return reply.fail(msg="请先正确登录")


@require_http_methods('GET')
def collected_papers(request):
    """ 收藏文献列表 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if not user:
        return reply.fail(msg="请先正确登录")
    data = {'total': 0, 'papers': []}
    papers_cnt = 0
    for paper in user.collected_papers.all():
        papers_cnt += 1
        data['papers'].append({
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": paper.authors.split(','),
            "abstract": paper.abstract,
            "publication_date": paper.publication_date.strftime("%Y-%m-%d"),
            "journal": paper.journal,
            "citation_count": paper.citation_count,
            "read_count": paper.read_count,
            "like_count": paper.like_count,
            "collect_count": paper.collect_count,
            "download_count": paper.download_count,
            "score": paper.score
        })
    data['total'] = papers_cnt
    return reply.success(data=data, msg='收藏文章列表获取成功')


@require_http_methods('GET')
def search_history(request):
    """ 搜索历史列表 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if not user:
        return reply.fail(msg="请先正确登录")
    SearchRecord(user_id=user, keyword="man~").save()
    search_records = SearchRecord.objects.filter(user_id=user).order_by('-date')
    data = {'total': len(search_records), 'keywords': []}
    for item in search_records:
        data['keywords'].append({
            "search_record_id": item.search_record_id,
            "keyword": item.keyword,
            "date": item.date.strftime("%Y-%m-%d %H:%M:%S")
        })
    return reply.success(data=data, msg='搜索历史记录获取成功')


@require_http_methods('DELETE')
def delete_search_history(request):
    """ 删除历史搜索记录 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if not user:
        return reply.fail(msg="请先正确登录")
    params: dict = json.loads(request.body)
    search_record_id = params.get("search_record_id", None)
    print(search_record_id)
    if search_record_id:
        record = SearchRecord.objects.filter(search_record_id=search_record_id).first()
        if record:
            record.delete()
        else:
            return reply.fail(msg="搜索记录不存在")
    else:
        SearchRecord.objects.filter(user_id=user).delete()
    return reply.success(msg="记录已删除")


@require_http_methods('GET')
def summary_report(request):
    """ 查看用户生成的综述报告列表 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if not user:
        return reply.fail(msg="请先正确登录")

    summary_reports = SummaryReport.objects.filter(user_id=user)
    data = {'total': len(summary_reports), 'reports': []}
    for report in summary_reports:
        data['reports'].append({
            "title": report.title,
            "path": report.report_path,
            "date": report.date.strftime("%Y-%m-%d %H:%M:%S")
        })
    return reply.success(data=data, msg='综述报告列表获取成功')


@require_http_methods('GET')
def document_list(request):
    """ 用户上传文件列表 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if not user:
        return reply.fail(msg="请先正确登录")

    documents = UserDocument.objects.filter(user_id=user).order_by('-upload_date')
    data = {'total': len(documents), 'documents': []}
    for document in documents:
        data['documents'].append({
            "document_id": document.document_id,
            "title": document.title,
            "format": document.format,
            "size": document.size,
            "date": document.date.strftime("%Y-%m-%d %H:%M:%S")
        })
    return reply.success(data=data, msg='文件列表获取成功')