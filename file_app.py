from query_data import chain_options, get_prompt_qa_chain, init, QG_chain
from rich.console import Console
import json
from rich.prompt import Prompt
import sys
if __name__ == "__main__":
    c = Console()
    init()
    chain = get_prompt_qa_chain('local')
    qg_chain = QG_chain()
    c.print("[bold]Chat with your docs!")
    c.print("[bold red]---------------")
    out_file = open("out/" + sys.argv[1] + ".json", "w")
    out_file.write("[\n")
    FIRST = True
    with open("input/" + "in_" + sys.argv[1], "r") as f:
        content = f.read()
        questions = content.split('\n')

        for question in questions:
            c.print("question is " + question)
            default_question = "这篇文章的主要内容是什么"
            new_question = qg_chain.run(question=question).split('\n')
            new_question = [question] + new_question
            c.print(f"==============================\nNew questions is {new_question}")
            for q in new_question:
                c.print(q)
                result = chain({"question": q}, return_only_outputs=True)
                c.print("[green]Answer: [/green]" + result['answer'])
                if FIRST:
                    FIRST = False
                else:
                    out_file.write(",\n")
                data = {
                    "question": q,
                    "answer": result["answer"]
                }
                json_str = json.dumps(data, ensure_ascii=False)
                out_file.write(json_str)
            c.print("[bold red]---------------")
        out_file.write("]")
    out_file.close()
