import time

from ollama import Client
from typing import List, Dict
from pysyun_chain import Chainable


class OllamaProcessor:

    def init(self, uri: str, model: str):
        self.uri = uri
        self.model = model

    def process(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:

        client = Client(host=self.uri, verify=False)
        stream = client.chat(
            model=self.model,
            messages=messages,
            stream=True
        )

        results = []
        value = ''
        for chunk in stream:
            value += chunk['message']['content']

        result = {
            'time': int(time.time() * 1000),
            'value': value
        }
        results.append(result)

        return results


class Source:

    def init(self, messages):
        self.messages = messages

    def process(self, _):
        return self.messages


class Console:

    def process(self, data):
        print(data)


message_source = Chainable(Source([{
  "role": "user",
  "content": "Hi! I'm your radio-electronics developer!"
}, {
  "role": "user",
  "content": "Please, generate and Arduino sketch to send a JSON over Bluetooth."
}]))

# llama2
# wizard-vicuna-uncensored:30b
ollama_processor = Chainable(OllamaProcessor('https://api_ollama.detdom.work/api/generate', 'llama2'))

print((message_source | ollama_processor | Chainable(Console())).process([]))
