import json

import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, MilvusClient, Milvus, utility
_DIMENSION = 768      # 向量维度
CLUSTER_ENDPOINT="https://in01-525bfa666c9e9de.tc-ap-beijing.vectordb.zilliz.com.cn:443" # Set your cluster endpoint
TOKEN="de81326d1e4d53a6b27804821e986536a2b67575f44e068413b6cf2e1da17e4f6d5a73a6d9e0dfd2a6be151e42136e025fdb6b3d" # Set your token

def init_milvus(COLLECTION_NAME):
    connections.connect(
      alias='default',
      #  Public endpoint obtained from Zilliz Cloud
      uri=CLUSTER_ENDPOINT,
      # API key or a colon-separated cluster username and password
      token=TOKEN
    )

    def _check_collection_exists(collection_name):
        return collection_name in utility.list_collections()

    def _get_existing_collection(collection_name):
        if _check_collection_exists(collection_name):
            # 获取集合
            return Collection(name=collection_name)
        else:
            print(f"Collection '{collection_name}' does not exist.")
            return None

    collection = _get_existing_collection(COLLECTION_NAME)
    if collection:
        print(f"Successfully retrieved collection: {collection.name}")
        return collection
    else:
        print("Failed to retrieve collection.")
        return collection

# 创建新的收集
def create_new_collection_or_get_collection(collection_name):
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="title_vector", dtype=DataType.FLOAT_VECTOR, dim=768),
        FieldSchema(name="link", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="reading_time", dtype=DataType.INT64),
        FieldSchema(name="publication", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="claps", dtype=DataType.INT64),
        FieldSchema(name="responses", dtype=DataType.INT64)
    ]

    # 2. Build the schema*
    schema = CollectionSchema(
        fields,
        description="Schema of Medium articles",
        enable_dynamic_field=True
    )

    # 3. Create collection*
    collection = Collection(
        name=COLLECTION_NAME,
        description="Medium articles published between Jan and August in 2020 in prominent publications",
        schema=schema
    )

    # index_params = {
    #     "index_type": "AUTOINDEX",
    #     "metric_type": "L2",
    #     "params": {}
    # }
    #
    # # To name the index, do as follows:
    # collection.create_index(
    #     field_name="title_vector",
    #     index_params=index_params,
    #     index_name='title_vector_index'  # Optional
    # )

    return collection

def milvus_insert(collection, rows):
    # [{"vector": xx, "normal_id": xx}, {}]
    # print(rows)
    res = collection.insert(data=rows)
    collection.flush()
    print(res)

def milvus_search(collection, vector, limit):
    """
    向量检索
    :param collection:
    :param partition_name: 检索指定分区的向量
    :return:
    """
    # 将collection加载到内存，必须先加载到内存，然后才能检索
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
    # 向量搜索
    results = collection.search(
        data=[vector],  # Query, 支持多个Query一起检索
        anns_field="vector",  # 向量检索域
        param=search_params,
        output_fields=["normal_id"],  # 返回域
        limit=limit
    )
    return results

# collections = create_new_collection()
DATASET_PATH= "doc/test.json"  # Set your dataset path

# 6. Prepare data

# Prepare a list of rows
# with open(DATASET_PATH) as f:
#     data = json.load(f)
#     rows = data['rows']
# # for row in rows:
# #     del row['id']
# #     # print(row)
# collections = init_milvus("SE2024")
# row = [{"normal_id": "aaaaaaaaaaaaaa", "vector": rows[0]['title_vector']}]
# print(row)
# res = milvus_insert(collections, row)
# print(res)
# search(collections, rows[0]['title_vector'],5)