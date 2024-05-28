'''
用于热门文献推荐，热门文献推荐基于用户的搜索历史，点赞历史，收藏历史
'''
# -*- coding: utf-8 -*-
"""
几乎所有推荐系统都是有着前后顺序的，但是我们的没有这些，这也就意味着我们的推荐系统是一个无状态的推荐系统
所以我选择了从arXiv上爬取最近一周的cv的每天10篇论文，然后通过总结这些论文的关键词，来进行推荐
"""


# 定时调用这个接口
# yourappname/tasks.py

from django_cron import CronJobBase, Schedule
from django.utils import timezone
from business.utils import reply
from business.models import Paper
import random

# class refreshRecomendation(CronJobBase):
#     RUN_AT_TIMES = ['00:00']

#     schedule = Schedule(run_at_times=RUN_AT_TIMES)
#     code = 'yourappname.my_daily_task'

#     def do(self):
#         # 在这里写你想要执行的任务
#         pass
    

from django.core.cache import cache

def get_recommendation(request):
    # 尝试从缓存中获取推荐数据
    cached_papers = cache.get('recommended_papers')
    if cached_papers:
        return reply.success(data={'papers': cached_papers}, msg='success')

    # 从数据库中获取所有 Paper 对象的 ID
    papers_ids = Paper.objects.values_list('id', flat=True)

    # 随机选择五篇论文的 ID
    selected_paper_ids = random.sample(papers_ids, min(5, len(papers_ids)))

    # 获取选中论文的详细信息
    selected_papers = Paper.objects.filter(id__in=selected_paper_ids)

    # 将选中的论文对象转换为字典
    papers = [paper.to_dict() for paper in selected_papers]

    # 将推荐数据缓存一天
    cache.set('recommended_papers', papers, timeout=86400)

    return reply.success(data={'papers': papers}, msg='success')
