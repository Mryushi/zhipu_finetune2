import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from prompt_template import q_system_template_text, user_template_text, a_system_template_text
from clean import questions_clean, answer_clean


# 定义一个函数来处理单个问题
def process_question(question, content, a_chain, lock, qa_file, jsonl_file, error_file):
    try:
        a_result = a_chain.invoke({"content": content, "text": question})
        json_data = answer_clean(a_result.content, question)
        with lock:
            qa_file.write(f"{question}\n{a_result.content}\n\n")
            jsonl_file.write(json_data + '\n')
    except Exception as e:
        with lock:
            error_file.write(f"Error answering question '{question}': {e}\n")


# 定义一个线程工作函数
def process_text(text, index, q_chain, a_chain, lock, qa_file, jsonl_file, error_file):
    try:
        content = text.page_content
        q_result = q_chain.invoke({"text": content})
        questions_file_path = f"questions_{index}.txt"
        with open(questions_file_path, "w", encoding="utf-8") as result_file:
            result_file.write(q_result.content)
        questions = questions_clean(questions_file_path)

        # 创建一个线程池来并行处理每个问题
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_question, question, content, a_chain, lock, qa_file, jsonl_file, error_file) for question in questions]
            for future in as_completed(futures):
                future.result()  # 这会重新抛出线程中的任何异常

    except Exception as e:
        with lock:
            error_file.write(f"General Error processing text {index}: {e}\n")


api_key = os.getenv("GLM_API_KEY")

# 模型设置
model = ChatOpenAI(
    temperature=0.95,
    model="glm-4-0520",
    openai_api_key=api_key,
    max_tokens=4000,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

# 问题提示模板
q_prompt = ChatPromptTemplate([
    ("system", q_system_template_text),
    ("user", user_template_text)
])
q_chain = q_prompt | model

# 答案提示模板
a_prompt = ChatPromptTemplate([
    ("system", a_system_template_text),
    ("user", user_template_text)
])
a_chain = a_prompt | model

# 文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=50,
    separators=["<end>"]
)

# 加载文档
loader = TextLoader("source_file.txt", encoding='utf-8')
docs = loader.load()
# 分割文档
texts = text_splitter.split_documents(docs)

# 创建一个线程锁
lock = threading.Lock()

# 打开qa.txt文件，用于追加写入
qa_file = open("qa.txt", "a", encoding="utf-8")

# 打开qa.jsonl文件，用于追加写入
jsonl_file = open("qa_view.jsonl", "a", encoding="utf-8")

# 打开错误日志文件，用于追加写入
error_file = open("errors.txt", "a", encoding="utf-8")

# 使用线程池限制线程数量
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_text, text, index, q_chain, a_chain, lock, qa_file, jsonl_file, error_file) for index, text in enumerate(texts)]

# 等待所有线程完成
for future in as_completed(futures):
    future.result()

# 关闭文件
qa_file.close()
jsonl_file.close()
error_file.close()
