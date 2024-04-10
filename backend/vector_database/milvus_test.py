import json

import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, MilvusClient

_DIMENSION = 768      # 向量维度
CLUSTER_ENDPOINT="https://in01-525bfa666c9e9de.tc-ap-beijing.vectordb.zilliz.com.cn:443" # Set your cluster endpoint
TOKEN="de81326d1e4d53a6b27804821e986536a2b67575f44e068413b6cf2e1da17e4f6d5a73a6d9e0dfd2a6be151e42136e025fdb6b3d" # Set your token
COLLECTION_NAME="se2024"
DATASET_PATH="doc/test.json" # Set your dataset path
connections.connect(
  alias='default',
  #  Public endpoint obtained from Zilliz Cloud
  uri=CLUSTER_ENDPOINT,
  # API key or a colon-separated cluster username and password
  token=TOKEN,
)

collection = Collection(name=COLLECTION_NAME)

print(collection.num_entities)
with open(DATASET_PATH) as f:
    data = json.load(f)
    rows = data['rows']

rows[0]['title'] = "这是一个测试文章"
insert_data = rows[0]
# 插入数据, 应无id字段, 否则会出现重复id
def insert_vector(row):
    print(row)
    res = collection.insert(data=row)
    collection.flush()
    print(res)
def search(limit):
    """
    向量检索
    :param collection:
    :param partition_name: 检索指定分区的向量
    :return:
    """
    # 将collection加载到内存，必须先加载到内存，然后才能检索
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    # 向量搜索
    results = collection.search(
        data=[data["rows"][0]['title_vector']],
        anns_field="title_vector",
        param=search_params,
        output_fields=["title", "link"],
        limit=limit
    )
    print(results)

# insert_vector(insert_data)
search(5)