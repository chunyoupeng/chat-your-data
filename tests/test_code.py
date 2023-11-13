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
template = """你的任务是根据用户给出的文本，提取出关键信息和逻辑，用python画出一个简单流程图，Flowchar！图中的文字必须用中文，字体使用"/home/dell/.fonts/fonts/WenQuanYiMicroHei.ttf"。代码中仅仅需要将图片保存到本地, 不展示.名字是{picture_name}

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
 在高空飞行环境中，心理压力对飞行员的心理效能产生了显著的影响。这种影响主要表现在以下几个方面：

心理压力会导致飞行员的情绪波动。在高空飞行过程中，飞行员可能会遇到孤独、无助、紧张等负面情绪。这些情绪会对飞行员的心理健康产生负面影响，使他们难以保持稳定的情绪，进而影响飞行的效果。研究表明，心理压力与飞行员的情绪波动有直接关系，且情绪波动越大，心理压力就越大。

心理压力可能导致飞行员的情绪波动。在高空飞行过程中，飞行员可能会出现焦虑、恐慌等负面情绪。这些情绪会给他们带来极大的心理压力，从而影响飞行的安全与效率。研究发现，心理压力与飞行员的情绪波动呈正相关，且情绪波动越严重，心理压力就越大。

此外，心理压力还会影响飞行员的注意力和判断力。在高空飞行过程中，飞行员需要保持高度的警觉性，以应对各种突发情况，如机械故障、恶劣天气等。然而，当飞行员承受较大的心理压力时，他们的注意力可能会受到影响，从而降低应对这些紧急情况的能力，增加飞行的风险。研究表明，心理压力与飞行员的注意力和判断力之间存在明显的关联。

心理压力可能会损害飞行员的身心健康。长期承受较大的心理压力可能会导致飞行员出现身心疲劳、失眠、抑郁等问题，这些问题不仅会影响飞行的效果，还可能危及飞行员的生命安全。

因此，对于飞行员来说，有效地应对心理压力至关重要。他们可以通过学习放松技巧、进行情绪调节、采用认知重构等方式来减轻心理压力，以提高飞行的心理效能。同时，航空公司和相关机构也应重视飞行员的心理健康，为他们提供必要的支持和帮助，创造一个良好的工作环境，以保障飞行的安全和效率。

"""
just_text = """
为了更好地理解和传达这段文本的关键信息，我们可以将其整理成一个流程图。以下是文本中提到的主要节点和逻辑关系：

1. **心理压力的影响**：
    - 导致飞行员情绪波动：孤独、无助、紧张 → 影响心理健康 → 影响飞行效果。
    - 导致飞行员情绪波动：焦虑、恐慌 → 增加心理压力 → 影响飞行安全和效率。
    - 影响飞行员的注意力和判断力 → 降低应对紧急情况的能力 → 增加飞行风险。
    - 长期影响可能导致身心健康问题：疲劳、失眠、抑郁 → 影响飞行效果和飞行员生命安全。

2. **应对措施**：
    - 飞行员个人层面：学习放松技巧、进行情绪调节、采用认知重构等。
    - 航空公司和相关机构层面：重视飞行员心理健康、提供支持和帮助、创造良好工作环境 → 提高飞行安全和效率。

这个流程图可以用来展示心理压力对飞行员心理效能的影响，以及如何通过各种措施来应对这些压力，确保飞行安全和效率。
"""
out = chain.invoke({"input": text, "picture_name":"1.2.3.png"})
# exec(out)
print(out)