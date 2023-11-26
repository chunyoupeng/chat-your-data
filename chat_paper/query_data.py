from httpx import stream
from langchain.llms import LlamaCpp 
from langchain.schema import StrOutputParser
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.llms import ChatGLM
from langchain.chains import LLMChain
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory, ConversationBufferWindowMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.utilities.python import PythonREPL
import pickle
import sys
import os
from dotenv import load_dotenv
_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
You can assume the question about the most recent state of the union address.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

template = """You are a professional literature manager and adept writer,
capable of extracting all relevant document content based on
user responses and organizing it into a coherent paragraph.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
You can expand upon the given literature, but not excessively.
The writing style is in line with common Chinese academic writing styles.
=========
context:{context}
=========
Question: {question}
Answer must in Chinese:
Answer:"""

template_zh = """
### Instruction ###
您是一个很能写的写作助手,写的文章字数又多,文章又优美.能够根据下面<context>中的所有信息写出文章.
多引用背景材料, 对每一个例子都要有具体的分析, 避免出现总结性的语句.如果出现相关的数据,作者名,文章名,必须要全部引用出来 .不能漏掉. 
如果您不知道答案,只需说“嗯,我不确定”。不要试图编造答案。
写作风格符合常见的中文学术写作风格。要包函<context>中的所有内容.
<context>
背景: {context}
<context/>
用中文输出.1000字
"""

# 你应该针对你的问题进行针对性提问和扩展。你不能回答提出的问题, 只能分点提问,你的输出只能是问题, 输出5个问题, 用中文回答.
question_generator_template = """
Take deep and think step by step.
现在你是一个提问小助手, 你非常善于提问,但不会回答问题.你的任务是根据下面提供的问题将问题进行扩展, 制造出更多的问题,用来指导写作.只提出6个问题就可以了.要从不同的角度去提问,
因为我想得到不同观点的相关信息.
=========
你输出的是一系列的问题而不是分析.要以问号结尾.参考如下问题:
Template:
<Question>: 什么叫废物固体处理?我们可以从废物固处理得到什么?
<Output>:
    1. 废物固体处理的定义是什么，它与其他废物处理方式有何不同？
    2. 废物固体处理的历史背景和发展是怎样的？
    3. 哪些因素促使我们需要对废物固体进行处理？
    4. 废物固体处理的各个阶段包括哪些步骤？
    5. 哪些技术和方法常用于废物固体处理？
=========
Question是: {question}
<Output>:
"""

sentence_change_template = """
你的任务是把下面的陈述句改成一个有启发性的疑问句,只输出疑问句,忽略前面的数字:
陈述句:{question}
疑问句:
"""
thanks_template = """你的任务是结合文本内容和给出的论文致谢写出一个更丰富,内容更多的论文致谢部份
文本:
{text}
参考论文致谢:
{thanks}
丰富后的论文致谢:

"""

reference_template = """你现在是一个作家, 你的任务是根据用户提供的Reference中的引用写一个关于{title}的{domain}文献综述段落，
作为我论文中文献综述的一部分.要求要详尽,说明背景,并对每一篇文章进行分析.必要时可以扩展,避免出现文章名, 仅出现作者名.除了英文名字外,其余用中文输出.
"""

abstract_template = """你现在是一个论文写手, 你的任务是根据用户提供的论文的一部份, 写出关于{title}的论文摘要.包括摘要,关键词
相关论文:{content}
输出详细:
摘要:
关键词:
"""

trans_template = """
你的任务是下面的内容翻译成中文.Only output the translated version of the original text. Don't fucking talking!
要翻译的文本:{context}
"""

trans_en_template = """
你的任务是下面的内容翻译成英文. Don't fucking talking!
要翻译的文本:{context}
"""


template = """你的任务是根据用户给出的文本，提取出关键信息和逻辑流图，用python的Graphviz画出一个简单流程图，Flowchar！特别关注时间，空间，顺序等关键信息。图中的文字必须用中文，字体使用"/home/dell/.fonts/fonts/WenQuanYiMicroHei.ttf"。代码中仅仅需要将图片保存到本地, 不展示.名字是{picture_name}
尽可能的把图片设计得很美观
Return only python code in Markdown format, e.g.:

```python
....
```"""

summary_template = """对下面题目为{title}的论文写一段论文的总结部份
论文内容：
{content}
总结：
"""

GRAPH_PROMPT = ChatPromptTemplate.from_messages([("system", template), ("human", "{input}")])


QA_PROMPT = PromptTemplate(template=template_zh, input_variables=[
                           "question", "context"])
QG_PROMPT = PromptTemplate(
    template=question_generator_template, input_variables=["question"])
SENTENCE_CHANGE_PROMPT = PromptTemplate.from_template(template=sentence_change_template)
ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", template_zh),
        ("user", "{question}"),
    ]
)
THANKS_PROMPT = PromptTemplate.from_template(
    template=thanks_template
)
REFERENCE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", reference_template),
        ("user", "Reference: {reference}"),
    ]
)
ABSTRACT_PROMPT = PromptTemplate.from_template(template=abstract_template)
TRANS_PROMPT = PromptTemplate.from_template(trans_template)
TRANS_EN_PROMPT = PromptTemplate.from_template(trans_en_template)
SUMMARY_PROMPT = PromptTemplate.from_template(summary_template)
PATH = "vector_src"
OUT_PATH = "out"


def get_llm(name, temperature=0.1):


    stream = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_base="http://localhost:8001/v1",
        openai_api_key="EMPTY",
        max_tokens=8000,
        temperature=temperature,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()]
    )
    local_llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_base="http://localhost:8001/v1",
        openai_api_key="EMPTY",
        max_tokens=8000,
        temperature=temperature,
        # streaming=True,
        # callbacks=[StreamingStdOutCallbackHandler()]
    )

    openai_llm = ChatOpenAI(
        openai_api_base="https://aiapi.xing-yun.cn/v1",
        openai_api_key="sk-3e5wTBAl2iFDvQvW9b5693C90a97425eBf3b4bEa558eC66a",
        temperature=temperature,
        model_name="gpt-4",
        # streaming=True,  # ! important
        # callbacks=[StreamingStdOutCallbackHandler()]  # ! important
    )

    openai_llm_3 = ChatOpenAI(
        openai_api_base="https://aiapi.xing-yun.cn/v1",
        openai_api_key="sk-3e5wTBAl2iFDvQvW9b5693C90a97425eBf3b4bEa558eC66a",
        temperature=temperature,
        model_name="gpt-3.5-turbo",
        # streaming=True,  # ! important
        # callbacks=[StreamingStdOutCallbackHandler()]  # ! important
    )
    n_gpu_layers = -1  # Change this value based on your model and your GPU VRAM pool.
    n_batch = 256  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

    # Make sure the model path is correct for your system!
    llama = LlamaCpp(
        model_path="../models/openbuddy-zephyr-7b-v14.1.Q5_K_M.gguf",
        # n_threads=31,
        n_ctx=8000,
        max_tokens = 8000,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        # callback_manager=callback_manager,
        verbose=False,  # Verbose is required to pass to the callback manager
    )

    if name == 'local':
        return local_llm
    elif name == 'openai':
        return openai_llm
    elif name == 'openai_3':
        return openai_llm_3
    elif name == 'stream':
        return stream
    elif name == 'llama':
        return llama
    return None


def get_chain(prompt_name, llm_name='local'):

    llm = get_llm(llm_name)
    qg_chain = QG_PROMPT | llm | StrOutputParser()  # Generate question
    sentence_change_chain = SENTENCE_CHANGE_PROMPT | llm | StrOutputParser() # Generate ?
    thanks_chain = THANKS_PROMPT | llm |StrOutputParser()
    # From docs import useful information

    doc_chain = ANSWER_PROMPT | llm | StrOutputParser()
    ref_chain = REFERENCE_PROMPT | llm | StrOutputParser()
    abstract_chain = ABSTRACT_PROMPT | llm | StrOutputParser()
    trans_chain = TRANS_PROMPT | llm | StrOutputParser()
    trans_en_chain = TRANS_EN_PROMPT | llm | StrOutputParser()
    graph_chain = GRAPH_PROMPT | llm | StrOutputParser() | PythonREPL().run
    summary_chain = SUMMARY_PROMPT | llm | StrOutputParser()
    chain = None 
    if prompt_name == 'qg':
        chain = qg_chain
    elif prompt_name == 'sentence_change':
        chain = sentence_change_chain
    elif prompt_name == 'doc':
        chain = doc_chain
    elif prompt_name == 'thanks':
        chain = thanks_chain
    elif prompt_name =='ref':
        chain = ref_chain
    elif prompt_name == 'abstract':
        chain = abstract_chain
    elif prompt_name == 'trans':
        return trans_chain
    elif prompt_name == 'trans_en':
        return trans_en_chain
    elif prompt_name == 'graph':
        return graph_chain
    elif prompt_name == 'summary':
        return summary_chain
    return chain


def init():
    load_dotenv()
    if len(sys.argv) < 1:
        print("You should input the dir name for vector storage")
        sys.exit(-1)
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)


def load_db(root_path):
    to_file = 'data/' + PATH + "/" + root_path + "-vectorstore.pkl"
    with open(to_file, "rb") as f:
        db = pickle.load(f)
    return db





def get_prompt_qa_chain(llm_name):
    # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.6)
    llm = get_llm(llm_name)
    retriever = load_retriever()

    # memory = ConversationSummaryMemory(
    #     llm=llm,
    #     memory_key="chat_history",
    #     return_messages=True
    # )
    memory = ConversationBufferWindowMemory(k=3,
                                            memory_key="chat_history",
                                            return_messages=True)
    model = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        max_tokens_limit=4000,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT})
    return model
