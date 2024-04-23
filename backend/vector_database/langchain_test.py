
from langchain.document_loaders import UnstructuredFileLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter

# 导入文本
loader = UnstructuredFileLoader("pdf_file/sam.pdf")
# 将文本转成 Document 对象
document = loader.load()
print(f'documents:{len(document)}')

# 初始化文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 200
)

# 切分文本
split_documents = text_splitter.split_documents(document)
print(f'documents:{split_documents}, {len(split_documents)}')
assert 1==0
# 加载 llm 模型
llm = OpenAI(model_name="text-davinci-003", max_tokens=1500)

# 创建总结链
chain = load_summarize_chain(llm, chain_type="refine", verbose=True)

# 执行总结链，（为了快速演示，只总结前5段）
chain.run(split_documents[:5])