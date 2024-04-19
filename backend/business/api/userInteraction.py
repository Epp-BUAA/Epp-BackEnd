"""
    用户交互模块
"""
import json
from django.http import JsonResponse
from business.models import User, Paper, PaperScore, CommentReport, FirstLevelComment, SecondLevelComment


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


def report_comment(request):
    """
    举报评论
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        comment_id = data.get('comment_id')
        comment_level = data.get('comment_level')
        report = data.get('report')
        user = User.objects.filter(username=username).first()
        # 这里需要知道是一级评论还是二级评论
        comment = None
        if comment_level == 1:
            comment = FirstLevelComment.objects.filter(comment_id=comment_id).first()
        elif comment_level == 2:
            comment = SecondLevelComment.objects.filter(comment_id=comment_id).first()
        if user and comment:
            if comment_level == 1:
                report_com = CommentReport(comment_id_1=comment, user_id=user, content=report)
                report_com.save()
            elif comment_level == 2:
                report_com = CommentReport(comment_id_2=comment, user_id=user, content=report)
                report_com.save()
            return JsonResponse({'message': '举报成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或评论不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def comment_paper(request):
    """
    用户评论（含一级、二级评论）
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_id = data.get('paper_id')
        comment_level = data.get('comment_level')  # 1 / 2
        text = data.get('comment')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        if user and paper:
            if comment_level == 1:
                comment = FirstLevelComment(user_id=user, paper_id=paper, text=text)
                comment.save()
            elif comment_level == 2:
                level1_comment_id = data.get('level1_comment_id')
                level1_comment = FirstLevelComment.objects.filter(comment_id=level1_comment_id).first()
                # 如果是回复二级评论的评论，获取其回复的二级评论的id
                reply_comment_id = data.get('reply_comment_id')
                reply_comment = None
                if reply_comment_id:
                    reply_comment = SecondLevelComment.objects.filter(comment_id=reply_comment).first()
                comment = SecondLevelComment(user_id=user, paper_id=paper, text=text, level1_comment=level1_comment,
                                             reply_comment=reply_comment)
                comment.save()
            return JsonResponse({'message': '评论成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)
