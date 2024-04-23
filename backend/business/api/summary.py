'''
本文件主要用于文献综述生成，包括单篇文献的综述生成和多篇文献的综述生成
path : /api/summary/...
'''

from django.http import JsonResponse, HttpRequest
import openai, json
from business.models import User, paper
import threading

lock = threading.Lock()

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