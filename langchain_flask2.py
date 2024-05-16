from flask import Flask, request, jsonify, render_template_string
import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
import re

from deep_translator import GoogleTranslator
from langchain_community.document_loaders import YoutubeLoader


app = Flask(__name__)

# Setup Ollama Embeddings
#embeddings = OllamaEmbeddings(model='llama2:13b-chat')
#llm = ChatOllama(model_name="llama2:13b-chat", temperature=0.9)
#embeddings = OllamaEmbeddings(model='wizard-vicuna-uncensored:30b')
#llm = ChatOllama(model_name="wizard-vicuna-uncensored:30b", temperature=0.3)
#embeddings = OllamaEmbeddings(model='llama3:8b')
#llm = ChatOllama(model_name="llama3:8b", temperature=0.14)

embeddings = OllamaEmbeddings(model='llama3:8b')
llm = ChatOllama(model_name="llama3:8b", temperature=0.3)





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
        
        # Load documents for each template
        
        #doc_loader = DirectoryLoader(f'dialogs/{template_name}', glob="**/*.txt")
        #pages = doc_loader.load()
        #docs = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]).split_documents(pages)

        loader = YoutubeLoader.from_youtube_url(
                        "https://youtu.be/2BTI3KIiGHU", add_video_info=False, language=["en"],
        )
        pages = loader.load()

        print("Documents length :",  len(pages))
        # define the text splitter
        r_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200, 
            separators=["\n\n", "\n", " ", ""]
        )
        docs = r_splitter.split_documents(pages)
        print(docs)
        qdrants[template_name] = Qdrant.from_documents(docs, embeddings, location=":memory:", collection_name=f"{template_name}_documents")

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HOME_PAGE, templates=templates.keys())

@app.route('/api/generate/<template_name>', methods=['POST'])
def generate(template_name):
    if template_name not in templates:
        return jsonify({"error": "Template not found"}), 404

    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        template = PromptTemplate.from_template(templates[template_name])
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=qdrants[template_name].as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": template}
        )
        result = qa_chain.invoke({"query": prompt})
        
        # Extract source documents and result
        source_documents = result["source_documents"]
        llm_response = result["result"]
        
        # Create a new document containing the LLM's response
        new_document = Document(page_content=llm_response, metadata={"source": "llm"})
        
        # Add the new document to the corresponding Qdrant database
        qdrants[template_name].add_documents([new_document])
        
        # Translate the response
        translated = GoogleTranslator(source='en', target='ru').translate(llm_response)
        
        return jsonify(translated)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/edit', methods=['GET'])
def edit_select_template():
    return render_template_string(EDIT_SELECT_TEMPLATE_PAGE, templates=templates.keys())

@app.route('/edit/<template_name>', methods=['GET', 'POST'])
def edit_template(template_name):
    if not re.match(r'^[a-zA-Z0-9_\-]+$', template_name):
        return jsonify({"error": "Invalid template name"}), 400
    if template_name not in templates:
        return jsonify({"error": "Template not found"}), 404

    template_path = os.path.join(template_dir, template_name + '.md')

    if request.method == 'POST':
        content = request.form['content']
        with open(template_path, 'w') as file:
            file.write(content)
        templates[template_name] = content  # Update the template in memory
        return jsonify({"message": "Template updated successfully"})

    # For GET request, load the current content of the template
    with open(template_path, 'r') as file:
        content = file.read()
    return render_template_string(EDIT_TEMPLATE_FORM, template_name=template_name, content=content)

HOME_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Query Generator</title>
    <style>
    body { font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background-color: #f0f2f5; }
    h1 { color: #333; margin-bottom: 20px; }
    ul { list-style-type: none; padding: 0; }
    li { margin-bottom: 10px; }
    a { color: #0056b3; text-decoration: none; }
    a:hover { text-decoration: underline; }
    form { max-width: 600px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; border: 1px solid #ccc; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    label, input, button { display: block; width: 100%; box-sizing: border-box; }
    label { margin-bottom: 10px; }
    input[type="text"] {
        padding: 10px; /* Adequate padding for comfort */
        margin-bottom: 20px; /* Separate from the next element */
        border: 1px solid #ccc; /* Subtle border styling */
        border-radius: 4px; /* Rounded corners for a modern look */
    }
    button { background-color: #0056b3; color: white; padding: 10px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
    button:hover { background-color: #003d7a; }
    #response { background: white; padding: 10px; margin-top: 20px; border-radius: 8px; border: 1px solid #ccc; font-family: monospace; }
    .loading { font-style: italic; }
    </style>
</head>
<body>
    <h1>Query Generator</h1>
    <ul>
        {% for template in templates %}
        <li><a href="/edit/{{ template }}">{{ template }}</a> - <a href="#" onclick="loadForm('{{ template }}'); return false;">Use Template</a></li>
        {% endfor %}
    </ul>
    <form id="queryForm" style="display:none;">
        <label for="prompt">Enter your prompt:</label>
        <input type="text" id="prompt" name="prompt" required>
        <input type="hidden" id="template" name="template">
        <button type="button" onclick="submitForm()">Send</button>
    </form>
    <div id="response"><b>Response will appear here</b></div>

    <script>
        function loadForm(templateName) {
            document.getElementById('template').value = templateName;
            document.getElementById('queryForm').style.display = 'block';
            document.getElementById('prompt').focus();
        }

        function submitForm() {
            var prompt = document.getElementById('prompt').value;
            var template = document.getElementById('template').value;
            var submitButton = document.querySelector('button');
            var responseDiv = document.getElementById('response');

            // Disable the button and show loading text
            submitButton.disabled = true;
            responseDiv.innerHTML = '<span class="loading">Loading...</span>';

            fetch('/api/generate/' + template, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt })
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Server returned ' + response.status + ': ' + response.statusText);
                }
            })
            .then(data => {
                responseDiv.textContent = JSON.stringify(data, null, 2);
                submitButton.disabled = false; // Re-enable the button once the request is complete
            })
            .catch((error) => {
                console.error('Error:', error);
                responseDiv.textContent = 'Error: ' + error.message;
                submitButton.disabled = false; // Re-enable the button in case of an error
            });
        }
    </script>
</body>
</html>
'''

EDIT_SELECT_TEMPLATE_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Select Template to Edit</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f0f2f5; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; }
        a { color: #0056b3; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .template-link { display: block; padding: 10px; background-color: #fff; border: 1px solid #ddd; border-radius: 5px; }
        .template-link:hover { background-color: #f0f0f0; }
    </style>
</head>
<body>
    <h1>Select Template to Edit</h1>
    <ul>
        {% for template in templates %}
        <li>
            <a class="template-link" href="/edit/{{ template }}">
                {{ template }}
            </a>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
'''

EDIT_TEMPLATE_FORM = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Template: {{ template_name }}</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; color: #333; }
        h1 { background-color: #0056b3; color: #fff; padding: 20px; margin: 0; }
        form { max-width: 800px; margin: 20px auto; padding: 20px; background: #fff; border: 1px solid #ddd; border-radius: 5px; }
        textarea { width: calc(100% - 12px); padding: 5px; border-radius: 4px; border: 1px solid #ccc; height: 400px; }
        button { background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #218838; }
        a { display: inline-block; margin-top: 20px; color: #0056b3; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Edit Template: {{ template_name }}</h1>
    <form method="post">
        <textarea name="content" autofocus>{{ content }}</textarea><br>
        <button type="submit">Save Changes</button>
    </form>
    <div style="text-align: center;">
        <a href="/">Back to Home</a>
    </div>
</body>
</html>
'''


if __name__ == '__main__':
    app.run(port=7888, host='192.168.243.3')
