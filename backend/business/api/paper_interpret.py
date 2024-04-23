'''
本文件的功能是文献阅读助手，给定一篇文章进行阅读，根据问题的答案进行回答。
API格式如下：
api/peper_interpret/...
'''
import json, openai
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from backend.business.models import paper, file_reading, User
import PyPDF2
from backend.settings import USER_READ_CONSERVATION_PATH, MAX_Similarity
from PyPDF2 import PdfReader


class Paper(object):

    def __init__(self, paper_path) -> None:
        self.pdf_path = paper_path
        self.pdf_obj = PdfReader(paper_path)
        self.paper_meta = self.pdf_obj.metadata
        self.catelogue = None
        self.text = ''
        for page in self.pdf_obj.pages:
            txt = page.extract_text()
            self.text += txt

        self.paper_parts = None
        self.paper_summaries = [('PaperMeta', str(self.paper_meta))]

    def has_catelogue(self):
        return self.catelogue is not None

    def set_catelogue(self, catelogue_list):
        self.catelogue = catelogue_list

    def iter_pages(self, iter_text_len: int = 3000):
        page_idx = 0
        for page in self.pdf_obj.pages:
            txt = page.extract_text()
            for i in range((len(txt) // iter_text_len) + 1):
                yield page_idx, i, txt[i * iter_text_len:(i + 1) * iter_text_len]
            page_idx += 1

    def split_paper_by_titles(self):

        if self.catelogue is None:
            raise RuntimeError('catelogue is None, not initialized')

        text_str = self.text
        titles = self.catelogue
        title_positions = []
        for title in titles:
            position = text_str.find(title)
            if position != -1:
                title_positions.append((position, title))

        title_positions.sort()

        paper_parts = []
        for i, (position, title) in enumerate(title_positions):
            start_pos = position
            end_pos = title_positions[i+1][0] if i < len(title_positions) - 1 else len(text_str)
            paper_part = text_str[start_pos:end_pos].strip()
            paper_parts.append((title, paper_part))

        self.paper_parts = paper_parts
    

def get_pdf_title(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        page = reader.getPage(0)
        title = page.extractText().split('\n')[0]
        return title

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


@require_http_methods(["POST"])
def paper_interpret(request):
    '''
    本文件唯一的接口，类型为POST
    根据用户的问题，返回一个回答
    思路如下：
        1. 根据session获得用户的username, request中包含local_path和question
        2. 根据paper_id得到向量库中各段落的向量，根据question得到问题的向量，选择最相似的段落
        3. 将段落输入到ChatGLM2-6B中，得到回答，进行总结，给出一个本文中的回答
        4. 查找与其相似度最高的几篇文章的段落，相似度最高的5个段落，对每段给出一个简单的总结。
        5. 将几个总结和回答拼接返回
        6. 把聊天记录保存到数据库中，见backend/business/models/file_reading.py
    return : {
        content: str
    }
    '''
    if request.method == 'POST':
        data = json.loads(request.body)
        local_path = data['local_path']
        question = data['question']
        username = request.session.get('username')
        user = User.objects.get(username=username)
        file = file_reading.objects.get(user_id=user, file_local_path=local_path)
        conversation = []
        conversation_path = ''
        if file is None:
            # 新建一个研读记录
            t = get_pdf_title(local_path)
            file = file_reading(user_id=user, file_local_path=local_path, title=t, conversation_path=None)
            file.conversation_path = f'{USER_READ_CONSERVATION_PATH}/{file.user_id.id}_{file.title}.txt'
            conversation_path = file.conversation_path
            file.save()
        else:
            conversation_path = file.conversation_path
            with open(conversation_path, 'r') as f:
                conversation = json.load(f)
        conversation.append({'role': 'user', 'content': question})
        # 从数据库中找到最相似的段落