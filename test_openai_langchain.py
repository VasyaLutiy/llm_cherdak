import re
from openai import OpenAI

from llama_index.core import KeywordTableIndex, SimpleDirectoryReader, GPTVectorStoreIndex, TreeIndex
#from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.utilities.dalle_image_generator import DallEAPIWrapper

from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain


import os
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


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

def extract_and_format_description(text):
    pattern = re.compile(r'\*\*Starting Location:\*\*([\s\S]*?)\*\*Possible Actions:\*\*')
    match = pattern.search(text)
    if match:
        description = match.group(1).strip()
        # Split the description into the location name and the rest of the description
        lines = description.split('\n', 1)
        if len(lines) > 1:
            location_name = lines[0].replace('**', '').strip()
            description_text = lines[1].strip()
            formatted_output = f"{location_name}:{description_text}"
        else:
            # Handle case where there's no description text, just the location name
            location_name = lines[0].replace('**', '').strip()
            formatted_output = f"{location_name}:"
        return formatted_output
    else:
        return None


def query_model(conversation, question):
    # Get OpenAI Response
    response = conversation.invoke(
        {
            "question": question
        })
    response_text = response['text']

    description = extract_and_format_description(response_text)
    print(description)
    client = OpenAI()
    response_image= client.images.generate(
        model="dall-e-3",
        prompt=description,
        size="1792x1024",
        quality="hd",
        style="vivid",
        n=1,
        )
    image_url = response_image.data[0].url
    return response_text, image_url

if __name__ == "__main__":
    conv = define_model()
    response_text, response_image = query_model(conv, "wakeup")
    #print(respond["text"])
    print(response_image)
