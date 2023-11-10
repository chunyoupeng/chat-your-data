def generate_statements(markdown_content):
    # 将Markdown文本拆分成行
    lines = markdown_content.strip().split('\n')

    # 创建一个空字典来存储结果
    result_dict = {}

    # 存储当前遍历时的一级标题，用于附加到后面的陈述中
    current_main_title = ""

    # 遍历所有行
    for line in lines:
        # 检查标题的等级
        if line.startswith('# '):
            # 更新当前的一级标题
            current_main_title = line.strip('# ').strip()
            result_dict[line] = ""
        elif line.startswith('## '):
            result_dict[line] = ""
        elif line.startswith('### ') or line.startswith('#### '):
            # 创建陈述句
            removed_line = remove_numbers_from_headings(line)
            statement = f"{current_main_title}中,{removed_line.strip('# ').strip()}"
            # 将陈述句添加到结果字典中
            result_dict[line] = statement
    return result_dict

import re

def remove_numbers_from_headings(input_text):
    # Match one or more '#' characters followed by spaces and the number pattern
    pattern = re.compile(r'(#+ )\d+(\.\d+)* ')

    # Define a replacement function that retains the '#' characters and the following space
    def repl(matchobj):
        # Return the '#' characters and the space, omitting the numbers
        return matchobj.group(1)

    # Replace each match in the text
    output_content = pattern.sub(repl, input_text)

    return output_content


if __name__ == '__main__':
    with open("input/mh_src_catalog.md", "r") as f:
        rt = generate_statements(f.read())
        for k,v in rt.items():
            print(k,"--",v)
    
    