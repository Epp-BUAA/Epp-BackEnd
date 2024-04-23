
import os
import random
import requests
import django


from tqdm import tqdm


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')

django.setup()
from business.models import Paper

PAPERS_PATH = 'F:\软工\paper_pdf'
papers = Paper.objects.all()
for paper in tqdm(papers):
    paper_name = paper.paper_id
    keyword = paper.title + '.' + paper.abstract
    paper_id = paper.paper_id
    # 将路径中的abs修改为pdf，最后加上.pdf后缀
    original_url = paper.original_url.replace('abs', 'pdf') + '.pdf'
    response = requests.get(original_url)
    if response.status_code == 200:
        filepath = os.path.join(PAPERS_PATH, str(paper_name) + '.pdf')
        with open(filepath, 'wb') as f:
            f.write(response.content)
