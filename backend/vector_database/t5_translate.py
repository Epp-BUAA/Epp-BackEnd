import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration



def save_model(model, tokenizer, save_directory):
    """
    保存模型和分词器到指定的目录

    参数:
    - model: 训练或加载的模型实例
    - tokenizer: 使用的分词器实例
    - save_directory: 模型和分词器保存的目录路径
    """
    save_directory = "./t5_base"
    tokenizer = T5Tokenizer.from_pretrained('t5_base')
    model = T5ForConditionalGeneration.from_pretrained('t5_base')

    # 保存模型
    model.save_pretrained(save_directory)
    # 保存分词器
    tokenizer.save_pretrained(save_directory)


def translate_zh_to_en(text):
    # 初始化模型和分词器
    model_name = "./t5_base"  # 请根据需要选择适合的模型
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # 对中文文本进行预处理，添加适当的前缀
    input_text = "translate Chinese to English: " + text

    # 使用分词器编码文本
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    print(inputs["input_ids"])
    translated_text = tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)
    print(translated_text)
    # 生成翻译结果
    outputs = model.generate(inputs["input_ids"], max_length=200, num_beams=5, early_stopping=True)
    print(outputs)
    # 将生成的 token IDs 解码为翻译文本
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text


# 使用示例
text = "Hello world"
translated = translate_zh_to_en(text)
print("Translated Text:", translated)

