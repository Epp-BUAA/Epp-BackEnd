'''
本文件主要用于文献综述生成，包括单篇文献的综述生成和多篇文献的综述生成
path : /api/summary/...
'''

from django.http import JsonResponse, HttpRequest
import openai, json
from business.models import User, paper
import threading, requests
from business.utils.reply import fail, success
from django.conf import settings
from business.models import User, UserDocument, Paper, abstract_report
from django.views.decorators.http import require_http_methods
import os


##################################新建一个临时知识库，多问几次，然后通过一个模板生成综述#######################################

###################综述生成##########################

def quertGLM(msg: str, history=None) -> str:
    '''
    对chatGLM3-6B发出一次单纯的询问
    '''
    openai.api_base = f'http://{settings.REMOTE_CHATCHAT_GLM3_OPENAI_PATH}/v1'
    openai.api_key = "none"
    history.append({"role": "user", "content": msg})
    response = openai.ChatCompletion.create(
        model="chatglm3-6b",
        messages=history,
        stream=False
    )
    print("ChatGLM3-6B：", response.choices[0].message.content)
    history.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content
    
@require_http_methods(['POST'])
def generate_summary(request):
    '''
    生成综述
    '''
    try:
        data = json.loads(request.body)
        paper_ids = data.get('paper_id_list')
        username = request.session.get('username')
        if username is None:
            username = 'sanyuba'
        from business.models import SummaryReport, User
        user = User.objects.filter(username=username).first()
        report = SummaryReport.objects.create(user_id=user)
        report.title = '综述'+str(report.report_id)
        p = settings.USER_REPORTS_PATH + '/' + str(report.report_id) + '.md'
        report.local_path = p
        report.save()
        # download_dir = settings.CACHE_PATH + '/' + str(report.report_id)
        # os.makedirs(download_dir)
        # # 先下载文章
        # for paper_id in paper_ids:
        #     download_paper(paper_id, download_dir)
        # # 创建临时知识库
        # tmp_kb_id = create_tmp_knowledge_base(download_dir)
        # if tmp_kb_id is None:
        #     return fail('创建临时知识库失败')
        # 开始生成综述
        # keywords = ['现状', '问题', '方法', '结果', '结论', '展望']
        introduction = '' # 引言
        paper_content = [] # 每个论文一个标题，然后是内容
        conclusion = '' # 结论
        paper_conclusions = [] 
        paper_themes = []
        paper_situations = []
        # 先把每篇论文需要的信息生成好了
        for paper_id in paper_ids:
            p = Paper.objects.filter(document_id=paper_id).first()
            content_prompt = '将这篇论文的摘要以第三人称的方式复述一遍，摘要如下：\n' + p.abstract
            paper_content.append(quertGLM(content_prompt, []))
            content_prompt = '将这篇论文的题目转化为中文：\n' + p.title
            paper_themes.append(quertGLM(content_prompt, []))
            content_prompt = '将这篇论文的现状部分以第三人称的方式复述一遍：\n' + p.abstract
            paper_situations.append(quertGLM(content_prompt, []))
            content_prompt = '将这篇论文的结论和展望部分以第三人称的方式复述一遍：\n' + p.abstract
            paper_conclusions.append(quertGLM(content_prompt, []))
        # 生成引言
        introduction_prompt = '请根据以下信息生成综述的引言：\n'
        for i in range(len(paper_ids)):
            introduction_prompt += '第' + str(i+1) + '篇论文的题目是：' + paper_themes[i] + '\n'
            introduction_prompt += '第' + str(i+1) + '篇论文的现状部分是：' + paper_situations[i] + '\n'
        introduction = quertGLM(introduction_prompt, [])
        # 生成结论
        conclusion_prompt = '请根据以下信息生成综述的结论：\n'
        for i in range(len(paper_ids)):
            conclusion_prompt += '第' + str(i+1) + '篇论文的题目是：' + paper_themes[i] + '\n'
            conclusion_prompt += '第' + str(i+1) + '篇论文的结论部分是：' + paper_conclusions[i] + '\n'
        conclusion = quertGLM(conclusion_prompt, [])
        
        # 生成综述
        summary = '# 引言\n' + introduction + '\n'
        summary += '# 正文\n'
        for i in range(len(paper_ids)):
            summary += '## ' + paper_themes[i] + '\n'
            summary += paper_content[i] + '\n'
        summary += '# 结论\n' + conclusion + '\n'
        # 修改语病，更加通顺
        prompt = '这是一篇综述，请让他更加通顺：\n' + summary
        response = quertGLM(prompt, [])
        with open(report.report_path, 'w') as f:
            f.write(response)
            
        print(response)
        
        return JsonResponse({'message': "综述生成成功"}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'message': "综述生成失败"}, status=400)
    
    
##################################单篇摘要生成##############################

import os
import requests
from business.utils.download_paper import downloadPaper

def create_tmp_knowledge_base(dir : str) -> str:
    '''
    将cache中的所有文件全部上传到远端服务器，创建一个临时知识库
    '''
    # 上传到远端服务器, 创建新的临时知识库
    upload_temp_docs_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/knowledge_base/upload_temp_docs'
    payload = {}

    files = []
    import os
    # 遍历每个文件
    for root, dirs, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            files.append(('files', (file, open(file_path, 'rb'), 
                                    'application/vnd.openxmlformats-officedocument.presentationml.presentation')))
    response = requests.request("POST", upload_temp_docs_url, files=files)
    print(response)
    # 关闭文件，防止内存泄露
    for k, v in files:
        v[1].close()

    if response.status_code == 200:
        tmp_kb_id = response.json()['data']['id']
        return tmp_kb_id
    else:
        return None
    
def ask_ai_single_paper(payload):
    file_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/file_chat'
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", file_chat_url, data=payload, headers=headers, stream=False)
    ai_reply = ""
    origin_docs = []
    print(response)
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith('data'):
                data = decoded_line.replace('data: ', '')
                data = json.loads(data)
                ai_reply += data["answer"]
                for doc in data["docs"]:
                    doc = str(doc).replace("\n", " ").replace("<span style='color:red'>", "").replace("</span>", "")
                    origin_docs.append(doc)
    return ai_reply, origin_docs
    
    
def create_abstract_report(request):
    request_data = json.loads(request.body)
    document_id = request_data.get("document_id")
    paper_id = request_data.get("paper_id")
    username = request.session.get('username')
    print(paper_id)
    if username is None:
        username = 'sanyuba'
    print(username)
    user = User.objects.filter(username=username).first()
    if user is None:
        return fail(msg="请先正确登录")
    if len(document_id) != 0:
        document = UserDocument.objects.get(document_id=document_id)
        # 获取服务器本地的path
        local_path = document.local_path
        content_type = document.format
        title = document.title
    elif len(paper_id) != 0:
        p = Paper.objects.filter(paper_id=paper_id).first()
        pdf_url = p.original_url.replace('abs/','pdf/') + '.pdf'
        local_path = settings.PAPERS_URL  + str(p.paper_id) + '.pdf'
        print(local_path)
        print(pdf_url)
        if os.path.exists(local_path) == False:
            # 下载下来
            downloadPaper(url=pdf_url, filename=str(p.paper_id))
        content_type = '.pdf'
        title = p.title
    print('下载完毕')

    from business.models.abstract_report import AbstractReport
    report_path = os.path.join(settings.USER_REPORTS_PATH, title + '.md')
    if os.path.exists(report_path):
        content = open(report_path, 'r').read()
        print(content)
        return success({'summary': content}, msg="生成摘要成功")
    ar = AbstractReport.objects.create(file_local_path=local_path, report_path=report_path)
    ar.save()
    # 上传到远端服务器, 创建新的临时知识库
    upload_temp_docs_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/knowledge_base/upload_temp_docs'
    payload = {}
    local_path = local_path[1:] if local_path.startswith('/') else local_path
    print(local_path)
    files = [
        ('files', (title + content_type, open(local_path, 'rb'),
                   'application/vnd.openxmlformats-officedocument.presentationml.presentation'))
    ]
    response = requests.post(upload_temp_docs_url, files=files)

    # 关闭文件，防止内存泄露
    for k, v in files:
        v[1].close()
    if response.status_code != 200:
        return fail(msg="连接模型服务器失败")
    tmp_kb_id = response.json()['data']['id']
    summary = ""
    # 开始生成摘要
    ## 现状，解决问题，解决方法，实验结果，结论
    summary += '# 摘要报告\n'
    
    from business.api.paper_interpret import do_file_chat
    
    #### 研究现状
    
    query_current_situation = '请讲述研究现状部分\n'
    payload_cur_situation = json.dumps({
        "query": query_current_situation,
        "knowledge_id": tmp_kb_id,
        "prompt_name": "default"  # 使用普通对话模式
    })
    response_current_situation,_ = ask_ai_single_paper(payload=payload_cur_situation)
    print(_)
    summary += '## 研究现状\n' + response_current_situation + '\n'
    
    #### 解决问题
    
    query_problem = '请讲讲这篇论文解决的问题\n'
    payload_problem = json.dumps({
        "query": query_problem,
        "knowledge_id": tmp_kb_id,
        "prompt_name": "default",  # 使用普通对话模式
        "score_threshold" : 0.1
    })
    response_problem,_ = ask_ai_single_paper(payload=payload_problem)
    print(_)
    summary += '## 解决问题\n' + response_problem + '\n'
    
    #### 解决方法
    
    query_solution = '请讲讲这篇论文提出的解决方法\n'
    payload_solution = json.dumps({
        "query": query_problem,
        "knowledge_id": tmp_kb_id,
        "prompt_name": "default"  # 使用普通对话模式
    })
    response_solution,_ = ask_ai_single_paper(payload=payload_solution)
    print(_)
    summary += '## 解决方法\n' + response_solution + '\n'
    
    #### 实验结果
    
    query_result = '请讲讲这篇论文实验得到的结果\n'
    payload_res = json.dumps({
        "query": query_result,
        "knowledge_id": tmp_kb_id,
        "prompt_name": "default"  # 使用普通对话模式
    })
    response_result,_ = ask_ai_single_paper(payload=payload_res)
    print(_)
    summary += '## 实验结果\n' + response_result + '\n'
    
    #### 结论
    
    query_conclusion = '请讲讲这篇论文得出的结论\n'
    payload_conclusion = json.dumps({
        "query": query_conclusion,
        "knowledge_id": tmp_kb_id,
        "prompt_name": "default"  # 使用普通对话模式
    })
    response_conclusion,_ = ask_ai_single_paper(payload=payload_conclusion)
    print(_)
    summary += '## 结论\n' + response_conclusion + '\n'
    
    
    # 修改语病，更加通顺
    print(summary)
    
    prompt = '这是一篇摘要，请让他更加通顺：\n' + summary
    response = quertGLM(prompt, [])
    print(response)
    with open(report_path, 'w') as f:
        f.write(response)
        
    return success({'summary': response}, msg="生成摘要成功")
    