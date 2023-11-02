from httpx import stream
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain.prompts.prompt import PromptTemplate
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.llms import ChatGLM
from langchain.chains import LLMChain
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory, ConversationBufferWindowMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
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
Take deep and think step by step.
您是一个专业和熟练的作家,能够根据如下背景中的所有信息,回答问题, 组织成一个连贯的段落。
只能根据提供的背景材料回答. 如果您不知道答案,只需说“嗯,我不确定”。不要试图编造答案。您可以在给定的文本基础上扩展.
写作风格符合常见的中文学术写作风格。
=========
背景: {context}
=========
问题:{question}
除了人名和文献引用之外, 其它的输出必须用中文输出.
输出：
"""

question_generator_template = """
Take deep and think step by step.
您是一个专业和熟练的作家,能够根据用户的反馈提取所有相关的信息,并组织成一个连贯的段落。如果您不知道答案,只需说“嗯,我不确定”。不要试图编造答案。您可以在给定的文本基础上扩展.写作风格符合常见的中文学术写作风格。
现在你是一个提问小助手, 你非常善于提问,但不会回答问题.你的任务是根据下面提供的问题将问题进行扩展, 制造出更多的问题,用来指导写作.只提出5个问题就可以了.要从不同的角度去提问,
因为我想得到不同观点的相关信息.
=========
你输出的是一系列的问题而不是分析.要以问号结尾.参考如下问题:
Template:
Question是: 什么叫废物固体处理?我们可以从废物固处理得到什么?
你应该输出:
    1. 废物固体处理的定义是什么，它与其他废物处理方式有何不同？
    2. 废物固体处理的历史背景和发展是怎样的？
    3. 哪些因素促使我们需要对废物固体进行处理？
    4. 废物固体处理的各个阶段包括哪些步骤？
    5. 哪些技术和方法常用于废物固体处理？
上面的问题只是参考，你应该针对你的问题进行针对性提问和扩展。你不能回答提出的问题, 只能分点提问,你的输出只能是问题, 输出5个问题, 用中文回答.
=========
Question是: {question}
输出:
"""

QA_PROMPT = PromptTemplate(template=template_zh, input_variables=[
                           "question", "context"])
QG_PROMPT = PromptTemplate(
    template=question_generator_template, input_variables=["question"])

PATH = "vector_src"
OUT_PATH = "out"


def get_llm(name):
    endpoint_url = "http://127.0.0.1:8000"
    glm = ChatGLM(
        endpoint_url=endpoint_url,
        max_token=80000,
        top_p=0.3,
        model_kwargs={"sample_model_args": False},
    )
    local_llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_base="http://localhost:8000/v1",
        openai_api_key="EMPTY",
        max_tokens=8000,
        temperature=0.1,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()]
    )

    openai_llm = ChatOpenAI(
        openai_api_base="https://aiapi.xing-yun.cn/v1",
        openai_api_key="sk-3e5wTBAl2iFDvQvW9b5693C90a97425eBf3b4bEa558eC66a",
        temperature=0.1,
        model_name="gpt-4",
        streaming=True,  # ! important
        callbacks=[StreamingStdOutCallbackHandler()]  # ! important
    )
    if name == 'local':
        return local_llm
    elif name == 'openai':
        return openai_llm
    elif name == 'glm':
        return glm
    return None


def QG_chain():

    llm = get_llm('local')
    # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.6)
    llm_chain = LLMChain(prompt=QG_PROMPT, llm=llm)
    return llm_chain


def init():
    load_dotenv()
    if len(sys.argv) < 1:
        print("You should input the dir name for vector storage")
        sys.exit(-1)
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)


def load_retriever():
    to_file = PATH + "/" + sys.argv[1] + "-vectorstore.pkl"
    with open(to_file, "rb") as f:
        vectorstore = pickle.load(f)
    retriever = VectorStoreRetriever(vectorstore=vectorstore)
    return retriever





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
