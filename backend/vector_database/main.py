import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')
django.setup()
from flask_cors import CORS

from models import UserDocument, FileReading
from vector_database.sci_bert_embedding import search_paper_with_query
from flask import Flask, request, jsonify
from django.conf import settings
app = Flask(__name__)
CORS(app)


@app.route('/api/do_paper_study', methods=['GET'])
def do_paper_study():
    file_reading_id = request.json['file_reading_id']
    file_reading = FileReading.objects.get(id=file_reading_id)

    # conversation_path = file.conversation_path
    #     with open(conversation_path, 'r') as f:
    #         conversation = json.load(f)
    # conversation.append({'role': 'user', 'content': question})

@app.route('/api/create_paper_study', methods=['POST'])
def create_paper_study():
    # 获取用户名
    # username = request.session.get('username')
    # user = User.objects.get(username=username)

    document_id = request.json['document_id']
    # 获取url
    url = UserDocument.objects.get(document_id=document_id).url
    print(url)
    # 将url读取后发送给远端服务器
    document = ...
    # 创建一段新的filereading对话
    file_reading = FileReading(user_id="063eccd476b3475584c0eef9baf16c04", document_id=document_id, title="论文研读",
                               conversation_path=None)
    file_reading.save()

    return jsonify({"file_reading_id": file_reading.id, "code": 200}), 200


@app.route('/api/search/vectorQuery', methods=['GET'])
def search_paper():
    text = request.args.get('search_content')
    print(text)
    if text is None:
        return jsonify({"message": "Text is None!", "code": 400}), 400
    # insert_paper_info_2_vector_database()
    filtered_paper = search_paper_with_query(text)
    filtered_paper_list = []
    for paper in filtered_paper:
        filtered_paper_list.append(paper.to_dict())
    print(filtered_paper_list)

    return jsonify({"paper_infos": filtered_paper_list, "code": 200}), 200


# 返回字典 1: {}
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

