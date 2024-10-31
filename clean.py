import json


def questions_clean(file_path):
    questions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 如果行是以 'Q: ' 开头，就处理它
            if line.startswith('Q:'):
                # 去除行首的 'Q: ' 和行尾的空白字符
                question = line.replace('Q:', '').strip()
                # 如果处理后的字符串非空，则添加到列表中
                if question:
                    questions.append(question)
    return questions


def answer_clean(data, question):
    # 将原始数据分割成行，并去除空行
    lines = [line.strip() for line in data.strip().split('\n') if line.strip()]
    # 构建处理后的数据结构
    processed_data = {
        "messages": [
            {"role": "system", "content": "你是智谱MaaS平台的智能客服，帮助用户解决智谱AI的相关产品问题"},
            {"role": "user", "content": question},
            {
                "role": "assistant",
                "content": "\n".join(lines)  # 将处理后的数据合并为一个字符串
            }
        ]
    }

    # 将处理后的数据转换为JSON格式
    json_data = json.dumps(processed_data, indent=2, ensure_ascii=False)
    return json_data
