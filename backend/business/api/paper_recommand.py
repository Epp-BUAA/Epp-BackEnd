'''
用于热门文献推荐，热门文献推荐基于用户的搜索历史，点赞历史，收藏历史
'''
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# 假设我们有以下数据
num_users = 1000  # 用户数量
num_documents = 5000  # 文献数量
embedding_dim = 128  # 文献嵌入向量的维度
hidden_dim = 256  # LSTM隐藏层维度
sequence_length = 10  # 用户阅读历史的序列长度
batch_size = 32  # 批处理大小
num_epochs = 10  # 训练轮数

# 构造一个示例数据集
class LiteratureDataset(Dataset):
    def __init__(self, num_users, num_documents, sequence_length):
        self.num_users = num_users
        self.num_documents = num_documents
        self.sequence_length = sequence_length
        self.data = self.generate_data()
        
    def generate_data(self):
        data = []
        for _ in range(self.num_users):
            history = torch.randint(0, self.num_documents, (self.sequence_length,))
            target = torch.randint(0, self.num_documents, (1,))
            data.append((history, target))
        return data
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]

dataset = LiteratureDataset(num_users, num_documents, sequence_length)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# 定义模型
class LiteratureRecommendationModel(nn.Module):
    def __init__(self, num_documents, embedding_dim, hidden_dim):
        super(LiteratureRecommendationModel, self).__init__()
        self.embedding = nn.Embedding(num_documents, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_documents)
    
    def forward(self, x):
        x = self.embedding(x)
        _, (h_n, _) = self.lstm(x)
        out = self.fc(h_n[-1])
        return out

model = LiteratureRecommendationModel(num_documents, embedding_dim, hidden_dim)

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练模型
for epoch in range(num_epochs):
    for histories, targets in dataloader:
        outputs = model(histories)
        loss = criterion(outputs, targets.squeeze())
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# 测试模型
def recommend(model, user_history):
    model.eval()
    with torch.no_grad():
        output = model(user_history.unsqueeze(0))
        _, predicted = torch.max(output, 1)
        return predicted.item()

user_history = torch.randint(0, num_documents, (sequence_length,))
recommended_doc = recommend(model, user_history)
print(f'Recommended document ID: {recommended_doc}')
