from functools import reduce
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from query_data import get_llm
from langchain.document_loaders import PyPDFLoader
import os
import sys
import tiktoken  # !pip install tiktoken

OUT_PAPER_PATH="out_paper"

tokenizer = tiktoken.get_encoding('p50k_base')
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

llm = get_llm("glm")
trans_template = """
你的任务是下面的内容翻译成中文.Only output the translated version of the original text. Don't fucking talking!
要翻译的文本:{context}
"""
prompt_template = PromptTemplate.from_template(trans_template)
chain = LLMChain(llm=llm, prompt=prompt_template)
if not os.path.exists(OUT_PAPER_PATH):
    os.makedirs(OUT_PAPER_PATH)

def translate_document(document):
    trans_text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=2096,
        chunk_overlap=0,
        length_function=tiktoken_len,
    )
    new_docs = trans_text_splitter.split_documents(document)
    output = ""
    for d in new_docs:
        output += chain.run(d.page_content)
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
            new_filepath = os.path.join(OUT_PAPER_PATH, new_filename)
            with open(new_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            # translate document
            translated_text = translate_document(document)
            translated_filename = "zh_" + new_filename
            translated_path = os.path.join(OUT_PAPER_PATH, translated_filename)
            with open(translated_path, "w", encoding="utf-8") as f:
                f.write(translated_text)
            print(f"{filename} load successfully")

if __name__ == "__main__":
    load_paper("en_papers")