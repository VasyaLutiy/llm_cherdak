import json
from urllib import request, parse
import random

#This is the ComfyUI api prompt format.

#If you want it for a specific workflow you can "enable dev mode options"
#in the settings of the UI (gear beside the "Queue Size: ") this will enable
#a button on the UI to save workflows in api format.

#keep in mind ComfyUI is pre alpha software so this format will change a bit.

#this is the one for the default workflow

with open('workflow_api_SabrinaCyberpunk.json') as f:
  prompt_text = json.load(f)

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
#    req =  request.Request("https://sdapi-1.detdom.work/prompt", data=data)
    req =  request.Request("http://192.168.243.3:8188/prompt", data=data)
    request.urlopen(req)


#prompt = json.loads(prompt_text)
#prompt = prompt_text
#set the text prompt for our positive CLIPTextEncode

# POSITIVE PROMPTS
print(prompt_text["19"]["inputs"]["prompt"])
print(prompt_text["21"]["inputs"]["prompt"])
# NEGATIVE PROMPTS
print(prompt_text["22"]["inputs"]["prompt"])

#set the seed for our KSampler node
prompt_text["129"]["inputs"]["value"] = 130
print(prompt_text["129"]["inputs"]["value"])

queue_prompt(prompt_text)

