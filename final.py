# import 
from os import write
import re
import random
from change_sentence import *
from query_data import *
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import JSONLoader
from langchain.globals import set_verbose
import sys
from langchain.schema.output_parser import StrOutputParser
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores.faiss import FAISS
import pypandoc
import io
root_path = sys.argv[1]
set_verbose(True)
# 写作


def get_thanks(content):
    thanks = """论文致谢:
    这篇论文的完成得到了许多人的帮助与支持。我首先要向我的指导老师表示最深的感激，感谢您的无私奉献和精心指导。同时，我也要感谢那些与我并肩奋斗的同学，你们的友情与支持是我前进的力量。最重要的，我要感谢我的父母，你们是我永远的坚强后盾。每当想到大学生活，我都会感慨万千。"""
    chain = get_chain('thanks')
    rt =  chain.invoke({"text": content, "thanks": thanks})
    rt = rt.replace("首先，", "").replace("其次，", "").replace("最后，", "").replace("再者 ，","").replace("再次 ，","")
    return rt 


def get_reference(content):
    import re
    pattern = re.compile(r'\[\d+\].*?(?=\n|$)')
    matches = pattern.findall(content)
    rt = '\n'.join(matches)
    return rt

def to_docx(filename):

# Read the Markdown file with UTF-8 encoding
    input_md = filename
    output_docx = input_md.replace('.md', '.docx')

    with io.open(input_md, 'r', encoding='utf-8') as md_file:
        md_content = md_file.read()

    # Convert the markdown content to docx
    pypandoc.convert_text(md_content, 'docx', format='md', outputfile=output_docx)
    print(f"Converted '{input_md}' to '{output_docx}' with Chinese content.")

def get_jsondb():
    print("first json")
    filename = "out/" + root_path + ".json"
    loader = JSONLoader(
        file_path=filename,
        jq_schema='.[].answer',
    )
    docs = loader.load()

    embedding = HuggingFaceInstructEmbeddings(
        model_name="../models/stella-large-zh-v2"
    )
    db = FAISS.from_documents(docs, embedding)
    print("Vectorestore created successful")
    return db

def write_main(question, db):
    print("Begin writing")
    _template = """
    <信息>{context}</信息>
    根据上面的信息, 写出{question}相关的内容, 只写一个段落, 作为论文的一部份.要具体的分析,有相关的作者,文献,数据就要提出来详细说明.
    请用一种连贯的叙述方式来阐述你的观点和论据。用丰富的词汇和多样的句式来表达你的观点,让你的回答更具可读性.句式和结构必须多变, 语句和词汇必须丰富.
    """

    retriever = db.as_retriever(search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.15})

    info = retriever.get_relevant_documents(query=question)
    content='\n'.join([i.page_content for i in info])
    prompt = PromptTemplate.from_template(_template)
    llm = get_llm('local')
    chain = prompt | llm | StrOutputParser()
    rt = chain.invoke({"context": content, "question": question})
    print(f"The first content is {rt}")
    return rt


def extend_content(question, content):
    print("Begin extending")
    llm = get_llm('local', temperature=0.3)
    temp = """
    原文:
    {text}

    对原文扩写, 作为{question}研究中的一部份"""
    write_prompt = PromptTemplate.from_template(temp)
    write_chain = write_prompt | llm | StrOutputParser()
    rt = write_chain.invoke({"text":content, "question": question})
    rt = rt.replace("首先，", "").replace("其次，", "").replace("最后，", "").replace("再者 ，","").replace("再次 ，","")
    pattern = r"（[^）]*）"
    rt = re.sub(pattern, "", rt)

    print(f"The second content is {rt}")
    return rt

if __name__ == "__main__":
    input_file="input/" + sys.argv[1] + "_catalog.md"
    with open(input_file, "r", encoding="utf-8") as f:
        catalog_dict = generate_statements(f.read())
    final_file_path = "final/"+ sys.argv[1] + "_final.md"
    final_file = open(final_file_path, "w", encoding="utf-8")
    db = get_jsondb()
    for key, value in catalog_dict.items():
        final_file.write(key + "\n")
        if value:
            question = get_chain('sentence_change', llm_name='openai').invoke({"question": value})
            print(f"The quesiont is {question}")
            draft_text = write_main(question, db)
            result = extend_content(question, draft_text)
            final_file.write(result + "\n\n")
    final_file.close()
    with open(final_file_path, "a+", encoding="utf-8") as f:
        f.seek(0)
        content = f.read()
        refs = get_reference(content=content)
        ref_text = "\n参考文献\n\n" + refs + "\n"
        f.write(ref_text) 
        thanks = get_thanks(content[0:2000])
        text = "\n## 致谢\n\n" + thanks + "\n"
        f.write(text)
    to_docx(final_file_path)