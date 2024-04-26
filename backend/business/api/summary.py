'''
本文件主要用于文献综述生成，包括单篇文献的综述生成和多篇文献的综述生成
path : /api/summary/...
'''

from django.http import JsonResponse, HttpRequest
import openai, json
from business.models import User, paper
import threading, requests
from utils.reply import fail, success
from django.conf import settings
from business.models import User, UserDocument, Paper
from django.views.decorators.http import require_http_methods
import os


##################################新建一个临时知识库，多问几次，然后通过一个模板生成综述#######################################

###################综述生成##########################

def quertGLM(msg: str, history=None) -> str:
    '''
    对chatGLM2-6B发出一次单纯的询问
    '''
    openai.api_base = f'http://{settings.REMOTE_MODEL_BASE_PATH}/v1'
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
        with open(report.report_path, 'w') as f:
            f.write(summary)
        
        return JsonResponse({'message': "综述生成成功"}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'message': "综述生成失败"}, status=400)
    
    
##################################单篇摘要生成##############################

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