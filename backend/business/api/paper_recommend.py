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

# class refreshRecomendation(CronJobBase):
#     RUN_AT_TIMES = ['00:00']

#     schedule = Schedule(run_at_times=RUN_AT_TIMES)
#     code = 'yourappname.my_daily_task'

#     def do(self):
#         # 在这里写你想要执行的任务
#         pass
    

def get_recommendation(request):
    # 从arXiv上爬取最近一周的cv的每天10篇论文
    # 然后通过总结这些论文的关键词，来进行推荐
    from business.models import Paper
    
    l = Paper.objects.all()
    import random
    
    # 随机五个
    papers = []
    for i in range(5):
        papers.append(random.choice(l).__dict__)
        
    return reply.success({ 'papers': papers })