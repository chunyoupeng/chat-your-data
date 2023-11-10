# Chat-Your-Data

Create a ChatGPT like experience over your custom docs using [LangChain](https://github.com/langchain-ai/langchain).

See [this blog post](blogpost.md) for a more detailed explanation.

## Step 0: Install requirements

`pip install -r requirements.txt`



## Step 1: Ingest your data

Run: `python ingest_data.py`

This builds `vectorstore.pkl` using OpenAI Embeddings and FAISS.

## Query data

Custom prompts are used to ground the answers in the state of the union text file.

## Running the Application

By running `python app.py` from the command line you can easily interact with your ChatGPT over your own data.

一共要传三个文件进去
文件
xx_src
目录
xx_src_catalog.md
引用
xx_src_refs.md

顺序
ingest_data.py
file_app.py
final.py