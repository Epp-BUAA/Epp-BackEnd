'''
本文件的功能是文献阅读助手，给定一篇文章进行阅读，根据问题的答案进行回答。
API格式如下：
api/peper_interpret/...
'''
import json, openai
from django.http import JsonResponse, HttpRequest

server_ip = '172.17.62.88'
url = f'http://{server_ip}:8000'


def queryGLM(msg: str, history=None) -> str:
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


def paper_interpret(request):
    '''
    本文件唯一的接口，类型为POST
    根据用户的问题，返回一个回答
    思路如下：
        1. 根据session获得用户的username, request中包含paper_id和question
        2. 根据paper_id得到向量库中各段落的向量，根据question得到问题的向量，选择最相似的段落
        3. 将段落输入到ChatGLM2-6B中，得到回答，进行总结，给出一个本文中的回答
        4. 查找与其相似度最高的几篇文章的段落，相似度最高的5个段落，对每段给出一个简单的总结。
        5. 将几个总结和回答拼接返回
        6. 把聊天记录保存到数据库中，见backend/business/models/file_reading.py
        
    return : {
        content: str
    }
    '''
