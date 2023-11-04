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
            statement = f"{current_main_title}中,{line.strip('# ').strip()}"
            # 将陈述句添加到结果字典中
            result_dict[line] = statement
    return result_dict

if __name__ == '__main__':
    with open("input/mh_src_catalog.md", "r") as f:
        rt = generate_statements(f.read())
        for k,v in rt.items():
            print(k,"--",v)