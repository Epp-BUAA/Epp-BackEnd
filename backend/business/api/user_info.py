"""
用户信息模块API
api/userInfo/...
"""
from django.views.decorators.http import require_http_methods
import json

from business.models import User
from business.utils import req


@require_http_methods('GET')
def user_info(request):
    """ 用户基础信息 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if user:
        return req.success(data={'user_id': user.user_id,
                                 'username': user.username,
                                 'avatar': user.avatar.url,
                                 'registration_date': user.registration_date,
                                 'collected_papers_cnt': user.collected_papers.all().count(),
                                 'liked_papers_cnt': user.liked_papers.all().count()},
                           msg='个人信息获取成功')
    else:
        return req.fail(msg="请先正确登录")


@require_http_methods('POST')
def modify_avatar(request):
    """ 修改用户头像 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if user:
        user.avatar = request.FILES['avatar']
        user.save()
        return req.success(data={'avatar': user.avatar.url}, msg='头像修改成功')
    else:
        return req.fail(msg="请先正确登录")


@require_http_methods('GET')
def collected_papers(request):
    """ 收藏文献列表 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if not user:
        return req.fail(msg="请先正确登录")
    data = {'total': 0, 'papers': []}
    papers_cnt = 0
    for paper in user.collected_papers.all():
        papers_cnt += 1
        data['papers'].append({
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": paper.authors.split(','),
            "abstract": paper.abstract,
            "publication_date": paper.publication_date,
            "journal": paper.journal,
            "citation_count": paper.citation_count,
            "read_count": paper.read_count,
            "like_count": paper.like_count,
            "collect_count": paper.collect_count,
            "download_count": paper.download_count,
            "score": paper.score
        })
    data['total'] = papers_cnt
    return req.success(data=data, msg='收藏文章列表获取成功')


@require_http_methods('GET')
def search_history(request):
    """ 收藏文献列表 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if not user:
        return req.fail(msg="请先正确登录")
    data = {'total': 0, 'papers': []}
    papers_cnt = 0
    for paper in user.collected_papers.all():
        papers_cnt += 1
        data['papers'].append({
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": paper.authors.split(','),
            "abstract": paper.abstract,
            "publication_date": paper.publication_date,
            "journal": paper.journal,
            "citation_count": paper.citation_count,
            "read_count": paper.read_count,
            "like_count": paper.like_count,
            "collect_count": paper.collect_count,
            "download_count": paper.download_count,
            "score": paper.score
        })
    data['total'] = papers_cnt
    return req.success(data=data, msg='收藏文章列表获取成功')