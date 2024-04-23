from flask_cors import CORS

from vector_database.sci_bert_embedding import search_paper_with_query
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)

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

