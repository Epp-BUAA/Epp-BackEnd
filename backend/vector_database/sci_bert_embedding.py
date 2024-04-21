import os
import django

from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm

from backend.vector_database.chatglm_translate import translate_zh2en
from backend.vector_database.milvus_test import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()
from business.models import Paper
model_dir = "sci_bert"

def get_sci_bert():
    model = AutoModel.from_pretrained(model_dir)
    print(f'Model loaded from {model_dir} OK!')
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    print(f'Tokenizer loaded from {model_dir} OK!')

    if torch.cuda.is_available():
        device = torch.device("cuda")  # 使用 CUDA
        model.to(device)  # 将模型移动到 GPU
    else:
        device = torch.device("cpu")  # 仅使用 CPU
        print("CUDA is not available. Using CPU instead.")
    return tokenizer, model


def text_embedding(text, tokenizer, model):
    # 使用分词器编码文本
    inputs = tokenizer(text, return_tensors="pt")
    # print(inputs)
    for k, _ in inputs.items():
        inputs[k] = inputs[k].cuda()
    # 3. 获取词嵌入
    # 传入编码后的文本到模型，得到输出
    outputs = model(**inputs)

    # 输出的 `outputs` 是一个包含多个层的输出的元组，我们通常使用最后一层的隐藏状态
    last_hidden_states = outputs.last_hidden_state

    # last_hidden_states 的形状是 [batch_size, sequence_length, hidden_size]
    # 这里 batch_size=1, sequence_length 是输入文本的长度（包括特殊字符）

    # print("Shape of output embeddings:", last_hidden_states.shape)
    # print("Output tensor:", last_hidden_states)

    # 4. (可选) 使用输出
    # 例如，你可以取第一个 token (通常是 [CLS] token) 的嵌入来做文本分类任务
    # cls_embedding = last_hidden_states[:, 0, :]
    cls_embedding = last_hidden_states[0, 0, :]
    # print("CLS token embedding:", cls_embedding)
    return cls_embedding

# django的增删改查
# 增
def create_paper():
    new_paper = Paper(title='New Research', author='John Doe')
    new_paper.save()


# 删一个
def delete_paper(paper_id):
    paper = Paper.objects.get(id=paper_id)
    paper.delete()


# 删多个
def delete_papers_by_author():
    Paper.objects.filter(author='John Doe').delete()


# 改
def update_paper(paper_id):
    paper = Paper.objects.get(id=paper_id)
    paper.title = 'Updated Title'
    paper.save()


def update_papers_by_author():
    Paper.objects.filter(author='John Doe').update(title='Uniform Title')


# 查
def get_paper_by_id(paper_id):
    try:
        paper = Paper.objects.get(id=paper_id)
        print(paper.title)
    except Paper.DoesNotExist:
        print("Paper not found.")


# 获取所有 John Doe 的论文
def get_papers_by_author():
    papers = Paper.objects.filter(author='John Doe')
    for paper in papers:
        print(paper.title)

# 获取除了 John Doe 之外的所有论文
def get_papers_exclude_author():
    papers = Paper.objects.exclude(author='John Doe')
    for paper in papers:
        print(paper.title)


def search_paper_with_query(text, limit=20):
    t, m = get_sci_bert()
    collection = init_milvus("SE2024")
    text = translate_zh2en(text)  # 任意语言到英文翻译
    print(text)
    query_embedding = text_embedding(text, t, m).cpu().detach().numpy()
    search_results = milvus_search(collection, query_embedding, limit)
    entities = [x.entity.to_dict() for x in search_results[0]]
    ids = [i['entity']['normal_id'] for i in entities]
    filtered_paper = Paper.objects.filter(paper_id__in=ids)
    # for paper in filtered_paper:
    #     print(paper.title)
    return filtered_paper


def get_all_paper():
    papers = Paper.objects.all()
    for paper in papers:
        keyword = paper.title + '.' + paper.abstract
        paper_id = paper.paper_id
        yield keyword, paper_id

def insert_paper_info_2_vector_database():
    t, m = get_sci_bert()
    collection = init_milvus("SE2024")
    infos = []
    for keyword, paper_id in tqdm(get_all_paper()):
        embedding = text_embedding(keyword, t, m).cpu().detach().numpy()
        infos.append({
            'vector': embedding.astype(np.float32),
            'normal_id': str(paper_id)
        })
        torch.cuda.empty_cache()
    milvus_insert(collection, infos)

