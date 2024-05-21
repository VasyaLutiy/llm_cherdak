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
os.environ["OPENAI_API_KEY"] = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


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
    # Обновленный шаблон для нового формата, учитывающий **Possible Actions:**
    pattern = re.compile(r'\*\*Scene Description:\*\*([\s\S]*?)(?=\*\*Possible Actions:\*\*|\Z)', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        description = match.group(1).strip()
        # Удаляем все переводы строки
        description = description.replace('\n', ' ')
        # Удаляем лишние пробелы
        description = re.sub(r'\s+', ' ', description).strip()
        return description
    return None

def extract_possible_actions(text):
    action_patterns = [
        #r'(?:\*\*Possible Actions:\*\*|### Possible Actions:|---\s*\*\*Actions:\*\*|\*\*Actions\*\*|\*\*Possible Actions\*\*)([\s\S]*?)(?:\n\n|\Z|What will Sabrina do next\?|---)'
        r'\*\*Possible Actions:\*\*([\s\S]*)'

    ]
    
    for pattern_str in action_patterns:
        pattern = re.compile(pattern_str)
        match = pattern.search(text)
        if match:
            actions_block = match.group(1).strip()
            actions = re.findall(r'\d+\.\s\*\*(.*?)\*\*', actions_block)
            if not actions:
                # В случае если нет форматирования ** **, попробуем другой вариант
                actions = re.findall(r'\d+\.\s(.*?)(?:\n|$)', actions_block)
            return actions
    return None

def query_model(conversation, question):
    # Get OpenAI Response
    response = conversation.invoke(
        {
            "question": question
        })
    response_text = response['text']
    print(response_text)

    description = extract_and_format_description(response_text)
    possible_actions = extract_possible_actions(response_text)
    print(possible_actions)

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
    return response_text, image_url, possible_actions

if __name__ == "__main__":
    conv = define_model()
    response_text, response_image, possible_actions = query_model(conv, "Examine the wildflowers and collect a few samples for future study")
    print(response_text)
    print(response_image)
    print("Scene description :")
    print(extract_and_format_description(response_text))
    print("\nPossible Actions:")
    for action in possible_actions:
        print(f"- {action}")

