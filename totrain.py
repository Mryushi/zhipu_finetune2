def read_and_concatenate(input_file_path, output_file_path):
    formatted_lines = []

    with open(input_file_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

        # 每16行组成一个完整的问答单元
        for i in range(0, len(lines), 16):
            chunk = lines[i:i + 16]

            # 清除每行开头和结尾的空白，并且过滤掉空行
            cleaned_chunk = [line.strip() for line in chunk if line.strip()]

            # 将每16行的内容合并成一个字符串
            concatenated_line = ''.join(cleaned_chunk)
            formatted_lines.append(concatenated_line)

    # 写入到输出文件
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for line in formatted_lines:
            outfile.write(line + '\n')


# 定义输入输出文件路径
input_file_path = 'qa_view.jsonl'
output_file_path = 'qa_train.jsonl'

# 执行读取和格式化操作
read_and_concatenate(input_file_path, output_file_path)