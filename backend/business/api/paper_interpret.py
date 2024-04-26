'''
本文件的功能是文献阅读助手，给定一篇文章进行阅读，根据问题的答案进行回答。
API格式如下：
api/peper_interpret/...
'''
import json, openai
import os
from urllib.parse import quote
import requests
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from business.models import paper, file_reading, User
import PyPDF2
from PyPDF2 import PdfReader
from django.conf import settings
from business.models import UserDocument, FileReading
from business.utils import reply

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


# 论文研读模块

'''
    创建文献研读对话：
        上传一个文件，开启一个研读对话，返回 tmp_kb_id
    
    对话记录方式为: [
        {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
        {"role": "assistant", "content": "虎头虎脑"},
    ]
'''


def create_content_disposition(filename):
    """构建适用于Content-Disposition的filename和filename*参数"""
    # URL 编码文件名
    safe_filename = quote(filename)
    # 构建Content-Disposition头部
    disposition = f'form-data; name="file"; filename="{filename}"; filename*=UTF-8\'\'{safe_filename}'
    return disposition


@require_http_methods(["POST"])
def create_paper_study(request):
    request_data = json.loads(request.body)
    document_id = request_data.get("document_id")
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    print(username)
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    # 获取文件, 后续支持直接对8k篇论文进行检索
    document = UserDocument.objects.get(document_id=document_id)
    # 获取服务器本地的path
    local_path = document.local_path
    content_type = document.format
    title = document.title
    print(url)

    # 创建一段新的filereading对话, 并设置conversation对话路径，创建json文件
    file_reading = FileReading(user_id=user, document_id=document, title="论文研读",
                               conversation_path=None)
    file_reading.save()
    conversation_path = os.path.join(settings.USER_READ_CONSERVATION_PATH, str(file_reading.id) + ".json")
    file_reading.conversation_path = conversation_path
    file_reading.save()
    if os.path.exists(conversation_path):
        os.remove(conversation_path)
    with open(conversation_path, 'w') as f:
        json.dump({"conversation": []}, f, indent=4)

    # 上传到远端服务器, 创建新的临时知识库
    upload_temp_docs_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/knowledge_base/upload_temp_docs'
    payload = {}

    # 后续可支持多文件，多类型
    with open(local_path, 'rb') as f:
        print(f.__sizeof__())

    print(create_content_disposition(title + content_type))
    files = [
        ('files', (title + content_type, open(local_path, 'rb'),
                   'application/vnd.openxmlformats-officedocument.presentationml.presentation'))
    ]

    # headers = {
    #     'Content-Type': 'multipart/form-data'
    # }

    response = requests.request("POST", upload_temp_docs_url, files=files)
    print(response)
    # 关闭文件，防止内存泄露
    for k, v in files:
        v[1].close()

    if response.status_code == 200:
        tmp_kb_id = response.json()['data']['id']
        return reply.success({'tmp_kb_id': tmp_kb_id, 'file_reading_id': file_reading.id}, msg="开启文献研读对话成功")
    else:
        return reply.fail(msg="连接模型服务器失败")


'''
    恢复文献研读对话：
        传入文献研读对话id
'''


@require_http_methods(["POST"])
def restore_paper_study(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    # 获取filereading与文件路径，重新上传给服务器开启对话
    request_data = json.loads(request.body)
    file_reading_id = request_data.get('file_reading_id')
    fr = FileReading.objects.get(id=file_reading_id)
    document = UserDocument.objects.get(document_id=fr.document_id)

    # 上传到远端服务器, 创建新的临时知识库
    upload_temp_docs_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/knowledge_base/upload_temp_docs'
    files = {
        'files': [
            (document.title, open(document.local_path, 'rb')),
        ]
    }
    response = requests.post(upload_temp_docs_url, files=files)

    # 关闭文件，防止内存泄露
    for file_tuple in files['files']:
        file_tuple[1].close()

    # 返回结果, 需要将历史对话一起返回
    if response.status_code == 200:
        tmp_kb_id = response.json()['data']['id']

        # 若删除过历史对话, 则再创建一个文件
        if not os.path.exists(fr.conversation_path):
            with open(fr.conversation_path, 'w') as f:
                json.dump({"conversation": []}, f, indent=4)

        # 读取历史对话记录
        with open(fr.conversation_path, 'r') as f:
            conversation_history = json.load(f)  # 使用 json.load() 方法将 JSON 数据转换为字典

        return reply.success(
            {'tmp_kb_id': tmp_kb_id, 'file_reading_id': file_reading_id, 'conversation_history': conversation_history},
            msg="恢复文献研读对话成功")
    else:
        return reply.fail(msg="连接模型服务器失败")


'''
    论文研读
'''


@require_http_methods(["POST"])
def do_paper_study(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    request_data = json.loads(request.body)
    tmp_kb_id = request_data.get('tmp_kb_id')  # 临时知识库id
    query = request_data.get('query')  # 本次询问对话
    file_reading_id = request_data.get('file_reading_id')
    fr = FileReading.objects.get(id=file_reading_id)

    # 加载历史记录
    with open(fr.conversation_path, 'r') as f:
        conversation_history = json.load(f)

    conversation_history = conversation_history.get('conversation')  # List[Dict]
    print(conversation_history)
    # 将历史记录与本次对话发送给服务器, 获取对话结果
    file_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/file_chat'
    if len(conversation_history) != 0:
        # 有问题
        payload = json.dumps({
            "query": query,
            "knowledge_id": tmp_kb_id,
            "prompt_name": "with_history"  # 使用历史记录对话模式
        })
        headers = {
            'Content-Type': 'application/json'
        }
    else:
        payload = json.dumps({
            "query": query,
            "knowledge_id": tmp_kb_id,
            "prompt_name": "default"  # 使用历史记录对话模式
        })
        print(payload)
        headers = {
            'Content-Type': 'application/json'
        }
    response = requests.request("POST", file_chat_url, data=payload, headers=headers, stream=True)
    client_id = None
    ai_reply = ""
    origin_docs = []
    try:
        for line in response.iter_lines():

            if line:
                decoded_line = line.decode('utf-8')

                if decoded_line.startswith('id'):
                    client_id = decoded_line.replace('id: ', '')
                elif decoded_line.startswith('data'):
                    data = decoded_line.replace('data: ', '')
                    data = json.loads(data)
                    print(data["answer"])
                    print(data["docs"])
                    ai_reply += data["answer"]
                    for doc in data["docs"]:
                        doc = str(doc).replace("\n", " ")
                        origin_docs.append(doc)

                    # print(f"Received data (Client ID {client_id}): {data}")
                elif decoded_line.startswith('event'):
                    event_type = decoded_line.replace('event: ', '')
                    # print(f"Event type: {event_type}")
    finally:
        response.close()
    # print(response)  # 目前不清楚是何种返回 TODO:
    return reply.success({"ai_reply": ai_reply, "docs": origin_docs}, msg="成功")
