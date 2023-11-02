from query_data import *
from langchain.chains import ConversationChain
from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
import json

# Initialize the LLM
llm = get_llm("glm")

template_paper = """
材料：{context}
根据上面的材料，写一个{name}关于{question}的段落，作为论文的一部份。
"""

prompt = PromptTemplate.from_template(template_paper)
chain = LLMChain(
    llm=llm, 
    prompt=prompt
)

name = "爱奇艺营销模式"

ques_list = ["意义","问题"]
data = None
with open('out/aqy_src.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
for question in ques_list:
    all_context = ""
    for item in data:
        if question in item["question"]:
            context = item["answer"]
            all_context += context 
    print(all_context + "\n")
    print(f"关于{name}的{question}的答案是：")
    result = chain.predict(context=context, question=item["question"], name=name)
print(result)