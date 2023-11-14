import sys
from pathlib import Path

# Add the parent directory of src to sys.path
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))

# Now you can import your module
from chat_paper import query_data

# Rest of your test code
from chat_paper import query_data
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema.output_parser import StrOutputParser
from langchain.utilities.python import PythonREPL
template = """你的任务是根据用户给出的文本，提取出关键信息和逻辑流图，用python的Graphviz画出一个简单流程图，Flowchar！图中的文字必须用中文，字体使用"/home/dell/.fonts/fonts/WenQuanYiMicroHei.ttf"。代码中仅仅需要将图片保存到本地, 不展示.名字是{picture_name}
尽可能的把图片设计得很美观
Return only python code in Markdown format, e.g.:

```python
....
```"""

graph_template = """

"""
prompt = ChatPromptTemplate.from_messages([("system", template), ("human", "{input}")])

# model = ChatOpenAI()
llm = query_data.get_llm('openai_3')

def _sanitize_output(text: str):
    _, after = text.split("```python")
    return after.split("```")[0]


chain = prompt | llm | StrOutputParser() | _sanitize_output | PythonREPL().run

# chain = prompt | llm | StrOutputParser() 

text = """
格力电器，一家成立于1991年的领先家电制造商，自创业伊始，就以稳固并高效的线下销售渠道为发展目标，迅速确立了行业内的优势地位[2]。公司于1994年开始进一步探索线上市场，通过不懈的技术创新和卓越的市场策略，继续巩固其市场份额。到了2000年，格力实现了一个里程碑式的壮举，成功收购了美国知名家电品牌“海尔”，从而大幅提高了其国际影响力。这之后，格力进入了其国际化发展阶段，2002年在香港注册子公司，并持续拓展全球市场，至2005年，其已然成为了全球知名品牌。自2006年起，格力开始积极推进自主研发，尤其是在空调领域，成功推出了具有自主知识产权的高端产品，进一步巩固了其在全球市场的领先地位。此外，格力自2012年开始大力投资于管理信息化，将最前沿的数字化技术融入企业管理，提升了公司的整体运营效率[14]。董明珠，作为该公司的关键领导人，不仅在信息化管理方面有着卓越的贡献，更在推动公司持续创新和技术升级方面发挥了至关重要的作用。
"""
just_text = """
理解高空飞行中心理压力对飞行员心理效能的影响

- 心理压力
  - 影响飞行员情绪波动
    - 孤独、无助、紧张等负面情绪
    - 负面情绪影响心理健康和情绪稳定性
  - 导致飞行员情绪波动
    - 焦虑、恐慌等负面情绪
    - 增加心理压力，影响飞行安全与效率
  - 影响飞行员注意力和判断力
    - 高空飞行需要高度警觉性
    - 心理压力降低应对紧急情况的能力，增加飞行风险
  - 损害身心健康
    - 长期心理压力可能导致身心疲劳、失眠、抑郁等问题
    - 影响飞行效果，危及生命安全

应对心理压力的方法
- 学习放松技巧
- 进行情绪调节
- 采用认知重构

支持和帮助
- 航空公司和相关机构提供支持
- 创造良好的工作环境，保障飞行的安全和效率
"""
out = chain.invoke({"input": text, "picture_name":"1.2.3.png"})
# exec(out)
print(out)