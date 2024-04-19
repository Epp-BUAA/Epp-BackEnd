"""
    用户交互模块
"""
import json
from django.http import JsonResponse
from business.models import User, Paper, PaperScore


def like_paper(request):
    """
    点赞/取消点赞文献
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_id = data.get('paper_id')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        liked = user.liked_papers.filter(paper_id=paper_id).first()
        # 取消点赞
        if liked:
            user.liked_papers.remove(paper)
            paper.like_count -= 1
            user.save()
            paper.save()
            return JsonResponse({'message': '取消点赞成功', 'is_success': True})
        # 点赞
        if user and paper:
            user.liked_papers.add(paper)
            paper.like_count += 1
            user.save()
            paper.save()
            return JsonResponse({'message': '点赞成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def score_paper(request):
    """
    文献评分
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_id = data.get('paper_id')
        score = data.get('score')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        paper_score = PaperScore.objects.filter(user_id=user, paper_id=paper).first()
        # 判断用户是否对该文献进行过评分
        if paper_score:
            return JsonResponse({'error': '用户已对该文献进行过评分', 'is_success': False}, status=400)
        # 判断评分是否在1到5之间，且为整数
        if not isinstance(score, int) or score < 1 or score > 5:
            return JsonResponse({'error': '评分应为0到10之间的整数', 'is_success': False}, status=400)
        # 存储评分，更新文献平均分，保留两位小数
        if user and paper:
            paper_score = PaperScore(user_id=user, paper_id=paper, score=score)
            paper_score.save()
            paper.score_count += 1
            paper.score = round((paper.score * (paper.score_count - 1) + score) / paper.score_count, 2)
            paper.save()
            return JsonResponse({'message': '评分成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def collect_paper(request):
    """
    收藏/取消收藏文献
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_id = data.get('paper_id')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        collected = user.collected_papers.filter(paper_id=paper_id).first()
        # 取消收藏
        if collected:
            user.collected_papers.remove(paper)
            paper.collect_count -= 1
            user.save()
            paper.save()
            return JsonResponse({'message': '取消收藏成功', 'is_success': True})
        # 收藏
        if user and paper:
            user.collected_papers.add(paper)
            paper.collect_count += 1
            user.save()
            paper.save()
            return JsonResponse({'message': '收藏成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)
