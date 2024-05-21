from llama_index.core import KeywordTableIndex, SimpleDirectoryReader, GPTVectorStoreIndex, TreeIndex
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain


import os
os.environ["OPENAI_API_KEY"] = "sk-*********************************"


# Directory for templates
template_dir = "templates_2/"

# Load templates and their associated Qdrant databases
qdrants = {}
templates = {}
for filename in os.listdir(template_dir):
    if filename.endswith(".md"):
        template_name = filename[:-3]
        print("Template :", template_name)
        with open(os.path.join(template_dir, filename), 'r') as file:
            templates[template_name] = file.read()

def define_model():
    # define LLM
    #llm = ChatOllama(model_name="llama2:13b", temperature=0.8, max_tokens=512)
    #embeddings = OllamaEmbeddings(model='llama2:13b') 

    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o", n=3)
    # Prompt
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(templates["Assistant"]),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{question}"),
        ]
    )

    # Notice that we `return_messages=True` to fit into the MessagesPlaceholder
    # Notice that `"chat_history"` aligns with the MessagesPlaceholder name
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation = LLMChain(llm=llm, prompt=prompt, verbose=False, memory=memory)
    return(conversation)

def query_model(conversation, question):
    # Get OpenAI Response
    response = conversation.invoke(
        {
            "question": question
        })
    #response_text = response['text']
    return response

if __name__ == "__main__":
    conv = define_model()
    respond = query_model(conv, "Lets start.")
    print(respond)
