'''
本文件主要处理搜索功能，包括向量化检索和对话检索
API格式如下：
api/serach/...
'''
import json, openai
import os

from django.db.models import Q
from django.http import JsonResponse, HttpRequest
from business.models.search_record import SearchRecord, User
from django.conf import settings
import datetime
import numpy as np

import requests
from business.utils import reply
from business.utils.paper_vdb_init import get_filtered_paper


def queryGLM(msg: str, history=None) -> str:
    '''
    对chatGLM3-6B发出一次单纯的询问
    '''
    openai.api_base = settings.REMOTE_CHATCHAT_GLM3_OPENAI_PATH
    openai.api_key = "empty"
    history.append({"role": "user", "content": msg})
    response = openai.ChatCompletion.create(
        model="chatglm3-6b",
        messages=history,
        stream=False
    )
    print("ChatGLM3-6B：", response.choices[0].message.content)
    history.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content


from django.views.decorators.http import require_http_methods
from business.models.paper import Paper


def query_with_vector(search_content: str) -> list[Paper]:
    '''
    本函数用于向量化检索
    '''
    file_query_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/knowledge_base/search_docs'
    english_search_content = queryGLM("请把这段话翻译为英文：" + search_content)
    data = {
        'query': english_search_content,
        'knowledge_base_name': 'ZJY'  # 这是最大的知识库
    }
    response = requests.post(file_query_url, json=data)
    ps = response.json().get('data')
    # 下来是把这堆数据转化为json
    '''
    ps的格式为
    [
        {
            "page_content":"六、实验设置 为验证我们提出的“变色龙”模型在攻击性，隐蔽性与动态性上是否如理论预期， 我们将在这一部分进行大量有说服力的对比实验与消融实验作为说明。 6.1 数据集与预处理 6.1.1 CUHK-SYSU 该数据集是由香港中文大学与中山大学开源的行人搜索数据集，主要从电影片段 和街拍中构造，共包含 17k 余张图像与 8k 余查询人物，我们选择其全部的训练集训练 我们的模型，并使用 Test50G(1 张 Query 图片对应 50 张 Gallery 图片)来评估我们的攻击 模型。",
            "metadata":{
                "source":"变色龙——行人搜索智能攻击方案.pdf",
                "id":"f9f4bad8-b627-4b29-90f2-6a1f2fef63a0"
                },
            "type":"Document",
            "id":"f9f4bad8-b627-4b29-90f2-6a1f2fef63a0",
            "score":0.940712571144104
        }
    ]
    不出意外，metadata里面的pdf应该是arxiv的名字，所以得根据这个来锁定他的url，然后确定是哪个paper实体
    '''
    ps.sort(key=lambda x: x.get('score'), reverse=True)
    filtered_paper = []
    for p in ps:
        paper_name = p.get('metadata').get('source')
        original_url = 'https://arxiv.org/abs/' + paper_name.spilt('/')[-1].replace('.pdf', '')
        print(original_url)
        p = Paper.objects.filter(original_url=original_url).first()
        if p is not None:
            filtered_paper.append(p)
    return filtered_paper


def search_papers_by_keywords(keywords):
    # 初始化查询条件，此时没有任何条件，查询将返回所有Paper对象
    query = Q()

    # 为每个关键词添加搜索条件
    for keyword in keywords:
        query |= Q(title__icontains=keyword) | Q(abstract__icontains=keyword)

    # 使用累积的查询条件执行查询
    result = Paper.objects.filter(query)
    filtered_paper_list = []
    for paper in result:
        filtered_paper_list.append(paper)
    return filtered_paper_list


@require_http_methods(["POST"])
def vector_query(request):
    """
    本函数用于处理向量化检索的请求，search_record含不存在则创建，存在（需传参数）则恢复两种情况
    此类检索不包含上下文信息，仅用当前提问对本地知识库检索即可
    :param Request: 请求，类型为GET
        内容包含：{
            "search_content": 检索关键词
        }
    :return: 返回一个json对象，其中为一个列表，列表中的每个元素为一个文献的信息
    {
        [
            {
                "paper_id": 文献id,
                "title": 文献标题,
                "authors": 作者,
                "abstract": 摘要,
                "time": 发布时间,
                "journal": 期刊,
                "ref_cnt": 引用次数,
                "original_url": 原文地址,
                "read_count": 阅读次数
            }
        ]
    }

    TODO:
        1. 从Request中获取user_id和search_content
        2. 将search_content存入数据库
        3. 使用向量检索从数据库中获取文献信息
        4. 返回文献信息
    """
    # 鉴权
    items = request.session.items()
    for key, value in items:
        print(f'{key}: {value}')

    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    request_data = json.loads(request.body)
    search_content = request_data.get('search_content')
    ai_reply = ""
    # filtered_paper = search_paper_with_query(search_content, limit=200) 从这里改为使用服务器的查询接口
    vector_filtered_papers = get_filtered_paper(search_content, 100, threshold=0.25)  # 这是新版的调用服务器模型的接口

    # 进行二次关键词检索
    # 首先获取关键词, 同样使用chatglm6b的普通对话
    chat_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/chat'
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "query": search_content,
        "prompt_name": "keyword",
        "temperature": 0.3
    })
    response = requests.request("POST", chat_chat_url, data=payload, headers=headers, stream=False)
    keyword = ""

    decoded_line = response.iter_lines().__next__().decode('utf-8')
    # print(decoded_line)
    if decoded_line.startswith('data'):
        data = json.loads(decoded_line.replace('data: ', ''))
        keyword += data['text']

    print(keyword)
    keywords = keyword.split(", ")  # ["aa", "bb"]
    not_keywords = ["paper", "research", "article"]
    for not_keyword in not_keywords:
        keywords = [keyword for keyword in keywords if not_keyword not in keyword]

    keyword_filtered_papers = search_papers_by_keywords(keywords=keywords)

    if len(keyword_filtered_papers) > 20:
        keyword_filtered_papers = keyword_filtered_papers[:20]

    keyword_filtered_papers.extend(vector_filtered_papers)  # Paper类的列表
    filtered_papers = keyword_filtered_papers
    start_year = min([paper.publication_date.year for paper in filtered_papers])
    end_year = max([paper.publication_date.year for paper in filtered_papers])
    # 发表数量最多的年份
    most_year = max(set([paper.publication_date.year for paper in filtered_papers]),
                    key=[paper.publication_date.year for paper in filtered_papers].count)

    cnt = len([1 for paper in filtered_papers if paper.publication_date.year == most_year])
    ai_reply += (f'根据您的需求，Epp论文助手检索到了【{len(filtered_papers)}】篇论文，其主要分布在【{start_year}】'
                 f'到【{end_year}】之间，其中【{most_year}】这一年的论文数量最多，有【{cnt}】篇论文,'
                 f'显示出近几年在该领域的研究活跃度较高。\n')
    # return reply.success({"keyword": keyword, 'papers': filtered_paper})

    # return reply.success({"data": "成功", "content": content})
    # 进行总结， 输入标题/摘要
    # papers_summary = f"关键词："
    # papers_summary = "下述论文与主题"
    # for keyword in keywords:
    #     papers_summary += keyword + "，"
    # papers_summary += "密切相关\n"
    papers_summary = ""
    for paper in filtered_papers[:20]:
        papers_summary += f'{paper.title}\n'
        # papers_summary += f'摘要为：{paper.abstract}\n'

    payload = json.dumps({
        "query": papers_summary,
        "prompt_name": "query_summary",
        "temperature": 0.3
    })

    response = requests.request("POST", chat_chat_url, data=payload, headers=headers, stream=False)
    if response.status_code == 200:
        lines = response.iter_lines()
        for line in lines:
            decoded_line = line.decode('utf-8')
            print(decoded_line)
            if decoded_line.startswith('data'):
                data = json.loads(decoded_line.replace('data: ', ''))
                ai_reply += data['text']
            print(f'ai_reply: {ai_reply}')
    else:
        return reply.fail(msg='检索总结失败，请检查网络并重新尝试')

    # 判断是创建检索/恢复检索
    search_record_id = request_data.get('search_record_id')
    if search_record_id is None:
        search_record = SearchRecord(user_id=user, keyword=search_content, conversation_path=None)
        search_record.save()
        conversation_path = os.path.join(settings.USER_SEARCH_CONSERVATION_PATH, str(search_record.search_record_id) + '.json')
        if os.path.exists(conversation_path):
            os.remove(conversation_path)
        with open(conversation_path, 'w') as f:
            json.dump({"conversation": []}, f, indent=4)
        search_record.conversation_path = conversation_path
        search_record.save()
    else:
        search_record = SearchRecord.objects.get(search_record_id=search_record_id)
        conversation_path = search_record.conversation_path

    # 处理历史记录部分, 无需向前端传递历史记录, 仅需对话文件中添加
    with open(conversation_path, 'r') as f:
        conversation_history = json.load(f)

    conversation_history = list(conversation_history.get('conversation'))
    conversation_history.extend([{
        "role": "user",
        "content": search_content
    }, {
        "role": "assistant",
        "content": ai_reply
    }])

    with open(conversation_path, 'w') as f:
        json.dump({"conversation": conversation_history}, f, indent=4)

    # 将paper转化为json
    filtered_papers_list = []
    for p in filtered_papers:
        filtered_papers_list.append(p.to_dict())

    return JsonResponse({"paper_infos": filtered_papers_list, 'ai_reply': ai_reply, 'keywords': keywords}, status=200)

@require_http_methods(["GET"])
def restore_search_record(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    search_record_id = request.GET.get('search_record_id')
    search_record = SearchRecord.objects.get(search_record_id=search_record_id)
    conversation_path = search_record.conversation_path
    with open(conversation_path, 'r') as f:
        conversation_history = json.load(f)

    return reply.success(conversation_history)
@require_http_methods(["GET"])
def get_user_search_history(request):
    username = request.session.get('username')
    if username is None:
        username = 'Ank'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")
    search_records = SearchRecord.objects.filter(user_id=user).order_by('-date')
    keywords = []
    for item in search_records:
        keywords.append(item.keyword)

    return reply.success({"keywords": list(set(keywords))[:10]})

@require_http_methods(["POST"])
def dialog_query(request):
    """
    本函数用于处理对话检索的请求
    :param Request: 请求，类型为POST
        内容包含：{
            message: string
            ,
            paper_ids:[
                string, //很多个paper_id
            ]
        }
        
    :return: 返回一个json对象，格式为：
    {
        dialog_type: 'dialog' or 'query',
        papers:[
            {//只有在dialog_type为'query'时才有，这时需要前端对文献卡片进行渲染。
                "paper_id": 文献id,
                "title": 文献标题,
                "authors": 作者,
                "abstract": 摘要,
                "publication_date": 发布时间,
                "journal": 期刊,
                "citation_count": 引用次数,
                "original_url": 原文地址,
                "read_count": 阅读次数
            },
        ],
        content: '回复内容'
    }
    
    TODO:
        1. 从Request中获取对话内容
        2. 根据最后一条user的对话回答进行关键词触发，分析属于哪种对话类型
            - 如果对话类型为'query'
                1. 使用向量检索从数据库中获取文献信息 5篇
                2. 将文献信息整理为json，作为papers属性
                3. 将文献信息进行整理作为content属性
            - 如果对话类型为'dialog'
                1. 大模型正常推理就可以了
        3. 把聊天记录存在本地
        4. 返回json对象,存入到数据库，见backend/business/models/search_record.py
    """
    import sys, os
    username = request.session.get('username')
    data = json.loads(request.body)
    message = data.get('message')
    keyword = data.get('keyword')
    paper_ids = data.get('paper_ids')
    user = User.objects.filter(username=username).first()
    if user is None:
        return JsonResponse({'error': '用户不存在'}, status=404)
    search_record = SearchRecord.objects.filter(user_id=user.user_id, keyword=keyword).first()
    if search_record is None:
        # 创建新的聊天记录
        search_record = SearchRecord.objects.create(user_id=user.user_id, keyword=keyword)
        search_record.conversation_path = settings.USER_SEARCH_CONSERVATION_PATH + '/' + search_record.search_record_id + '.json'
        search_record.date = datetime.datetime.now()
        search_record.save()
    # 历史记录的json文件名称和search_record_id一致
    conversation_path = settings.USER_SEARCH_CONSERVATION_PATH + '/' + search_record.search_record_id + '.json'
    history = []
    if os.path.exists(conversation_path):
        c = json.loads(open(conversation_path).read())
        history = c
    history.append({'role': 'user', 'content': message})
    # 先判断下是不是要查询论文
    prompt = '想象你是一个科研助手，帮我判断一下这段用户的需求是不是要求查找一些论文，你的回答只能是\"yes\"或者\"no\"，他的需求是：\n' + message + '\n'
    response_type = queryGLM(prompt)
    papers = []
    dialog_type = ''
    content = ''
    if 'yes' in response_type:  # 担心可能有句号等等
        # 查询论文，TODO:接入向量化检索
        filtered_paper = query_with_vector(message)
        dialog_type = 'query'
        papers = []
        for paper in filtered_paper:
            papers.append(paper.to_dict())
        content = '根据您的需求，我们检索到了如下的论文信息'
        for i in len(papers):
            content + '\n' + f'第{i}篇：'
            # TODO: 这里需要把papers的信息整理到content里面
            content += f'标题为：{papers[i].title}\n'
            content += f'摘要为：{papers[i].abstract}\n'
        history.append({'role': 'assistant', 'content': content})
    else:
        # 对话，保存3轮最多了，担心吃不下
        print(history.copy()[-5:])
        response = queryGLM(message, history.copy()[-5:])
        dialog_type = 'dialog'
        papers = []
        content = response
        history.append({'role': 'assistant', 'content': content})
    with open(conversation_path, 'w') as f:
        f.write(json.dumps(history))
    res = {
        'dialog_type': dialog_type,
        'papers': papers,
        'content': content
    }
    return JsonResponse(res, status=200)

@require_http_methods(["DELETE"])
def flush(request):
    '''
    这是用来清空对话记录的函数
    :param request: 请求，类型为GET
        内容包含：{
            keyword: string
        }
    '''
    username = request.session.get('username')
    data = json.loads(request.body)
    keyword = data.get('keyword')
    search_record = SearchRecord.objects.filter(user_id=username, keyword=keyword).first()
    if search_record is None:
        return JsonResponse({'error': '搜索记录不存在'}, status=404)
    else:
        conversation_path = search_record.conversation_path
        import os
        if os.path.exists(conversation_path):
            os.remove(conversation_path)
        HttpRequest('清空成功', status=200)
