from query_data import  init, get_chain, load_db
from rich.console import Console
from change_sentence import *
import json
from rich.prompt import Prompt
import sys
import os
import os
import sys
import json

def main(root_path: str) -> None:
    c = Console()
    init()
  
    question_model = "openai_3"
    main_llm = 'local'
  
    retriver = load_db(root_path).as_retriever(search_type="mmr", search_kwargs={'k': 8})
    qg_chain = get_chain('qg')
  
    c.print("[bold]Chat with your docs!")
    c.print("[bold red]---------------")
  
    OUT_JSON_PATH = f"data/out/{root_path}.json"
    if os.path.exists(OUT_JSON_PATH):
        print(f"{OUT_JSON_PATH} already exists, please delete it first")
        return
  
    out_file = open(OUT_JSON_PATH, "w")
    out_file.write("[\n")
  
    FIRST = True
  
    with open(f"data/catalog/{root_path}_catalog.md", "r") as f:
        markdown_content_with_number = f.read()
        markdown_content = remove_numbers_from_headings(markdown_content_with_number)
  
        questions = generate_statements(markdown_content)
        print(questions)
  
        for title, statement in questions.items():
            c.print(f"question is {statement}")
            if statement:
                question = get_chain('sentence_change', llm_name=question_model).invoke({"question": statement})
                new_questions = get_chain("qg", llm_name=question_model).invoke({"question": question}).split('\n')
                new_questions = [question] + new_questions
                c.print(f"==============================\nNew questions is {new_questions}")
  
                for q in new_questions:
                    c.print(q)
                    docs = retriver.get_relevant_documents(query=q)
                    content = "\n".join([doc.page_content for doc in docs])
                    doc_chain = get_chain("doc", llm_name=main_llm)
                    result = doc_chain.invoke({"context": content, "question": question})
                    c.print("[green]Answer: [/green]" + result)
  
                    if FIRST:
                        FIRST = False
                    else:
                        out_file.write(",\n")
  
                    data = {
                        "question": q,
                        "answer": result
                    }
  
                    json_str = json.dumps(data, ensure_ascii=False)
                    out_file.write(json_str)
  
                c.print("[bold red]---------------")
  
        out_file.write("]")
  
    out_file.close()

if __name__ == "__main__":
    root_path = sys.argv[1]
    main(root_path)