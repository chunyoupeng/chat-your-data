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
template = """Write some python code to solve the user's problem. 

Return only python code in Markdown format, e.g.:

```python
....
```"""
prompt = ChatPromptTemplate.from_messages([("system", template), ("human", "{input}")])

# model = ChatOpenAI()
llm = query_data.get_llm('openai')

def _sanitize_output(text: str):
    _, after = text.split("```python")
    return after.split("```")[0]


# chain = prompt | llm | StrOutputParser() | _sanitize_output | PythonREPL().run
chain = prompt | llm | StrOutputParser() 

out = chain.invoke({"input": "whats 2 plus 2"})

print(out)