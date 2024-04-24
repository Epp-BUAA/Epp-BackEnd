'''
本文件主要用于文献综述生成，包括单篇文献的综述生成和多篇文献的综述生成
path : /api/summary/...
'''

from django.http import JsonResponse, HttpRequest
import openai, json
from business.models import User, paper
import threading

lock = threading.Lock()

openai.api_base = "https://api.moonshot.cn/v1"
openai.api_key = 'sk-yXyyuuFBxj3m8v0baMatcFATSB0XxjJYInNMOr5lPKGDyPAA'

def query_Kimi(user_input, history=None):
    if history is None:
        history.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="moonshot-v1-8k",
        messages=history,
        stream=False
    )
    print(response.choices[0].message.content)
    if history is not None:
        history.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content
    
def paper_summary(request):
    '''
    本文件唯一的接口，类型为POST
    根据用户的问题，返回一个回答
    思路如下：
        1. 根据session获得用户的username, request中包含paper_ids
        2. 直接生成综述
    return : {
        summary: str
    }
    '''
    data = json.loads(request.body)
    paper_ids = data.get('paper_ids')
    if type(paper_ids) != list:
        return JsonResponse({"summary": "参数错误"})
    username = request.session.get('username')
    user = User.objects.get(username=username)
    from business.models import paper, summary_report
    import openai
    openai.api_base = "https://api.sanyue.site/v1"
    openai.api_key = 'sk-RHa0NhwUiZCPu4vt06A0368e10624e348233D60aB799Bc11'


def single_paper_summary(request):
    '''
    单篇摘要生成，存到user_document表中
    api/study/singlepapersummary
    '''
    data = json.loads(request.body)
    document_id = data.get('document_id')
    username = request.session.get('username')
    user = User.objects.get(username=username)
    from business.models import UserDocument
    document = UserDocument.objects.get(document_id=document_id)
    if document is None:
        return JsonResponse({"summary": "参数错误"})
    if document.summary is not None:
        return JsonResponse({"summary": document.summary})
    else:
        from pathlib import Path
        from openai import OpenAI
        client = OpenAI(
            api_key="MOONSHOT_API_KEY",
            base_url="https://api.moonshot.cn/v1",
        )
        file_object = client.files.create(file=Path(document.local_path), purpose="file-extract")
        
        # 获取结果
        # file_content = client.files.retrieve_content(file_id=file_object.id)
        # 注意，之前 retrieve_content api 在最新版本标记了 warning, 可以用下面这行代替
        # 如果是旧版本，可以用 retrieve_content
        file_content = client.files.content(file_id=file_object.id).text
        
        # 把它放进请求中
        messages=[
            {
                "role": "system",
                "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
            },
            {
                "role": "system",
                "content": file_content,
            },
            {"role": "user", "content": f'请简单介绍 {document.title}.pdf 讲了啥'},
        ]
        
        # 然后调用 chat-completion, 获取 kimi 的回答
        completion = client.chat.completions.create(
            model="moonshot-v1-32k",
            messages=messages,
            temperature=0.3,
        )
        
        print(completion.choices[0].message)
        summary = completion.choices[0].message
        # 删除文件
        client.files.delete(file_id=file_object.id)
        document.summary = summary
        document.save()
        return JsonResponse({"summary": summary})
    
    