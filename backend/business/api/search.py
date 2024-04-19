'''
本文件主要处理搜索功能，包括向量化检索和对话检索
API格式如下：
api/serach/...
'''
import json, openai
from django.http import JsonResponse, HttpRequest
from backend.business.models.search_record import SearchRecord, User
from django.conf import settings
import datetime

server_ip = '172.17.62.88'
url = f'http://{server_ip}:8000'

def queryGLM(msg : str, history=None) -> str:
    '''
    对chatGLM2-6B发出一次单纯的询问
    '''
    openai.api_base = f'http://{server_ip}:8000/v1'
    openai.api_key = "none"
    history.append({"role": "user", "content": msg})
    response = openai.ChatCompletion.create(
        model="chatglm2-6b",
        messages=history,
        stream=False
    )
    print("ChatGLM2-6B：", response.choices[0].message.content)
    history.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content
    

from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def vector_query(Request):
    """
    本函数用于处理向量化检索的请求
    :param Request: 请求，类型为GET
        内容包含：{
            "user_id": 用户id,
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
    pass

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
    history.append({ 'role' : 'user', 'content' : message })
    # 先判断下是不是要查询论文
    prompt = '想象你是一个科研助手，帮我判断一下这段用户的需求是不是要求查找一些论文，你的回答只能是\"yes\"或者\"no\"，他的需求是：\n' + message + '\n'
    response_type = queryGLM(prompt)
    papers = []
    dialog_type = ''
    content = ''
    if 'yes' in response_type: # 担心可能有句号等等
        # 查询论文，TODO:接入向量化检索
        dialog_type = 'query'
        papers = []
        content = '根据您的需求，我们检索到了如下的论文信息'
        for i in len(papers):
            content + '\n' + f'第{i}篇：'
            # TODO: 这里需要把papers的信息整理到content里面
        history.append({ 'role' : 'assistant', 'content' : content })
    else:
        # 对话，保存3轮最多了，担心吃不下
        print(history.copy()[-5:])
        response = queryGLM(message, history.copy()[-5:])
        dialog_type = 'dialog'
        papers = []
        content = response
        history.append({ 'role' : 'assistant', 'content' : content })
    with open(conversation_path, 'w') as f:
        f.write(json.dumps(history))
    res = {
        'dialog_type' : dialog_type,
        'papers' : papers,
        'content' : content
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