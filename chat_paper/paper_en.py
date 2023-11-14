from functools import reduce
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from query_data import *
from langchain.document_loaders import PyPDFLoader
import os
import re
import sys
import tiktoken  # !pip install tiktoken

OUT_PAPER_PATH="data/out_paper"
INPUT_PAPER_PATH="data/input_paper"
if not os.path.exists(OUT_PAPER_PATH):
    os.mkdir(OUT_PAPER_PATH)
if not os.path.exists(INPUT_PAPER_PATH):
    os.mkdir(INPUT_PAPER_PATH)

tokenizer = tiktoken.get_encoding('p50k_base')
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)


def remove_unnecessary_newlines(text):
    # 正则表达式: 查找换行符，其后紧跟小写字母或某些标点
    pattern = re.compile(r'\n(?=[a-z,\.])')
    # 替换这些换行符为空字符串
    return pattern.sub(' ', text)

def translate_document(document):
    trans_text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=2096,
        chunk_overlap=0,
        length_function=tiktoken_len,
    )
    chain = get_chain("trans")
    new_docs = trans_text_splitter.split_documents(document)
    output = ""
    for d in new_docs:
        # output += chain.run(d.page_content)
        output += chain.invoke({ "context": d.page_content })
    return output

def load_paper(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            new_filename = filename.replace(".pdf", ".txt")
            print(f"Begin loading {filename}")
            filepath = os.path.join(directory, filename)
            loader = PyPDFLoader(filepath)
            document = loader.load()
            content = reduce(lambda x, y: x + y.page_content, document, "")
            replaced_content = remove_unnecessary_newlines(content)
            new_filepath = os.path.join(OUT_PAPER_PATH, new_filename)
            with open(new_filepath, "w", encoding="utf-8") as f:
                f.write(replaced_content)
            # translate document
            translated_text = translate_document(document)
            translated_filename = "zh_" + new_filename
            translated_path = os.path.join(OUT_PAPER_PATH, translated_filename)
            with open(translated_path, "w", encoding="utf-8") as f:
                f.write(translated_text)
            print(f"{filename} load successfully")

if __name__ == "__main__":
    load_paper(INPUT_PAPER_PATH)