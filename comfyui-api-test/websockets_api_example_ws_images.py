#This is an example that uses the websockets api and the SaveImageWebsocket node to get images directly without
#them being saved to disk

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse

#server_address = "192.168.243.3:8188"
server_address = "sdapi-1.detdom.work:443"
client_id = str(uuid.uuid4())

def queue_prompt(prompt, client_id=str(uuid.uuid4()), server_address="sdapi-1.detdom.work:443", ):
    p = {"prompt": prompt, "client_id": client_id}
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("https://{}/prompt".format(server_address), data=data, headers=headers)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("https://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("https://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    current_node = ""
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break #Execution is done
                    else:
                        current_node = data['node']
        else:
            if current_node == 'save_image_websocket_node':
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:])
                output_images[current_node] = images_output

    return output_images

with open('workflow_api_SabrinaCyberpunk.json') as f:
  prompt = json.load(f)

# POSITIVE PROMPTS
print(prompt["19"]["inputs"]["prompt"])
print(prompt["21"]["inputs"]["prompt"])
# NEGATIVE PROMPTS
print(prompt["22"]["inputs"]["prompt"])

#set the seed for our KSampler node
prompt["129"]["inputs"]["value"] = 129
print(prompt["129"]["inputs"]["value"])

ws = websocket.WebSocket()
ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
images = get_images(ws, prompt)

#Commented out code to display the output images:

for node_id in images:
    print("Node id : ", node_id)
#     for image_data in images[node_id]:
#         from PIL import Image
#         import io
#         image = Image.open(io.BytesIO(image_data))
#         image.show()

